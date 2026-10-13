from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        action: str,
        endpoint: str,
        method: str,
        status_code: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            ip_address=ip_address,
            request_id=request_id,
            details=details,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs(self, skip: int = 0, limit: int = 50) -> Tuple[List[AuditLog], int]:
        total = self.db.query(AuditLog).count()
        logs = self.db.query(AuditLog).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        return logs, total
