from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid
from app.database.database import Base

class MessageAuthor(PyEnum):
    USER = "user"
    ASSISTANT = "assistant"

class ReactionType(PyEnum):
    LIKE = "like"
    DISLIKE = "dislike"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # Who created the message
    author = Column(Enum(MessageAuthor), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    reaction = Column(Enum(ReactionType), nullable=True)  # like, dislike, or null
    
    # Relationships
    thread = relationship("ChatThread", back_populates="messages")
    user = relationship("User", back_populates="messages")