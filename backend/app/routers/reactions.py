from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from app.database.database import get_db
from app.models.user import User
from app.models.message import Message, MessageAuthor, ReactionType
from app.models.user_reaction_log import UserReactionLog, ReactionLogType
from app.schemas.message import ReactionRequest
from app.core.auth import get_current_active_user

router = APIRouter()

def _extract_question_response_context(db: Session, message: Message) -> tuple[str, str]:
    """
    Extract the question (user message) and response (assistant message) pair
    for context in reaction logging.
    """
    try:
        # Get all messages in the thread ordered by timestamp
        thread_messages = db.query(Message).filter(
            Message.thread_id == message.thread_id
        ).order_by(Message.timestamp).all()
        
        # If this is an assistant message, find the preceding user message
        if message.author == MessageAuthor.ASSISTANT:
            response_content = message.content
            question_content = None
            
            # Find the most recent user message before this assistant message
            for i, msg in enumerate(thread_messages):
                if msg.id == message.id:
                    # Look backwards for the user message
                    for j in range(i-1, -1, -1):
                        if thread_messages[j].author == MessageAuthor.USER:
                            question_content = thread_messages[j].content
                            break
                    break
            
            return question_content or "No preceding question found", response_content
        
        # If this is a user message, find the following assistant message
        elif message.author == MessageAuthor.USER:
            question_content = message.content
            response_content = None
            
            # Find the next assistant message after this user message
            for i, msg in enumerate(thread_messages):
                if msg.id == message.id:
                    # Look forwards for the assistant message
                    for j in range(i+1, len(thread_messages)):
                        if thread_messages[j].author == MessageAuthor.ASSISTANT:
                            response_content = thread_messages[j].content
                            break
                    break
            
            return question_content, response_content or "No following response found"
        
        return "Unknown question", "Unknown response"
        
    except Exception as e:
        print(f"Error extracting Q&A context: {e}")
        return "Error extracting question", "Error extracting response"

def _log_user_reaction(db: Session, user: User, message: Message, reaction_type: str):
    """
    Log user reaction to permanent audit table with full context.
    This data is never deleted to maintain complete reaction history.
    """
    try:
        # Extract question-response context
        question_content, response_content = _extract_question_response_context(db, message)
        
        # Convert reaction type to log enum
        if reaction_type is None:
            log_reaction_type = ReactionLogType.REMOVED
        else:
            log_reaction_type = ReactionLogType.LIKE if reaction_type == "like" else ReactionLogType.DISLIKE
        
        # Create session info with metadata
        session_info = {
            "thread_type": message.thread.thread_type.value if message.thread.thread_type else None,
            "thread_language": message.thread.language,
            "message_author": message.author.value,
            "user_language": user.preferred_language,
            "user_theme": user.theme
        }
        
        # Create reaction log entry
        reaction_log = UserReactionLog(
            id=uuid.uuid4(),
            user_id=user.id,
            user_name=user.username,
            message_id=message.id,
            thread_id=message.thread_id,
            question_content=question_content,
            response_content=response_content,
            reaction_type=log_reaction_type,
            timestamp=datetime.now(timezone.utc),
            session_info=session_info
        )
        
        db.add(reaction_log)
        db.commit()
        
        print(f"Logged reaction: User {user.username} ({log_reaction_type.value}) on message {message.id}")
        
    except Exception as e:
        print(f"Error logging user reaction: {e}")
        # Don't fail the main operation if logging fails
        pass

@router.post("/")
async def add_reaction(
    reaction_data: ReactionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add or update a reaction to a message"""
    
    # Find the message
    message = db.query(Message).filter(Message.id == reaction_data.message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify the message belongs to a thread owned by the current user
    if message.thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to react to this message"
        )
    
    # Log the reaction before updating (capture both old and new state)
    _log_user_reaction(db, current_user, message, reaction_data.reaction_type)
    
    # Convert string to enum and update the reaction
    try:
        if reaction_data.reaction_type.lower() == "like":
            message.reaction = ReactionType.LIKE
        elif reaction_data.reaction_type.lower() == "dislike":
            message.reaction = ReactionType.DISLIKE
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reaction type: {reaction_data.reaction_type}. Must be 'like' or 'dislike'"
            )
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reaction type must be a string"
        )
    
    db.commit()
    
    return {"message": "Reaction updated successfully"}

@router.delete("/{message_id}")
async def remove_reaction(
    message_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a reaction from a message"""
    
    # Find the message
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify the message belongs to a thread owned by the current user
    if message.thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this message"
        )
    
    # Log the reaction removal
    _log_user_reaction(db, current_user, message, None)
    
    # Remove the reaction
    message.reaction = None
    db.commit()
    
    return {"message": "Reaction removed successfully"}