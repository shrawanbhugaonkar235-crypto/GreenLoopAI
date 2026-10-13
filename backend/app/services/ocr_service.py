import os
import re
import logging
from typing import Optional, List, Tuple
from PIL import Image
import numpy as np

from app.config import settings
from app.schemas import OcrResult

logger = logging.getLogger("greenloopai.ocr")

# Registered packaging brands for EPR verification
REGISTERED_BRANDS = [
    "Coca-Cola", "Coke", "Pepsi", "PepsiCo", "Nestle", "Danone",
    "Unilever", "Procter & Gamble", "P&G", "Bisleri", "Amul",
    "Tata", "Parle", "Britannia", "ITC", "Himalayan", "Kinley",
    "Aquafina", "Sprite", "Fanta", "Limca", "Thums Up", "Maaza",
    "Frooti", "Appy", "Lays", "Kurkure", "Tropicana", "Real",
    "Red Bull", "Monster", "Mother Dairy", "Haldiram"
]

RECYCLING_CODES = {
    "pet": "PET (Type 1)",
    "pete": "PET (Type 1)",
    "hdpe": "HDPE (Type 2)",
    "pvc": "PVC (Type 3)",
    "ldpe": "LDPE (Type 4)",
    "pp": "PP (Type 5)",
    "ps": "PS (Type 6)",
    "other": "Other (Type 7)"
}

class OcrBrandService:
    def __init__(self):
        self._tesseract_available = False
        self._init_error: Optional[str] = None
        self._setup_tesseract()

    def _setup_tesseract(self):
        try:
            import pytesseract
            
            cmd = settings.TESSERACT_CMD
            if cmd and os.path.exists(cmd):
                pytesseract.pytesseract.tesseract_cmd = cmd
            
            # Test running tesseract version
            ver = pytesseract.get_tesseract_version()
            self._tesseract_available = True
            self._init_error = None
            logger.info(f"Tesseract OCR initialized successfully (version {ver})")
        except Exception as e:
            self._tesseract_available = False
            self._init_error = f"Tesseract OCR initialization failed: {e}"
            logger.warning(self._init_error)

    @property
    def is_available(self) -> bool:
        return self._tesseract_available

    @property
    def error_message(self) -> Optional[str]:
        return self._init_error

    def _detect_barcode(self, image_np: np.ndarray) -> Tuple[Optional[str], Optional[str]]:
        """Scans for 1D barcodes and 2D QR codes using OpenCV."""
        try:
            import cv2
            # 1. 1D Barcode Detection
            barcode_detector = cv2.barcode.BarcodeDetector()
            retval, decoded_info, decoded_type, _ = barcode_detector.detectAndDecode(image_np)
            if retval and decoded_info:
                valid_codes = [str(code).strip() for code in decoded_info if code and str(code).strip()]
                if valid_codes:
                    types = [str(t) for t in decoded_type if t]
                    b_type = types[0] if types else "BARCODE_1D"
                    return valid_codes[0], b_type

            # 2. QR Code Detection
            qr_detector = cv2.QRCodeDetector()
            qr_val, _, _ = qr_detector.detectAndDecode(image_np)
            if qr_val and qr_val.strip():
                return qr_val.strip(), "QR_CODE"
        except Exception as e:
            logger.debug(f"Barcode detection skipped or failed: {e}")

        return None, None

    def extract_text_and_brand(self, image: Image.Image) -> OcrResult:
        """
        Runs real Tesseract OCR on the input image to extract text, identify brands,
        and detect barcodes or material marking codes.
        """
        if not self._tesseract_available:
            raise RuntimeError(f"Tesseract OCR is not available: {self._init_error}")

        import pytesseract

        image_np = np.array(image.convert("RGB"))
        barcode, barcode_type = self._detect_barcode(image_np)

        try:
            # Extract text
            raw_text = pytesseract.image_to_string(image)
            extracted_text = " ".join(raw_text.split()).strip()

            # Estimate OCR confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confs = [float(c) for c in data.get("conf", []) if float(c) > 0]
            avg_conf = round((sum(confs) / len(confs)) / 100.0, 4) if confs else (0.75 if extracted_text else 0.0)
        except Exception as e:
            logger.error(f"Error during pytesseract extraction: {e}")
            raise RuntimeError(f"OCR execution failed: {e}")

        # Match known brands
        matched_brand = None
        lower_text = extracted_text.lower()

        for brand in REGISTERED_BRANDS:
            # Match whole word or exact token
            pattern = r"\b" + re.escape(brand.lower()) + r"\b"
            if re.search(pattern, lower_text):
                matched_brand = brand
                break

        # Check recycling material markings if no brand
        if not matched_brand:
            for code_key, code_name in RECYCLING_CODES.items():
                pattern = r"\b" + re.escape(code_key) + r"\b"
                if re.search(pattern, lower_text):
                    matched_brand = code_name
                    break

        return OcrResult(
            text=extracted_text,
            brand=matched_brand,
            confidence=avg_conf,
            barcode=barcode,
            barcode_type=barcode_type
        )

ocr_service = OcrBrandService()
