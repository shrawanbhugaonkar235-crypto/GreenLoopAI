from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.assistant import AssistantSession, AssistantMessage


class AssistantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: Optional[str] = None, title: str = "New Conversation") -> AssistantSession:
        session = AssistantSession(
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[AssistantSession]:
        return self.db.query(AssistantSession).filter(AssistantSession.id == session_id).first()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens_used: Optional[int] = None,
        model_name: Optional[str] = None
    ) -> AssistantMessage:
        msg = AssistantMessage(
            session_id=session_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
            model_name=model_name,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def list_sessions(self, user_id: Optional[str] = None, limit: int = 10) -> List[AssistantSession]:
        query = self.db.query(AssistantSession)
        if user_id:
            query = query.filter(AssistantSession.user_id == user_id)
        return query.order_by(desc(AssistantSession.updated_at)).limit(limit).all()

    def delete_session(self, session_id: str) -> bool:
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
