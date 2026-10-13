from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.verification import VerificationRecord, VerificationSignal, VerificationStatusEnum, SignalTypeEnum
from app.models.greencoin import GreenCoinTransaction, TransactionTypeEnum, RewardTierEnum
from app.models.epr import EprRecord, EprComplianceStatusEnum


class VerificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, verification_id: str) -> Optional[VerificationRecord]:
        return self.db.query(VerificationRecord).filter(VerificationRecord.id == verification_id).first()

    def list_records(
        self,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[VerificationStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[VerificationRecord], int]:
        query = self.db.query(VerificationRecord)
        if user_id:
            query = query.filter(VerificationRecord.user_id == user_id)
        if category:
            query = query.filter(VerificationRecord.waste_category == category)
        if status:
            query = query.filter(VerificationRecord.status == status)

        total = query.count()
        records = query.order_by(desc(VerificationRecord.created_at)).offset(skip).limit(limit).all()
        return records, total

    def save_complete_verification(
        self,
        verification_id: str,
        user_id: Optional[str],
        file_name: Optional[str],
        file_size_bytes: Optional[float],
        waste_category: str,
        detected_label: Optional[str],
        detection_confidence: Optional[float],
        ocr_text: Optional[str],
        brand_name: Optional[str],
        barcode_value: Optional[str],
        authenticity_score: float,
        detection_score: float,
        brand_score: float,
        composite_score: float,
        status: VerificationStatusEnum,
        signals: List[dict],
        reward_coins: int,
        reward_tier: str,
        reward_basis: str,
        epr_evidence_id: Optional[str] = None,
        epr_credits: Optional[float] = None,
        epr_material: Optional[str] = None,
        epr_weight: Optional[float] = None,
        epr_tier: Optional[str] = None,
        epr_status: Optional[EprComplianceStatusEnum] = None,
        epr_standard: Optional[str] = None,
        epr_summary: Optional[str] = None
    ) -> VerificationRecord:
        """
        Saves verification record, audit signals, GreenCoin reward transaction,
        and EPR record atomically in a single database transaction.
        Rolls back automatically if any stage fails.
        """
        # 1. Main Verification Record
        record = VerificationRecord(
            id=verification_id,
            user_id=user_id,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
            waste_category=waste_category,
            detected_label=detected_label,
            detection_confidence=detection_confidence,
            ocr_text=ocr_text,
            brand_name=brand_name,
            barcode_value=barcode_value,
            authenticity_score=authenticity_score,
            detection_score=detection_score,
            brand_score=brand_score,
            composite_score=composite_score,
            status=status,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(record)

        # 2. Detailed Audit Signals
        for sig in signals:
            signal_entity = VerificationSignal(
                verification_id=verification_id,
                signal_type=sig.get("signal_type", SignalTypeEnum.YOLO_DETECTION),
                confidence=sig.get("confidence"),
                payload=sig.get("payload")
            )
            self.db.add(signal_entity)

        # 3. GreenCoins Transaction (if verified and coins awarded)
        if reward_coins > 0 and status == VerificationStatusEnum.VERIFIED:
            tier_enum = getattr(RewardTierEnum, reward_tier.upper(), RewardTierEnum.SILVER)
            coin_tx = GreenCoinTransaction(
                user_id=user_id,
                verification_id=verification_id,
                amount=reward_coins,
                transaction_type=TransactionTypeEnum.EARNED,
                reward_tier=tier_enum,
                calculation_basis=reward_basis,
                timestamp=datetime.now(timezone.utc)
            )
            self.db.add(coin_tx)

        # 4. EPR Compliance Record (if EPR evidence generated)
        if epr_evidence_id:
            epr_rec = EprRecord(
                verification_id=verification_id,
                evidence_id=epr_evidence_id,
                brand_name=brand_name,
                material_type=epr_material or "Recyclable",
                waste_category=waste_category,
                weight_kg=epr_weight or 0.05,
                epr_credits_generated=epr_credits or 0.0,
                recyclability_tier=epr_tier or "TIER_2_MEDIUM",
                compliance_status=epr_status or EprComplianceStatusEnum.COMPLIANT,
                regulatory_standard=epr_standard or "EPR Circularity Norms",
                calculation_summary=epr_summary,
                timestamp=datetime.now(timezone.utc)
            )
            self.db.add(epr_rec)

        # Commit all atomically
        self.db.commit()
        self.db.refresh(record)
        return record
