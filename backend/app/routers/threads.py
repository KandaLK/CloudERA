from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uuid

from app.database.database import get_db
from app.models.user import User
from app.models.chat_thread import ChatThread
from app.models.message import Message, MessageAuthor
from app.models.user_reaction_log import UserReactionLog
from app.schemas.chat_thread import ChatThreadResponse, ChatThreadListResponse, ChatThreadCreate, ChatThreadUpdate
from app.core.auth import get_current_active_user

router = APIRouter()

# Welcome messages are now generated during user registration for permanent threads

@router.get("/", response_model=List[ChatThreadListResponse])
async def get_user_threads(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all chat threads for the current user"""
    # Query threads with message count using subquery
    threads_with_count = db.query(
        ChatThread,
        func.count(Message.id).label('message_count')
    ).outerjoin(Message).filter(
        ChatThread.user_id == current_user.id
    ).group_by(ChatThread.id).all()
    
    # Convert to list response format
    thread_responses = []
    for thread, message_count in threads_with_count:
        thread_data = ChatThreadListResponse(
            id=thread.id,
            name=thread.name,
            user_id=thread.user_id,
            created_at=thread.created_at,
            last_modified=thread.last_modified,
            language=thread.language,
            message_count=message_count or 0
        )
        thread_responses.append(thread_data)
    
    return thread_responses

@router.post("/", response_model=ChatThreadResponse)
async def create_thread(
    thread_data: ChatThreadCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new chat thread"""
    
    # Create new thread
    new_thread = ChatThread(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=thread_data.name,
        language=thread_data.language or 'ENG',
        is_permanent=False,
        is_active=False
    )
    
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    
    return ChatThreadResponse.model_validate(new_thread)

@router.get("/{thread_id}", response_model=ChatThreadResponse)
async def get_thread(
    thread_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat thread with messages"""
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    return ChatThreadResponse.model_validate(thread)

@router.put("/{thread_id}", response_model=ChatThreadResponse)
async def update_thread(
    thread_id: str,
    thread_data: ChatThreadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update/rename a chat thread"""
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Don't allow renaming permanent threads
    if thread.is_permanent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot rename permanent threads"
        )
    
    # Update thread name if provided
    if thread_data.name is not None:
        thread.name = thread_data.name
    
    db.commit()
    db.refresh(thread)
    
    return ChatThreadResponse.model_validate(thread)

@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a chat thread or clear messages from permanent threads"""
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # First delete all reaction logs for messages in this thread
    db.query(UserReactionLog).filter(UserReactionLog.thread_id == thread_id).delete()
    
    # Then delete all messages from the thread
    db.query(Message).filter(Message.thread_id == thread_id).delete()
    
    if thread.is_permanent:
        # For permanent threads, just clear messages and set inactive
        thread.is_active = False
        db.commit()
        return {"message": "Thread messages cleared successfully"}
    else:
        # For non-permanent threads, delete the entire thread
        db.delete(thread)
        db.commit()
        return {"message": "Thread deleted successfully"}

@router.delete("/")
async def clear_all_thread_messages(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear all messages from all threads for the current user (threads remain permanent)"""
    threads = db.query(ChatThread).filter(ChatThread.user_id == current_user.id).all()
    
    # First delete all reaction logs for user's messages
    db.query(UserReactionLog).filter(UserReactionLog.user_id == current_user.id).delete()
    
    # Then delete all messages for user's threads
    db.query(Message).filter(Message.user_id == current_user.id).delete()
    
    # Set all threads as inactive
    for thread in threads:
        thread.is_active = False
    
    db.commit()
    
    return {"message": f"Cleared messages from {len(threads)} threads successfully"}