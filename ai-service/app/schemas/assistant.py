from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender: user, assistant, or system")
    content: str = Field(..., max_length=2000, description="Text content of the message")


class ChatContext(BaseModel):
    page: Optional[str] = Field(None, description="Active UI page or tab")
    current_result: Optional[Dict[str, Any]] = Field(None, description="Active verified scan result if present")


class ChatRequest(BaseModel):
    message: Optional[str] = Field(None, max_length=2000, description="Single prompt message")
    messages: Optional[List[ChatMessage]] = Field(None, description="Multi-turn conversation history")
    context: Optional[ChatContext] = Field(None, description="Contextual UI state")

    @model_validator(mode="after")
    def validate_content_present(self):
        has_message = self.message and self.message.strip()
        has_messages = self.messages and len(self.messages) > 0 and any(m.content and m.content.strip() for m in self.messages)
        if not has_message and not has_messages:
            raise ValueError("Either 'message' or non-empty 'messages' list must be provided.")
        return self


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI model response")
    model: str = Field(..., description="Model identifier used for inference")
    tokens_used: Optional[int] = Field(None, description="Total tokens used if provided by provider")
    request_id: Optional[str] = Field(None, description="Correlation request ID")
