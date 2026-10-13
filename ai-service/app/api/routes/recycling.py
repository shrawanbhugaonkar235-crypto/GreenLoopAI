from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import RequireServiceAuth
from app.services.recycling_service import recycling_service
from app.repositories.verification_repository import VerificationRepository
from app.schemas.recycling import (
    RecyclingCategoriesListResponse,
    RecyclingGuideResponse,
    RecyclingRecommendationRequest
)

router = APIRouter(prefix="/api/v1/recycling", tags=["How to Recycle"])


@router.get("/categories", response_model=RecyclingCategoriesListResponse, dependencies=[RequireServiceAuth])
async def list_recycling_categories(db: Session = Depends(get_db)):
    """
    Retrieves all supported household recycling categories with metadata and recyclability statuses.
    """
    categories = recycling_service.get_categories_list(db)
    return RecyclingCategoriesListResponse(
        total=len(categories),
        categories=categories
    )


@router.get("/categories/{slug}", response_model=RecyclingGuideResponse, dependencies=[RequireServiceAuth])
async def get_recycling_guide_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Retrieves complete step-by-step recycling, safety, and disposal instructions for a category slug.
    """
    return recycling_service.get_guide_by_slug(slug, db)


@router.get("/guide/{waste_type:path}", response_model=RecyclingGuideResponse, dependencies=[RequireServiceAuth])
async def get_guide_for_waste_type(
    waste_type: str,
    confidence: Optional[float] = Query(None, description="Detection confidence score"),
    db: Session = Depends(get_db)
):
    """
    Determines and returns dynamic recycling guidance for any scanned/detected waste type.
    """
    return recycling_service.get_guide_for_waste_item(
        waste_category=waste_type,
        detected_label=waste_type,
        confidence=confidence,
        db=db
    )


@router.post("/recommendation", response_model=RecyclingGuideResponse, dependencies=[RequireServiceAuth])
async def get_recommendation_for_verification(
    request: RecyclingRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Generates tailored recycling instructions based on an active or historical verification record.
    """
    waste_cat = request.waste_category
    det_label = request.detected_label
    conf = request.confidence

    if request.verification_id:
        v_repo = VerificationRepository(db)
        record = v_repo.get_by_id(request.verification_id)
        if record:
            waste_cat = record.waste_category
            det_label = record.detected_label
            conf = record.detection_confidence

    return recycling_service.get_guide_for_waste_item(
        waste_category=waste_cat,
        detected_label=det_label,
        confidence=conf,
        db=db
    )
