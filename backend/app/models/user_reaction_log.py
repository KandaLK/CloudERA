from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid
from app.database.database import Base

class ReactionLogType(PyEnum):
    LIKE = "like"
    DISLIKE = "dislike"
    REMOVED = "removed"  # Track when reactions are removed

class UserReactionLog(Base):
    """
    Permanent log of all user reactions with complete context.
    This table data must never be deleted to maintain audit trail.
    """
    __tablename__ = "user_reaction_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user_name = Column(String(50), nullable=False)  # Denormalized for reporting
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False, index=True)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=False, index=True)
    
    # Content for context (denormalized for permanent storage)
    question_content = Column(Text, nullable=True)  # User's question that led to this response
    response_content = Column(Text, nullable=False)  # Assistant's response being reacted to
    
    # Reaction details
    reaction_type = Column(Enum(ReactionLogType), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Optional metadata
    session_info = Column(JSON, nullable=True)  # Can store additional context like language, thread_type, etc.
    
    # Relationships for reference (but data is denormalized for permanence)
    user = relationship("User")
    message = relationship("Message")
    thread = relationship("ChatThread")

    def __repr__(self):
        return f"<UserReactionLog(user={self.user_name}, reaction={self.reaction_type}, timestamp={self.timestamp})>"