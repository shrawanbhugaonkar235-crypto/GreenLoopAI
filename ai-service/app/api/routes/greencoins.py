from typing import Optional, List
from fastapi import APIRouter, Header, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import RequireServiceAuth
from app.repositories.greencoin_repository import GreenCoinRepository

router = APIRouter(prefix="/api/v1/green-coins", tags=["GreenCoins Rewards"])


class GreenCoinTransactionItem(BaseModel):
    id: str
    user_id: Optional[str] = None
    verification_id: Optional[str] = None
    amount: int
    transaction_type: str
    reward_tier: str
    calculation_basis: Optional[str] = None
    timestamp: str


class GreenCoinsBalanceResponse(BaseModel):
    success: bool = True
    user_id: Optional[str] = None
    total_balance: int


class GreenCoinsTransactionsResponse(BaseModel):
    success: bool = True
    total: int
    skip: int
    limit: int
    transactions: List[GreenCoinTransactionItem]


@router.get("/balance", response_model=GreenCoinsBalanceResponse, dependencies=[RequireServiceAuth])
async def get_greencoins_balance(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Computes current user GreenCoin balance dynamically from transaction ledger.
    """
    target_user = user_id or x_user_id
    repo = GreenCoinRepository(db)
    balance = repo.get_user_balance(target_user)
    return GreenCoinsBalanceResponse(
        user_id=target_user,
        total_balance=balance
    )


@router.get("/transactions", response_model=GreenCoinsTransactionsResponse, dependencies=[RequireServiceAuth])
async def get_greencoins_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns transaction audit log for user rewards.
    """
    target_user = user_id or x_user_id
    repo = GreenCoinRepository(db)
    txs, total = repo.list_transactions(user_id=target_user, skip=skip, limit=limit)

    items = [
        GreenCoinTransactionItem(
            id=tx.id,
            user_id=tx.user_id,
            verification_id=tx.verification_id,
            amount=tx.amount,
            transaction_type=tx.transaction_type.value if hasattr(tx.transaction_type, "value") else str(tx.transaction_type),
            reward_tier=tx.reward_tier.value if hasattr(tx.reward_tier, "value") else str(tx.reward_tier),
            calculation_basis=tx.calculation_basis,
            timestamp=tx.timestamp.isoformat() if tx.timestamp else ""
        )
        for tx in txs
    ]

    return GreenCoinsTransactionsResponse(
        total=total,
        skip=skip,
        limit=limit,
        transactions=items
    )
