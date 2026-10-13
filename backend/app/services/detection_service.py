import os
import logging
from typing import List, Tuple, Optional
from PIL import Image

from app.config import settings
from app.schemas import DetectedObject

logger = logging.getLogger("greenloopai.detection")

# Taxonomy mapping COCO object classes to municipal waste & recyclable categories
WASTE_CATEGORY_TAXONOMY = {
    # Plastic
    "bottle": "Plastic",
    "cup": "Plastic",
    "bowl": "Plastic",
    "toothbrush": "Plastic",
    # Paper & Cardboard
    "book": "Paper / Cardboard",
    "box": "Paper / Cardboard",
    # Metal
    "can": "Metal",
    "fork": "Metal",
    "knife": "Metal",
    "spoon": "Metal",
    "scissors": "Metal",
    # Glass
    "wine glass": "Glass",
    "vase": "Glass",
    # E-Waste
    "cell phone": "E-Waste",
    "phone": "E-Waste",
    "laptop": "E-Waste",
    "mouse": "E-Waste",
    "keyboard": "E-Waste",
    "remote": "E-Waste",
    "tv": "E-Waste",
    "clock": "E-Waste",
    "toaster": "E-Waste",
    "microwave": "E-Waste",
    "oven": "E-Waste",
    "refrigerator": "E-Waste",
    # Textile / Fabric
    "backpack": "Textile / Fabric",
    "handbag": "Textile / Fabric",
    "suitcase": "Textile / Fabric",
    "umbrella": "Textile / Fabric",
    "tie": "Textile / Fabric",
    # Organic / Compost
    "banana": "Organic / Compost",
    "apple": "Organic / Compost",
    "sandwich": "Organic / Compost",
    "orange": "Organic / Compost",
    "broccoli": "Organic / Compost",
    "carrot": "Organic / Compost",
    "hot dog": "Organic / Compost",
    "pizza": "Organic / Compost",
    "donut": "Organic / Compost",
    "cake": "Organic / Compost",
    "potted plant": "Organic / Compost"
}

class WasteDetectionService:
    def __init__(self):
        self._model = None
        self._model_loaded = False
        self._init_error: Optional[str] = None
        self._initialize_model()

    def _initialize_model(self):
        model_path = settings.resolved_yolo_path
        if not os.path.exists(model_path):
            self._init_error = f"Model file not found at {model_path}"
            logger.warning(self._init_error)
            self._model_loaded = False
            return

        try:
            from ultralytics import YOLO
            self._model = YOLO(model_path)
            self._model_loaded = True
            self._init_error = None
            logger.info(f"YOLO model successfully loaded from {model_path}")
        except Exception as e:
            self._init_error = str(e)
            self._model_loaded = False
            logger.error(f"Failed to load YOLO model: {e}")

    @property
    def is_available(self) -> bool:
        return self._model_loaded

    @property
    def error_message(self) -> Optional[str]:
        return self._init_error

    def detect_objects(self, image: Image.Image) -> Tuple[List[DetectedObject], Optional[str], Optional[float]]:
        """
        Runs real YOLO inference on the input image.
        Returns:
            - detected_objects: list of DetectedObject
            - primary_category: main category or None
            - avg_confidence: average confidence or None
        """
        if not self._model_loaded or self._model is None:
            raise RuntimeError(f"YOLO detection model is unavailable: {self._init_error}")

        # Run inference
        results = self._model.predict(
            source=image,
            conf=settings.YOLO_CONF,
            verbose=False
        )

        detected_objects: List[DetectedObject] = []
        if not results:
            return [], None, None

        first_res = results[0]
        names = first_res.names

        for box in first_res.boxes:
            cls_id = int(box.cls[0].item())
            raw_label = names.get(cls_id, f"object_{cls_id}").lower()
            confidence = float(box.conf[0].item())

            category = WASTE_CATEGORY_TAXONOMY.get(raw_label, "Recyclable Waste")

            xyxy = [float(v) for v in box.xyxy[0].tolist()] if box.xyxy is not None else None

            detected_objects.append(
                DetectedObject(
                    label=raw_label.capitalize(),
                    category=category,
                    confidence=round(confidence, 4),
                    bbox=xyxy
                )
            )

        if not detected_objects:
            return [], None, None

        # Determine primary category based on highest confidence
        detected_objects.sort(key=lambda x: x.confidence, reverse=True)
        primary_category = detected_objects[0].category
        avg_confidence = round(
            sum(o.confidence for o in detected_objects) / len(detected_objects),
            4
        )

        return detected_objects, primary_category, avg_confidence

detection_service = WasteDetectionService()
