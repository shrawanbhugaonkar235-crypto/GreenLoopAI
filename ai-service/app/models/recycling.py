import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class RecyclabilityStatusEnum(str, enum.Enum):
    RECYCLABLE = "RECYCLABLE"
    CONDITIONALLY_RECYCLABLE = "CONDITIONALLY_RECYCLABLE"
    NOT_RECYCLABLE = "NOT_RECYCLABLE"
    SPECIAL_HANDLING = "SPECIAL_HANDLING"
    UNKNOWN = "UNKNOWN"


class WarningSeverityEnum(str, enum.Enum):
    INFO = "INFO"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    DANGER = "DANGER"


class RuleTypeEnum(str, enum.Enum):
    DO = "DO"
    DO_NOT = "DO_NOT"
    SPECIAL_HANDLING = "SPECIAL_HANDLING"
    DATA_SAFETY = "DATA_SAFETY"


class RecyclingCategory(Base):
    __tablename__ = "recycling_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    recyclability_status = Column(Enum(RecyclabilityStatusEnum), default=RecyclabilityStatusEnum.RECYCLABLE, nullable=False, index=True)
    
    # Audit & Versioning
    version = Column(String(20), default="1.0.0", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    steps = relationship("RecyclingStep", back_populates="category", cascade="all, delete-orphan", order_by="RecyclingStep.step_number")
    warnings = relationship("RecyclingWarning", back_populates="category", cascade="all, delete-orphan")
    rules = relationship("RecyclingRule", back_populates="category", cascade="all, delete-orphan")
    disposal_method = relationship("RecyclingDisposalMethod", back_populates="category", uselist=False, cascade="all, delete-orphan")


class RecyclingStep(Base):
    __tablename__ = "recycling_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    category_id = Column(String(36), ForeignKey("recycling_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    step_number = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    
    category = relationship("RecyclingCategory", back_populates="steps")


class RecyclingWarning(Base):
    __tablename__ = "recycling_warnings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    category_id = Column(String(36), ForeignKey("recycling_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(WarningSeverityEnum), default=WarningSeverityEnum.CAUTION, nullable=False)
    
    category = relationship("RecyclingCategory", back_populates="warnings")


class RecyclingRule(Base):
    __tablename__ = "recycling_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    category_id = Column(String(36), ForeignKey("recycling_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rule_type = Column(Enum(RuleTypeEnum), default=RuleTypeEnum.DO, nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    
    category = relationship("RecyclingCategory", back_populates="rules")


class RecyclingDisposalMethod(Base):
    __tablename__ = "recycling_disposal_methods"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    category_id = Column(String(36), ForeignKey("recycling_categories.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    primary_route = Column(String(150), nullable=False)
    stream_name = Column(String(100), nullable=False)  # e.g., "Dry Recyclables", "Wet Organic", "E-Waste", "Hazardous"
    bin_color = Column(String(50), nullable=True)  # e.g., "Blue (Dry)", "Green (Wet)", "Red (Hazardous)"
    special_notes = Column(Text, nullable=True)
    local_guidance_notes = Column(Text, nullable=True)

    category = relationship("RecyclingCategory", back_populates="disposal_method")
