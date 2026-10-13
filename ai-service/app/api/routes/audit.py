from typing import Optional, List
from fastapi import APIRouter, Header, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import RequireServiceAuth
from app.repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Logs"])


class AuditLogItem(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    endpoint: str
    method: str
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    status_code: int
    details: Optional[dict] = None
    timestamp: str


class AuditLogsResponse(BaseModel):
    success: bool = True
    total: int
    skip: int
    limit: int
    logs: List[AuditLogItem]


@router.get("/logs", response_model=AuditLogsResponse, dependencies=[RequireServiceAuth])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """
    Retrieves system audit logs. Restricted to ADMIN users.
    """
    if x_user_role and x_user_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )

    repo = AuditRepository(db)
    logs, total = repo.list_logs(skip=skip, limit=limit)

    items = [
        AuditLogItem(
            id=l.id,
            user_id=l.user_id,
            action=l.action,
            endpoint=l.endpoint,
            method=l.method,
            ip_address=l.ip_address,
            request_id=l.request_id,
            status_code=l.status_code,
            details=l.details,
            timestamp=l.timestamp.isoformat() if l.timestamp else ""
        )
        for l in logs
    ]

    return AuditLogsResponse(
        total=total,
        skip=skip,
        limit=limit,
        logs=items
    )
