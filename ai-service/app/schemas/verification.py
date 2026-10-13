from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")


class DetectedObject(BaseModel):
    label: str = Field(..., description="Object classification label")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    category: str = Field(..., description="Waste category e.g. Plastic, Paper, Metal, Glass, E-Waste")
    box: Optional[BoundingBox] = Field(None, description="Bounding box on image")


class OcrResult(BaseModel):
    text: Optional[str] = Field(None, description="Raw detected text from image")
    brand: Optional[str] = Field(None, description="Identified brand name or null if not detected")
    barcode: Optional[str] = Field(None, description="Decoded 1D/2D barcode or QR code value")
    barcode_type: Optional[str] = Field(None, description="Detected barcode symbology or format")
    confidence: Optional[float] = Field(None, description="OCR text detection confidence")
    status: str = Field(..., description="Detection status: DETECTED, NOT_DETECTED, or OCR_UNAVAILABLE")


class AuthenticitySignal(BaseModel):
    exif_present: bool = Field(..., description="Whether EXIF metadata was found")
    camera_make: Optional[str] = Field(None, description="Camera manufacturer if available")
    camera_model: Optional[str] = Field(None, description="Camera model if available")
    software: Optional[str] = Field(None, description="Software used if detected")
    timestamp_valid: bool = Field(..., description="Whether capture timestamp is physically valid")
    score: float = Field(..., description="Authenticity confidence score (0.0 to 1.0)")
    flags: List[str] = Field(default_factory=list, description="Authenticity flags or anomalies detected")


class VerificationScoreBreakdown(BaseModel):
    detection_score: float = Field(..., description="Normalized object detection score (0-100)")
    brand_score: float = Field(..., description="Normalized brand match score (0-100)")
    authenticity_score: float = Field(..., description="Normalized authenticity score (0-100)")
    composite_score: float = Field(..., description="Derived composite verification score (0-100)")


class RewardCalculation(BaseModel):
    greencoins_awarded: int = Field(..., description="Calculated reward points")
    reward_tier: str = Field(..., description="Calculated tier: BRONZE, SILVER, GOLD, PLATINUM")
    calculation_basis: str = Field(..., description="Transparent breakdown of calculation rules")


class VerificationResponse(BaseModel):
    verified: bool = Field(..., description="Overall verification outcome")
    verification_id: str = Field(..., description="Unique verification identifier")
    verification_score: float = Field(..., description="Overall calculated verification score (0-100)")
    status: str = Field(..., description="Verification status message")
    detected_objects: List[DetectedObject] = Field(default_factory=list, description="Objects detected in image")
    brand_detection: OcrResult = Field(..., description="Brand and OCR recognition details")
    authenticity: AuthenticitySignal = Field(..., description="Authenticity evaluation details")
    score_breakdown: VerificationScoreBreakdown = Field(..., description="Transparent scoring components")
    reward: RewardCalculation = Field(..., description="Calculated GreenCoins reward")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    notes: Optional[str] = Field(None, description="Additional operational notes")
