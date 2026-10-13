from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.database import get_db, get_user_balance
from app.auth import get_current_user
from app.schemas import VerificationResponse

router = APIRouter(tags=["Verification History"])

@router.get("/api/v1/history", response_model=List[VerificationResponse])
@router.get("/api/verification/history", response_model=List[VerificationResponse])
async def get_history(
    citizen_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns verified waste scan history strictly scoped to the authenticated citizen.
    Supports filtering by status and search terms.
    """
    user_id = current_user["id"]
    db = get_db()

    query = {"user_id": user_id}
    if status_filter and status_filter.lower() != "all":
        query["status"] = status_filter.lower()

    if search and search.strip():
        term = search.strip()
        query["$or"] = [
            {"file_name": {"$regex": term, "$options": "i"}},
            {"category": {"$regex": term, "$options": "i"}},
            {"brand": {"$regex": term, "$options": "i"}}
        ]

    cursor = db.verifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit)

    results = []
    for doc in cursor:
        results.append(VerificationResponse(**doc))
    return results

@router.get("/api/v1/history/{verification_id}", response_model=VerificationResponse)
async def get_history_detail(
    verification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves full details for a specific verification attempt,
    ensuring it belongs exclusively to the authenticated citizen.
    """
    user_id = current_user["id"]
    db = get_db()

    doc = db.verifications.find_one(
        {"id": verification_id, "user_id": user_id},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification record not found."
        )

    return VerificationResponse(**doc)
