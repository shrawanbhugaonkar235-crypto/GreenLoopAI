import logging
from datetime import datetime, timezone
from typing import Tuple, List, Optional
from PIL import Image, ExifTags

from app.schemas.verification import AuthenticitySignal

logger = logging.getLogger("greenloopai.authenticity")

# Suspicious software tags indicating digital tampering/synthesis
SUSPICIOUS_SOFTWARE = ["photoshop", "gimp", "canva", "midjourney", "stable diffusion", "dall-e"]


class AuthenticityService:
    def verify_authenticity(self, image: Image.Image) -> AuthenticitySignal:
        """
        Extracts and evaluates image metadata for genuine physical capture markers.
        Checks for:
        1. Presence of hardware EXIF headers
        2. Camera make and model verification
        3. Editing software markers
        4. Timestamp validity against physical capture time
        """
        flags: List[str] = []
        exif_present = False
        camera_make: Optional[str] = None
        camera_model: Optional[str] = None
        software: Optional[str] = None
        timestamp_valid = False

        score = 0.50  # Base neutral score for web/mobile uploads without metadata

        try:
            exif_data = image.getexif()
            if exif_data:
                exif_present = True
                score += 0.20  # Bonus for raw metadata presence

                tag_map = {ExifTags.TAGS[k]: v for k, v in exif_data.items() if k in ExifTags.TAGS}

                camera_make = tag_map.get("Make")
                if camera_make:
                    camera_make = str(camera_make).strip()
                    score += 0.10

                camera_model = tag_map.get("Model")
                if camera_model:
                    camera_model = str(camera_model).strip()
                    score += 0.10

                software_tag = tag_map.get("Software")
                if software_tag:
                    software = str(software_tag).strip()
                    # Check for editing software
                    for susp in SUSPICIOUS_SOFTWARE:
                        if susp in software.lower():
                            flags.append(f"Edited with software: {software}")
                            score -= 0.30
                            break

                datetime_str = tag_map.get("DateTimeOriginal") or tag_map.get("DateTime")
                if datetime_str:
                    try:
                        parsed_dt = datetime.strptime(str(datetime_str)[:19], "%Y:%m:%d %H:%M:%S")
                        now = datetime.now()
                        if parsed_dt <= now:
                            timestamp_valid = True
                            score += 0.10
                        else:
                            flags.append("Future timestamp detected")
                            score -= 0.20
                    except Exception:
                        flags.append("Non-standard EXIF timestamp format")

            else:
                flags.append("No hardware EXIF metadata found (common in web-compressed images)")

        except Exception as e:
            logger.warning("Error reading image EXIF data: %s", str(e))
            flags.append(f"EXIF parsing error: {str(e)}")

        # Constrain score between 0.0 and 1.0
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
