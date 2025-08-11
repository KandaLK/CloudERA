from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from .message import MessageResponse

class ChatThreadBase(BaseModel):
    name: str
    language: Optional[str] = "ENG"

class ChatThreadCreate(ChatThreadBase):
    pass

class ChatThreadUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None

class ChatThreadResponse(ChatThreadBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    last_modified: datetime
    messages: List[MessageResponse] = []
    
    model_config = {"from_attributes": True}

class ChatThreadListResponse(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    created_at: datetime
    last_modified: datetime
    language: str
    message_count: int = 0
    
    model_config = {"from_attributes": True}