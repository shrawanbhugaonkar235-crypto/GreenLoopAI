import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

# ---------------- Auth Schemas ----------------

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the citizen")
    email: str = Field(..., min_length=5, max_length=120, description="Valid email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (at least 6 characters)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format.")
        return clean

class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=120, description="Registered email address")
    password: str = Field(..., min_length=1, description="Password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format.")
        return clean

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: Optional[str] = None

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ---------------- Verification Pipeline Schemas ----------------

class DetectedObject(BaseModel):
    label: str
    category: str
    confidence: float
    bbox: Optional[List[float]] = None

class OcrResult(BaseModel):
    text: str
    brand: Optional[str] = None
    confidence: float = 0.0
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None

class AuthenticitySignal(BaseModel):
    exif_present: bool = False
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    software: Optional[str] = None
    timestamp_valid: bool = False
    score: float = 0.5
    flags: List[str] = []

class ScoreBreakdown(BaseModel):
    detection_score: float
    brand_score: float
    authenticity_score: float
    composite_score: float

class VerificationResponse(BaseModel):
    id: str
    citizen_id: str
    file_name: str
    file_size: int
    timestamp: str
    category: Optional[str] = None
    confidence: Optional[float] = None
    ocr_text: Optional[str] = None
    brand: Optional[str] = None
    authenticity: Optional[str] = None
    score: Optional[float] = None
    coins: Optional[int] = None
    reward_tier: Optional[str] = None
    status: str
    message: Optional[str] = None
    detected_objects: List[DetectedObject] = []
    ocr: Optional[Dict[str, Any]] = None
    authenticity_detail: Optional[Dict[str, Any]] = None
    breakdown: Optional[ScoreBreakdown] = None
    calculation_basis: Optional[str] = None
    balance: Optional[int] = None

# ---------------- GreenCoins Schemas ----------------

class GreenCoinsBalanceResponse(BaseModel):
    citizen_id: str
    balance: int
    verified_count: int
    total_count: int
    latest_score: Optional[float] = None

class GreenCoinTransactionResponse(BaseModel):
    id: str
    timestamp: str
    file_name: Optional[str] = None
    description: str
    category: Optional[str] = None
    reward_tier: Optional[str] = None
    coins: int
    type: str = "reward"

# ---------------- Health Schemas ----------------

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    detection_available: bool
    ocr_available: bool
    exif_available: bool
    model: str
    version: str = "1.0.0"
    database_message: Optional[str] = None
    detection_error: Optional[str] = None
    ocr_error: Optional[str] = None
