from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.greencoin import GreenCoinTransaction, TransactionTypeEnum


class GreenCoinRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_balance(self, user_id: Optional[str] = None) -> int:
        """
        Calculates user GreenCoin balance dynamically from immutable transaction records.
        """
        query = self.db.query(func.sum(GreenCoinTransaction.amount))
        if user_id:
            query = query.filter(GreenCoinTransaction.user_id == user_id)
        
        result = query.scalar()
        return int(result) if result else 0

    def list_transactions(
        self,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[GreenCoinTransaction], int]:
        query = self.db.query(GreenCoinTransaction)
        if user_id:
            query = query.filter(GreenCoinTransaction.user_id == user_id)

        total = query.count()
        transactions = query.order_by(desc(GreenCoinTransaction.timestamp)).offset(skip).limit(limit).all()
        return transactions, total
