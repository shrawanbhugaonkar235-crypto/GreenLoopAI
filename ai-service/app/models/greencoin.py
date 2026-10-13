import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransactionTypeEnum(str, enum.Enum):
    EARNED = "EARNED"
    REDEEMED = "REDEEMED"
    BONUS = "BONUS"
    ADJUSTMENT = "ADJUSTMENT"


class RewardTierEnum(str, enum.Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class GreenCoinTransaction(Base):
    __tablename__ = "greencoin_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    verification_id = Column(String(36), ForeignKey("verification_records.id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    
    amount = Column(Integer, nullable=False)
    transaction_type = Column(Enum(TransactionTypeEnum), default=TransactionTypeEnum.EARNED, nullable=False, index=True)
    reward_tier = Column(Enum(RewardTierEnum), default=RewardTierEnum.BRONZE, nullable=False)
    calculation_basis = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="greencoin_transactions")
    verification = relationship("VerificationRecord", back_populates="greencoin_transaction")
