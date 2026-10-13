from typing import Optional, List
from fastapi import APIRouter, Header, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.api.dependencies import RequireServiceAuth
from app.repositories.verification_repository import VerificationRepository
from app.models.verification import VerificationStatusEnum

router = APIRouter(prefix="/api/v1/verification", tags=["Verification History"])


class VerificationHistoryItem(BaseModel):
    id: str
    user_id: Optional[str] = None
    created_at: str
    waste_category: str
    detected_label: Optional[str] = None
    brand_name: Optional[str] = None
    barcode_value: Optional[str] = None
    detection_score: float
    brand_score: float
    authenticity_score: float
    composite_score: float
    status: str
    greencoins_awarded: int = 0
    epr_evidence_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VerificationHistoryResponse(BaseModel):
    success: bool = True
    total: int
    skip: int
    limit: int
    items: List[VerificationHistoryItem]


@router.get("/history", response_model=VerificationHistoryResponse, dependencies=[RequireServiceAuth])
async def get_verification_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    category: Optional[str] = Query(None, description="Filter by waste category"),
    status: Optional[VerificationStatusEnum] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """
    Retrieves real verification history from the database.
    Citizens view their own scans; Municipal Officers and Admins view all records.
    """
    repo = VerificationRepository(db)
    
    # Enforce role-based filter if Citizen
    filter_user_id = user_id
    if x_user_role == "CITIZEN" and x_user_id:
        filter_user_id = x_user_id

    records, total = repo.list_records(
        user_id=filter_user_id,
        category=category,
        status=status,
        skip=skip,
        limit=limit
    )

    items = []
    for r in records:
        coins = r.greencoin_transaction.amount if r.greencoin_transaction else 0
        epr_id = r.epr_record.evidence_id if r.epr_record else None
        items.append(
            VerificationHistoryItem(
                id=r.id,
                user_id=r.user_id,
                created_at=r.created_at.isoformat() if r.created_at else "",
                waste_category=r.waste_category,
                detected_label=r.detected_label,
                brand_name=r.brand_name,
                barcode_value=r.barcode_value,
                detection_score=r.detection_score,
                brand_score=r.brand_score,
                authenticity_score=r.authenticity_score,
                composite_score=r.composite_score,
                status=r.status.value if hasattr(r.status, "value") else str(r.status),
                greencoins_awarded=coins,
                epr_evidence_id=epr_id
            )
        )

    return VerificationHistoryResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items
    )


@router.get("/{verification_id}", dependencies=[RequireServiceAuth])
async def get_verification_details(
    verification_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves complete multi-signal details for a single verification record.
    """
    repo = VerificationRepository(db)
    record = repo.get_by_id(verification_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification record '{verification_id}' not found."
        )

    signals_data = [
        {
            "signal_type": s.signal_type.value if hasattr(s.signal_type, "value") else str(s.signal_type),
            "confidence": s.confidence,
            "payload": s.payload,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None
        }
        for s in record.signals
    ]

    return {
        "success": True,
        "verification_id": record.id,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "waste_category": record.waste_category,
        "detected_label": record.detected_label,
        "detection_confidence": record.detection_confidence,
        "ocr_text": record.ocr_text,
        "brand_name": record.brand_name,
        "barcode_value": record.barcode_value,
        "scores": {
            "detection": record.detection_score,
            "brand": record.brand_score,
            "authenticity": record.authenticity_score,
            "composite": record.composite_score
        },
        "status": record.status.value if hasattr(record.status, "value") else str(record.status),
        "greencoins_awarded": record.greencoin_transaction.amount if record.greencoin_transaction else 0,
        "epr_evidence_id": record.epr_record.evidence_id if record.epr_record else None,
        "signals": signals_data
    }
