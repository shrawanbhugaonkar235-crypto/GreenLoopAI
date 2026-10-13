import re
import secrets
from typing import Optional
from fastapi import Header, HTTPException, status
from app.core.config import settings


def sanitize_text_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitizes text inputs to prevent prompt injection, control characters abuse,
    and denial-of-service via oversized payloads.
    """
    if not text:
        return ""
    
    # Strip null bytes and non-printable control characters (except newline, tab, carriage return)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    cleaned = cleaned.strip()
    
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
        
    return cleaned


def verify_service_token(x_service_token: Optional[str] = Header(None, alias="X-Service-Token")) -> bool:
    """
    Validates internal service-to-service communication token between Spring Boot Gateway and FastAPI.
    If FASTAPI_SERVICE_TOKEN is configured in production, all requests must supply a valid matching token.
    In local development mode (dev-internal-secret-token or unset), allows smooth testing.
    """
    expected_token = settings.FASTAPI_SERVICE_TOKEN
    if not expected_token or expected_token == "dev-internal-secret-token":
        return True

    if not x_service_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service authentication token is missing.",
            headers={"WWW-Authenticate": "Token"}
        )

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_service_token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service authentication token."
        )

    return True
