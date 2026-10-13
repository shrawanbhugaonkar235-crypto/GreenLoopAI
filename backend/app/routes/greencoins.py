from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.database import get_db, get_user_balance
from app.auth import get_current_user
from app.schemas import GreenCoinsBalanceResponse, GreenCoinTransactionResponse

router = APIRouter(tags=["GreenCoins"])

@router.get("/api/v1/greencoins/balance", response_model=GreenCoinsBalanceResponse)
@router.get("/api/verification/greencoins", response_model=GreenCoinsBalanceResponse)
async def get_balance(
    citizen_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the authoritative GreenCoins balance derived from trusted database transactions,
    strictly scoped to the authenticated citizen.
    """
    user_id = current_user["id"]
    db = get_db()

    balance = get_user_balance(user_id)
    verified_count = db.verifications.count_documents({"user_id": user_id, "status": "verified"})
    total_count = db.verifications.count_documents({"user_id": user_id})

    # Latest score
    latest_cursor = db.verifications.find(
        {"user_id": user_id, "score": {"$ne": None}},
        {"score": 1}
    ).sort("created_at", -1).limit(1)
    latest_list = list(latest_cursor)
    latest_score = latest_list[0]["score"] if latest_list else None

    return GreenCoinsBalanceResponse(
        citizen_id=user_id,
        balance=balance,
        verified_count=verified_count,
        total_count=total_count,
        latest_score=latest_score
    )

@router.get("/api/v1/greencoins/transactions", response_model=List[GreenCoinTransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns paginated transaction history for the authenticated citizen.
    """
    user_id = current_user["id"]
    db = get_db()

    cursor = db.greencoins_transactions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit)

    results = []
    for doc in cursor:
        results.append(
            GreenCoinTransactionResponse(
                id=doc["id"],
                timestamp=doc.get("created_at", ""),
                file_name=doc.get("file_name"),
                description=doc.get("description", "Reward"),
                category=doc.get("category"),
                reward_tier=doc.get("reward_tier"),
                coins=doc.get("amount", 0),
                type=doc.get("type", "reward")
            )
        )
    return results
