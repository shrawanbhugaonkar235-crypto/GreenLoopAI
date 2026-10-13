import re
import logging
from typing import Optional, List, Tuple
from PIL import Image

from app.schemas.verification import OcrResult

logger = logging.getLogger("greenloopai.ocr")

# Known registered producer brands taxonomy for EPR matching
REGISTERED_BRANDS = [
    "Coca-Cola", "PepsiCo", "Nestle", "Danone", "Unilever",
    "Procter & Gamble", "Bisleri", "Amul", "Tata", "Parle",
    "Britannia", "ITC", "Himalayan", "Kinley", "Aquafina"
]


class OcrBrandService:
    def __init__(self):
        self._easyocr_reader = None
        self._tesseract_available = False
        self._init_ocr()

    def _init_ocr(self):
        # Attempt to load EasyOCR if available
        try:
            import easyocr
            self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR engine initialized.")
        except Exception:
            self._easyocr_reader = None

        # Check pytesseract availability
        try:
            import pytesseract
            self._tesseract_available = True
            logger.info("pytesseract engine available.")
        except Exception:
            self._tesseract_available = False

    def _detect_barcode(self, image_np) -> Tuple[Optional[str], Optional[str]]:
        """
        Scans image for 1D barcodes (EAN-13, UPC, Code128, etc.) and 2D QR codes using OpenCV.
        """
        try:
            import cv2
            # 1. 1D Barcode Detection (EAN-13, UPC-A, Code 128, etc.)
            barcode_detector = cv2.barcode.BarcodeDetector()
            retval, decoded_info, decoded_type, points = barcode_detector.detectAndDecode(image_np)
            if retval and decoded_info:
                valid_codes = [str(code).strip() for code in decoded_info if code and str(code).strip()]
                if valid_codes:
                    types = [str(t) for t in decoded_type if t]
                    b_type = types[0] if types else "BARCODE_1D"
                    return valid_codes[0], b_type

            # 2. 2D QR Code Detection
            qr_detector = cv2.QRCodeDetector()
            qr_val, qr_points, qr_straight = qr_detector.detectAndDecode(image_np)
            if qr_val and qr_val.strip():
                return qr_val.strip(), "QR_CODE"

        except Exception as e:
            logger.debug("Barcode detection attempt failed: %s", str(e))

        return None, None

    def extract_text_and_brand(self, image: Image.Image) -> OcrResult:
        """
        Performs OCR text recognition and Barcode / QR code identification from actual image contents.
        Never fabricates brand names or fake recognition text.
        """
        import numpy as np
        image_np = np.array(image.convert("RGB"))

        # Scan for Barcodes & QR Codes
        detected_barcode, detected_barcode_type = self._detect_barcode(image_np)

        extracted_text = ""
        avg_confidence = 0.0

        if self._easyocr_reader is not None:
            try:
                results = self._easyocr_reader.readtext(image_np)
                
                texts = []
                confidences = []
                for _, text, conf in results:
                    if text.strip():
                        texts.append(text.strip())
                        confidences.append(float(conf))
                
                if texts:
                    extracted_text = " ".join(texts)
                    avg_confidence = sum(confidences) / len(confidences)
            except Exception as e:
                logger.warning("EasyOCR execution failed: %s", str(e))

        elif self._tesseract_available:
            try:
                import pytesseract
                extracted_text = pytesseract.image_to_string(image).strip()
                avg_confidence = 0.75 if extracted_text else 0.0
            except Exception as e:
                logger.warning("Tesseract execution failed: %s", str(e))

        if not extracted_text and not detected_barcode:
            return OcrResult(
                text=None,
                brand=None,
                barcode=None,
                barcode_type=None,
                confidence=None,
                status="NOT_DETECTED"
            )

        # Match extracted text or barcode against registered producer brands
        matched_brand = None
        search_corpus = f"{extracted_text} {detected_barcode or ''}"
        for brand in REGISTERED_BRANDS:
            pattern = r"\b" + re.escape(brand) + r"\b"
            if re.search(pattern, search_corpus, re.IGNORECASE):
                matched_brand = brand
                break

        return OcrResult(
            text=extracted_text if extracted_text else (f"Barcode: {detected_barcode}" if detected_barcode else None),
            brand=matched_brand,
            barcode=detected_barcode,
            barcode_type=detected_barcode_type,
            confidence=round(avg_confidence, 4) if avg_confidence > 0 else (0.95 if detected_barcode else None),
            status="DETECTED" if (matched_brand or detected_barcode) else "NOT_DETECTED"
        )


ocr_service = OcrBrandService()
