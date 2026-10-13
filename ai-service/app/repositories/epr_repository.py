from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.epr import EprRecord, EprComplianceStatusEnum


class EprRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_evidence_id(self, evidence_id: str) -> Optional[EprRecord]:
        return self.db.query(EprRecord).filter(EprRecord.evidence_id == evidence_id).first()

    def list_records(
        self,
        brand_name: Optional[str] = None,
        status: Optional[EprComplianceStatusEnum] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[EprRecord], int]:
        query = self.db.query(EprRecord)
        if brand_name:
            query = query.filter(EprRecord.brand_name.ilike(f"%{brand_name}%"))
        if status:
            query = query.filter(EprRecord.compliance_status == status)

        total = query.count()
        records = query.order_by(desc(EprRecord.timestamp)).offset(skip).limit(limit).all()
        return records, total

    def get_summary_by_brand(self) -> List[dict]:
        """
        Aggregates EPR credits, weight, and counts by brand from real DB records.
        """
        results = (
            self.db.query(
                EprRecord.brand_name,
                func.count(EprRecord.id).label("total_items"),
                func.sum(EprRecord.weight_kg).label("total_weight_kg"),
                func.sum(EprRecord.epr_credits_generated).label("total_credits")
            )
            .group_by(EprRecord.brand_name)
            .all()
        )
        return [
            {
                "brand": r[0] or "Unbranded / Generic",
                "total_items": r[1],
                "total_weight_kg": round(float(r[2] or 0.0), 3),
                "total_credits": round(float(r[3] or 0.0), 3)
            }
            for r in results
        ]
