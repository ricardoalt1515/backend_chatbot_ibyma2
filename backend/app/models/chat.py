# app/models/chat.py (actualizado)

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    id: Optional[str] = None
    messages: List[Message] = []
    current_step: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
