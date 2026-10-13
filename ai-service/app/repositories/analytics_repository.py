from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.verification import VerificationRecord, VerificationStatusEnum
from app.models.greencoin import GreenCoinTransaction
from app.models.epr import EprRecord


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Calculates real-time platform statistics exclusively from database records.
        Returns zeros/empty structures if no records exist yet.
        """
        # 1. Total verifications
        total_scans = self.db.query(func.count(VerificationRecord.id)).scalar() or 0
        
        # 2. Verified vs Rejected
        verified_count = (
            self.db.query(func.count(VerificationRecord.id))
            .filter(VerificationRecord.status == VerificationStatusEnum.VERIFIED)
            .scalar() or 0
        )
        rejected_count = (
            self.db.query(func.count(VerificationRecord.id))
            .filter(VerificationRecord.status == VerificationStatusEnum.REJECTED)
            .scalar() or 0
        )
        
        verification_rate = round((verified_count / total_scans * 100.0), 1) if total_scans > 0 else 0.0

        # 3. Total GreenCoins Issued
        total_greencoins = (
            self.db.query(func.sum(GreenCoinTransaction.amount)).scalar() or 0
        )

        # 4. Total EPR Credits Generated & Weight
        total_epr_credits = (
            self.db.query(func.sum(EprRecord.epr_credits_generated)).scalar() or 0.0
        )
        total_weight_kg = (
            self.db.query(func.sum(EprRecord.weight_kg)).scalar() or 0.0
        )

        # 5. Waste Category Breakdown
        category_counts = (
            self.db.query(
                VerificationRecord.waste_category,
                func.count(VerificationRecord.id)
            )
            .group_by(VerificationRecord.waste_category)
            .all()
        )
        categories_dict = {cat: count for cat, count in category_counts}

        # 6. Brand Distribution
        brand_counts = (
            self.db.query(
                VerificationRecord.brand_name,
                func.count(VerificationRecord.id)
            )
            .filter(VerificationRecord.brand_name.isnot(None))
            .group_by(VerificationRecord.brand_name)
            .all()
        )
        brands_dict = {b: count for b, count in brand_counts if b}

        return {
            "total_verifications": total_scans,
            "verified_count": verified_count,
            "rejected_count": rejected_count,
            "verification_success_rate": verification_rate,
            "total_greencoins_issued": int(total_greencoins),
            "total_epr_credits": round(float(total_epr_credits), 3),
            "total_weight_diverted_kg": round(float(total_weight_kg), 3),
            "category_distribution": categories_dict,
            "brand_distribution": brands_dict,
            "has_data": total_scans > 0
        }
