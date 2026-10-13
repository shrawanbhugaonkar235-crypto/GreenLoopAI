import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class EprComplianceStatusEnum(str, enum.Enum):
    COMPLIANT = "COMPLIANT"
    PENDING_AUDIT = "PENDING_AUDIT"
    REJECTED = "REJECTED"


class EprRecord(Base):
    __tablename__ = "epr_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    verification_id = Column(String(36), ForeignKey("verification_records.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    evidence_id = Column(String(100), unique=True, nullable=False, index=True)
    
    brand_name = Column(String(150), nullable=True, index=True)
    material_type = Column(String(100), nullable=False, index=True)
    waste_category = Column(String(100), nullable=False)
    
    weight_kg = Column(Float, nullable=False, default=0.05)
    epr_credits_generated = Column(Float, nullable=False, default=0.0)
    recyclability_tier = Column(String(50), nullable=False)
    
    compliance_status = Column(Enum(EprComplianceStatusEnum), default=EprComplianceStatusEnum.COMPLIANT, nullable=False, index=True)
    regulatory_standard = Column(String(255), nullable=False)
    calculation_summary = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    verification = relationship("VerificationRecord", back_populates="epr_record")
