from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from app.core.database import get_db
from app.api.dependencies import RequireServiceAuth
from app.repositories.analytics_repository import AnalyticsRepository

router = APIRouter(prefix="/api/v1/analytics", tags=["Platform Analytics"])


class AnalyticsSummaryResponse(BaseModel):
    success: bool = True
    has_data: bool
    total_verifications: int
    verified_count: int
    rejected_count: int
    verification_success_rate: float
    total_greencoins_issued: int
    total_epr_credits: float
    total_weight_diverted_kg: float
    category_distribution: Dict[str, int]
    brand_distribution: Dict[str, int]


@router.get("/summary", response_model=AnalyticsSummaryResponse, dependencies=[RequireServiceAuth])
async def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Computes real-time platform analytics directly from relational database records.
    Never fabricates fake charts or sample metrics.
    """
    repo = AnalyticsRepository(db)
    summary = repo.get_dashboard_summary()
    return AnalyticsSummaryResponse(**summary)
