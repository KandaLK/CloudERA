from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from app.models.message import MessageAuthor, ReactionType

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    thread_id: Optional[uuid.UUID] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    reaction: Optional[ReactionType] = None

class MessageResponse(MessageBase):
    id: uuid.UUID
    thread_id: uuid.UUID
    user_id: uuid.UUID
    author: MessageAuthor
    timestamp: datetime
    reaction: Optional[ReactionType] = None
    
    model_config = {"from_attributes": True}

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[uuid.UUID] = None
    language: Optional[str] = "ENG"
    use_web_search: Optional[bool] = True

class ChatResponse(BaseModel):
    message_id: uuid.UUID
    thread_id: uuid.UUID
    response: str
    created_at: datetime
    agent_metadata: Optional[Dict[str, Any]] = None

class ReactionRequest(BaseModel):
    message_id: uuid.UUID
    reaction_type: str  # Accept string values like "like" or "dislike"