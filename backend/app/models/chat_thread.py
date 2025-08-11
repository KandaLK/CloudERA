from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid
from app.database.database import Base

class ThreadType(PyEnum):
    AWS_DISCUSSION = "AWS_DISCUSSION"
    AZURE_DISCUSSION = "AZURE_DISCUSSION" 
    SMART_LEARNER = "SMART_LEARNER"

class ChatThread(Base):
    __tablename__ = "chat_threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_modified = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    language = Column(String(3), default="ENG")  # ENG or SIN
    is_permanent = Column(Boolean, default=False, nullable=False)
    thread_type = Column(Enum(ThreadType), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan", order_by="Message.timestamp")