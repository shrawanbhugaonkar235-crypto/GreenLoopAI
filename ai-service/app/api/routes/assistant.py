from typing import Optional
from fastapi import APIRouter, Header, Depends
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.ai_assistant_service import ai_assistant_service
from app.api.dependencies import RequireServiceAuth

router = APIRouter(prefix="/api/v1/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse, dependencies=[RequireServiceAuth])
async def chat_with_assistant(
    request: ChatRequest,
    x_request_id: Optional[str] = Header(None, alias="X-Request-Id")
):
    """
    AI Assistant chat endpoint.
    Calls the OpenAI Responses / Chat Completion API with strict application instructions.
    Stateless, memory-safe, and does not persist chat conversations in any database.
    """
    return await ai_assistant_service.generate_response(
        message=request.message,
        messages=request.messages,
        context=request.context,
        request_id=x_request_id
    )
