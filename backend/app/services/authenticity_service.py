import logging
from datetime import datetime
from typing import List, Optional
from PIL import Image, ExifTags

from app.schemas import AuthenticitySignal

logger = logging.getLogger("greenloopai.authenticity")

SUSPICIOUS_SOFTWARE = [
    "photoshop", "gimp", "canva", "midjourney", "stable diffusion", "dall-e",
    "lightroom", "paint.net", "snapseed", "picsart", "vsco"
]

class AuthenticityService:
    def verify_authenticity(self, image: Image.Image) -> AuthenticitySignal:
        """
        Inspects hardware and software EXIF metadata using Pillow to assess photo authenticity.
        Does not pretend EXIF alone proves authenticity, and transparently flags missing headers.
        """
        flags: List[str] = []
        exif_present = False
        camera_make: Optional[str] = None
        camera_model: Optional[str] = None
        software: Optional[str] = None
        timestamp_valid = False

        # Base neutral score for web/mobile uploads without metadata
        score = 0.50

        try:
            exif_data = image.getexif()
            if exif_data and len(exif_data) > 0:
                exif_present = True
                score += 0.20  # Bonus for hardware metadata presence

                tag_map = {ExifTags.TAGS.get(k, str(k)): v for k, v in exif_data.items()}

                if "Make" in tag_map:
                    camera_make = str(tag_map["Make"]).strip()
                    score += 0.10

                if "Model" in tag_map:
                    camera_model = str(tag_map["Model"]).strip()
                    score += 0.10

                if "Software" in tag_map:
                    software = str(tag_map["Software"]).strip()
                    for susp in SUSPICIOUS_SOFTWARE:
                        if susp in software.lower():
                            flags.append(f"Image edited with software: {software}")
                            score -= 0.30
                            break

                dt_val = tag_map.get("DateTimeOriginal") or tag_map.get("DateTime")
                if dt_val:
                    try:
                        parsed_dt = datetime.strptime(str(dt_val)[:19], "%Y:%m:%d %H:%M:%S")
                        now = datetime.now()
                        if parsed_dt <= now:
                            timestamp_valid = True
                            score += 0.10
                        else:
                            flags.append("Future capture timestamp detected")
                            score -= 0.20
                    except Exception:
                        flags.append("Non-standard EXIF timestamp format")
            else:
                flags.append("No hardware EXIF metadata found (typical for web/chat compressed images)")

        except Exception as e:
            logger.warning(f"Error parsing image EXIF: {e}")
            flags.append(f"EXIF parsing error: {str(e)}")

        # Constrain score between 0.10 and 1.00
        normalized_score = round(max(0.10, min(1.0, score)), 4)

        return AuthenticitySignal(
            exif_present=exif_present,
            camera_make=camera_make,
            camera_model=camera_model,
            software=software,
            timestamp_valid=timestamp_valid,
            score=normalized_score,
            flags=flags
        )

authenticity_service = AuthenticityService()
