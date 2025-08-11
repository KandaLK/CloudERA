from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import json
import asyncio
from datetime import datetime, timezone

from app.database.database import get_db
from app.models.user import User
from app.models.chat_thread import ChatThread
from app.models.message import Message, MessageAuthor
from app.schemas.message import ChatRequest, ChatResponse, MessageResponse
from app.core.auth import get_current_active_user
from app.agents.agent_service import generate_agent_response, get_agent_status
from app.services.translation import get_translation_service
from app.agents.workflow_state import get_workflow_broadcaster, emit_translation_processing
from app.core.security import verify_token

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    
    # Validate thread exists and belongs to user (thread_id is now required)
    if not chat_request.thread_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thread ID is required"
        )
        
    thread = db.query(ChatThread).filter(
        ChatThread.id == chat_request.thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Set thread as active
    # First, deactivate all other threads for this user
    db.query(ChatThread).filter(
        ChatThread.user_id == current_user.id,
        ChatThread.id != thread.id
    ).update({ChatThread.is_active: False})
    
    # Activate current thread
    thread.is_active = True
    
    # Check if this is first access to thread (no messages yet)
    message_count = db.query(Message).filter(Message.thread_id == thread.id).count()
    first_access = message_count == 0
    
    # If first access, create welcome message based on thread type
    if first_access:
        from app.routers.auth import get_thread_config
        thread_config = get_thread_config()
        
        if thread.thread_type and thread.thread_type in thread_config:
            config = thread_config[thread.thread_type]
            welcome_content = config["welcome_si"] if chat_request.language == "SIN" else config["welcome_en"]
            
            welcome_message = Message(
                id=uuid.uuid4(),
                thread_id=thread.id,
                user_id=current_user.id,
                author=MessageAuthor.ASSISTANT,
                content=welcome_content
            )
            db.add(welcome_message)
    
    # Create user message first (store original message in database)
    original_message = chat_request.message
    user_message = Message(
        id=uuid.uuid4(),
        thread_id=thread.id,
        user_id=current_user.id,
        author=MessageAuthor.USER,
        content=original_message  # Store original message (Sinhala or English)
    )
    
    db.add(user_message)
    db.commit()
    
    # Get chat history for context (before translation)
    chat_history = db.query(Message).filter(
        Message.thread_id == thread.id
    ).order_by(Message.timestamp).all()
    
    # Handle translation for Sinhala messages using parallel translation
    processed_message = original_message
    translated_history = None
    
    if chat_request.language == "SIN":
        # Emit translation processing state
        await emit_translation_processing(str(thread.id))
        
        translation_service = get_translation_service()
        translation_result = await translation_service.translate_message_and_history_parallel(
            current_message=original_message,
            messages=chat_history[:-1]  # Exclude the just-added message to avoid duplication
        )
        
        processed_message = translation_result["translated_message"]
        translated_history = translation_result["translated_history"] if translation_result["success"] else None
        
        print(f"[ChatRouter] Parallel translation completed - Message: {len(processed_message)} chars, History: {len(translated_history or '')} chars")
    
    # Generate AI response using multi-agent system with translated content
    try:
        agent_result = await generate_agent_response(
            message=processed_message,  # Use translated English message for processing
            chat_history=chat_history,
            user_id=str(current_user.id),
            thread_id=str(thread.id),
            language=chat_request.language or "ENG",
            use_web_search=chat_request.use_web_search,
            translated_history=translated_history  # Pass translated history for Sinhala threads
        )
        ai_response_content = agent_result["response"]
        agent_metadata = agent_result["metadata"]
        
    except Exception as e:
        # Fallback response if agent service fails
        ai_response_content = "I apologize, but I'm having trouble processing your request right now. Please try again."
        agent_metadata = {"type": "fallback", "error": str(e), "agent_processing": False}
    
    # Create assistant message
    assistant_message = Message(
        id=uuid.uuid4(),
        thread_id=thread.id,
        user_id=current_user.id,
        author=MessageAuthor.ASSISTANT,
        content=ai_response_content
    )
    
    db.add(assistant_message)
    
    # Update thread's last_modified
    thread.last_modified = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(assistant_message)
    
    return ChatResponse(
        message_id=assistant_message.id,
        thread_id=thread.id,
        response=ai_response_content,
        created_at=assistant_message.timestamp,
        agent_metadata=agent_metadata
    )

@router.get("/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a thread"""
    
    # Verify thread exists and belongs to user
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    messages = db.query(Message).filter(
        Message.thread_id == thread_id
    ).order_by(Message.timestamp).all()
    
    return [MessageResponse.model_validate(msg) for msg in messages]

@router.put("/messages/{message_id}")
async def edit_message(
    message_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Edit a user message (only user messages can be edited)"""
    
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify message belongs to user and is a user message
    if message.user_id != current_user.id or message.author != MessageAuthor.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit this message"
        )
    
    # Update message content
    new_content = request.get("content", "")
    message.content = new_content
    db.commit()
    
    return {"message": "Message updated successfully"}

@router.post("/activate-thread/{thread_id}")
async def activate_thread(
    thread_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set a thread as active when user switches to it"""
    
    # Validate thread exists and belongs to user
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Deactivate all other threads
    db.query(ChatThread).filter(
        ChatThread.user_id == current_user.id,
        ChatThread.id != thread_id
    ).update({ChatThread.is_active: False})
    
    # Activate selected thread
    thread.is_active = True
    db.commit()
    
    return {"message": "Thread activated successfully", "thread_id": thread_id}

@router.get("/agent-status")
async def get_agent_system_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get status of the multi-agent system"""
    try:
        status = get_agent_status()
        return {
            "status": "success",
            "agent_system": status,
            "user_id": str(current_user.id)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "user_id": str(current_user.id)
        }

@router.get("/stream/{thread_id}")
async def stream_workflow_state(
    thread_id: str,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Stream real-time workflow state updates via Server-Sent Events"""
    
    # Authenticate user via token query parameter
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Verify thread exists and belongs to user
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    async def generate_state_stream():
        """Generate SSE stream for workflow state updates"""
        broadcaster = get_workflow_broadcaster()
        queue = await broadcaster.add_connection(thread_id)
        
        try:
            
            # Send initial connection event
            initial_data = {
                "type": "connection",
                "message": "Connected to workflow state stream",
                "thread_id": thread_id,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(initial_data)}\n\n"
            
            # Stream workflow state updates
            while True:
                try:
                    # Wait for state update with timeout
                    state = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # Format state for SSE
                    state_data = {
                        "type": "state_update",
                        "thread_id": state.thread_id,
                        "stage": state.stage,
                        "message": state.message,
                        "progress": state.progress,
                        "details": state.details,
                        "timestamp": state.timestamp
                    }
                    
                    yield f"data: {json.dumps(state_data)}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    ping_data = {
                        "type": "ping",
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(ping_data)}\n\n"
                    continue
                    
                except Exception as e:
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            pass
        finally:
            await broadcaster.remove_connection(thread_id, queue)
    
    return StreamingResponse(
        generate_state_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )