import io
from typing import Tuple
from PIL import Image
from fastapi import HTTPException, status
from app.core.config import settings


# Magic number byte signatures
MAGIC_NUMBERS = {
    b"\xFF\xD8\xFF": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WebP begins with RIFF....WEBP
}


def validate_image_file(file_bytes: bytes, filename: str) -> Tuple[Image.Image, str]:
    """
    Validates uploaded image bytes against:
    1. Maximum file size limits
    2. File magic bytes (preventing spoofed mime-types/extensions)
    3. Structural decoding with Pillow
    4. Image dimension sanity limits
    """
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    if len(file_bytes) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded image exceeds the maximum permitted size of {max_mb} MB."
        )

    # Check magic numbers
    detected_mime = None
    if file_bytes.startswith(b"\xFF\xD8\xFF"):
        detected_mime = "image/jpeg"
    elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        detected_mime = "image/png"
    elif file_bytes.startswith(b"RIFF") and len(file_bytes) > 12 and file_bytes[8:12] == b"WEBP":
        detected_mime = "image/webp"

    if not detected_mime or detected_mime not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported or invalid image format. Supported formats: JPEG, PNG, WebP."
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verify structural integrity
        # Re-open because verify() closes/invalidates the stream in PIL
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image file is corrupted or could not be decoded: {str(e)}"
        )

    # Limit image dimensions (prevent decompression bomb attacks)
    width, height = image.size
    if width > 8192 or height > 8192:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image dimensions ({width}x{height}) exceed maximum allowed dimension (8192x8192)."
        )

    return image, detected_mime
