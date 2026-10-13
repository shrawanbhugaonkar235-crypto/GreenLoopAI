from typing import Optional, List
from fastapi import APIRouter, Header, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.schemas.epr import EprProcessingRequest, EprProcessingResponse
from app.services.epr_service import epr_service
from app.api.dependencies import RequireServiceAuth
from app.core.database import get_db
from app.repositories.epr_repository import EprRepository
from app.models.epr import EprComplianceStatusEnum

router = APIRouter(prefix="/api/v1/epr", tags=["EPR Compliance"])


class EprRecordItem(BaseModel):
    id: str
    verification_id: str
    evidence_id: str
    brand_name: Optional[str] = None
    material_type: str
    waste_category: str
    weight_kg: float
    epr_credits_generated: float
    recyclability_tier: str
    compliance_status: str
    regulatory_standard: str
    calculation_summary: Optional[str] = None
    timestamp: str


class EprRecordsResponse(BaseModel):
    success: bool = True
    total: int
    skip: int
    limit: int
    records: List[EprRecordItem]


@router.post("/process", response_model=EprProcessingResponse, dependencies=[RequireServiceAuth])
async def process_epr(
    request: EprProcessingRequest,
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id")
):
    """
    Computes EPR compliance credits and regulatory evidence string for verified waste items.
    """
    return epr_service.process_compliance_record(request)


@router.get("/records", response_model=EprRecordsResponse, dependencies=[RequireServiceAuth])
async def list_epr_records(
    brand: Optional[str] = Query(None),
    status: Optional[EprComplianceStatusEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns verified EPR compliance records from the database for producer auditing.
    """
    repo = EprRepository(db)
    records, total = repo.list_records(brand_name=brand, status=status, skip=skip, limit=limit)

    items = [
        EprRecordItem(
            id=r.id,
            verification_id=r.verification_id,
            evidence_id=r.evidence_id,
            brand_name=r.brand_name,
            material_type=r.material_type,
            waste_category=r.waste_category,
            weight_kg=r.weight_kg,
            epr_credits_generated=r.epr_credits_generated,
            recyclability_tier=r.recyclability_tier,
            compliance_status=r.compliance_status.value if hasattr(r.compliance_status, "value") else str(r.compliance_status),
            regulatory_standard=r.regulatory_standard,
            calculation_summary=r.calculation_summary,
            timestamp=r.timestamp.isoformat() if r.timestamp else ""
        )
        for r in records
    ]

    return EprRecordsResponse(
        total=total,
        skip=skip,
        limit=limit,
        records=items
    )


@router.get("/summary", dependencies=[RequireServiceAuth])
async def get_epr_brand_summary(db: Session = Depends(get_db)):
    """
    Aggregates EPR credits, weight, and counts by brand from real DB records.
    """
    repo = EprRepository(db)
    summary = repo.get_summary_by_brand()
    return {
        "success": True,
        "brands_count": len(summary),
        "data": summary
    }
