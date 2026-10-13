import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class VerificationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class SignalTypeEnum(str, enum.Enum):
    YOLO_DETECTION = "YOLO_DETECTION"
    OCR_BRAND = "OCR_BRAND"
    BARCODE = "BARCODE"
    AUTHENTICITY = "AUTHENTICITY"
    SCORE_BREAKDOWN = "SCORE_BREAKDOWN"


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    image_hash = Column(String(64), nullable=True, index=True)
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Float, nullable=True)
    
    waste_category = Column(String(100), nullable=False, index=True)
    detected_label = Column(String(100), nullable=True)
    detection_confidence = Column(Float, nullable=True)
    
    ocr_text = Column(Text, nullable=True)
    brand_name = Column(String(150), nullable=True, index=True)
    barcode_value = Column(String(100), nullable=True)
    
    authenticity_score = Column(Float, nullable=False, default=0.0)
    detection_score = Column(Float, nullable=False, default=0.0)
    brand_score = Column(Float, nullable=False, default=0.0)
    composite_score = Column(Float, nullable=False, default=0.0)
    
    status = Column(Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="verifications")
    signals = relationship("VerificationSignal", back_populates="verification", cascade="all, delete-orphan")
    greencoin_transaction = relationship("GreenCoinTransaction", back_populates="verification", uselist=False, cascade="all, delete-orphan")
    epr_record = relationship("EprRecord", back_populates="verification", uselist=False, cascade="all, delete-orphan")


class VerificationSignal(Base):
    __tablename__ = "verification_signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    verification_id = Column(String(36), ForeignKey("verification_records.id", ondelete="CASCADE"), nullable=False, index=True)
    
    signal_type = Column(Enum(SignalTypeEnum), nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    verification = relationship("VerificationRecord", back_populates="signals")
