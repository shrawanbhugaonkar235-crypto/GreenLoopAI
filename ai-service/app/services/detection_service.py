import os
import logging
from typing import List, Tuple
from PIL import Image
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.verification import DetectedObject, BoundingBox

logger = logging.getLogger("greenloopai.detection")

# Waste category taxonomy mapping for all standard recyclable and material classes
WASTE_CATEGORY_TAXONOMY = {
    # Paper & Cardboard
    "paper": "Paper / Cardboard",
    "cardboard": "Paper / Cardboard",
    "box": "Paper / Cardboard",
    "book": "Paper / Cardboard",
    # Plastic
    "bottle": "Plastic",
    "cup": "Plastic",
    "container": "Plastic",
    "bag": "Plastic",
    "bowl": "Plastic",
    # Metal
    "can": "Metal",
    "fork": "Metal",
    "knife": "Metal",
    "spoon": "Metal",
    "scissors": "Metal",
    # Glass
    "glass": "Glass",
    "wine glass": "Glass",
    "vase": "Glass",
    # E-Waste
    "electronic": "E-Waste",
    "phone": "E-Waste",
    "cell phone": "E-Waste",
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
    # Textile & Fabric
    "backpack": "Textile / Fabric",
    "handbag": "Textile / Fabric",
    "suitcase": "Textile / Fabric",
    "umbrella": "Textile / Fabric",
    "tie": "Textile / Fabric",
    # Wood & Bulky
    "chair": "Wood / Bulky",
    "couch": "Furniture",
    "bed": "Furniture",
    "dining table": "Wood / Bulky",
    "bench": "Wood / Bulky",
    # Organic / Compostable
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
        self._initialize_model()

    def _initialize_model(self):
        model_path = settings.YOLO_MODEL_PATH
        if not model_path:
            logger.info("YOLO model path not configured.")
            self._model_loaded = False
            return

        resolved_path = None
        if os.path.exists(model_path):
            resolved_path = model_path
        else:
            # Check candidate paths relative to service root and workspace root
            service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            candidates = [
                os.path.join(service_root, model_path),
                os.path.join(service_root, "models", "yolov8n.pt"),
                os.path.join("ai-service", model_path),
                os.path.join("ai-service", "models", "yolov8n.pt"),
                os.path.abspath(os.path.join("models", "yolov8n.pt"))
            ]
            for c in candidates:
                if os.path.exists(c):
                    resolved_path = c
                    break

        if not resolved_path or not os.path.exists(resolved_path):
            logger.info("YOLO model path (%s) not found.", model_path)
            self._model = None
            self._model_loaded = False
            return

        try:
            # Dynamically import ultralytics if available in environment
            from ultralytics import YOLO
            self._model = YOLO(resolved_path)
            self._model_loaded = True
            logger.info("YOLO model successfully loaded from: %s", resolved_path)
        except ImportError:
            logger.warning("ultralytics library is not installed in the environment.")
            self._model = None
            self._model_loaded = False
        except Exception as e:
            logger.error("Failed to load YOLO model from %s: %s", resolved_path, str(e))
            self._model = None
            self._model_loaded = False

    def is_available(self) -> bool:
        if not self._model_loaded:
            # Retry initializing in case environment variable or file changed
            self._initialize_model()
        return self._model_loaded

    def detect_waste(self, image: Image.Image) -> List[DetectedObject]:
        """
        Executes real computer vision inference on the supplied image.
        Fails cleanly if model is not configured/available.
        Never fabricates detection results or returns fake hardcoded bounding boxes.
        """
        if not self.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI detection model unavailable"
            )

        try:
            results = self._model(image, conf=settings.YOLO_CONFIDENCE_THRESHOLD)
            detected_objects: List[DetectedObject] = []

            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    cls_name = self._model.names.get(cls_id, f"class_{cls_id}").lower()
                    confidence = float(box.conf[0].item())
                    xyxy = box.xyxy[0].tolist()

                    category = WASTE_CATEGORY_TAXONOMY.get(cls_name, "General Waste")

                    detected_objects.append(
                        DetectedObject(
                            label=cls_name.capitalize(),
                            confidence=round(confidence, 4),
                            category=category,
                            box=BoundingBox(
                                x1=round(xyxy[0], 2),
                                y1=round(xyxy[1], 2),
                                x2=round(xyxy[2], 2),
                                y2=round(xyxy[3], 2)
                            )
                        )
                    )

            return detected_objects

        except Exception as e:
            logger.error("Error during YOLO inference: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inference error: {str(e)}"
            )


detection_service = WasteDetectionService()
