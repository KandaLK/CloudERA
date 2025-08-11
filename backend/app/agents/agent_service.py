"""
Agent Service Module

Replaces the basic AI service with the multi-agent workflow system.
Provides enhanced AI responses using intent extraction, question enhancement,
decomposition, and validation with dual-layer memory management.
"""

from typing import List, Dict, Any
from app.models.message import Message
from app.core.config import settings
from .workflow import IntentExtractionWorkflow
from .session_persistence import save_sessions_to_disk, load_sessions_from_disk, get_persistence_status
from .circuit_breaker import circuit_manager, CircuitBreakerOpenError
from .workflow_state import emit_thinking


import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import time

# Global workflow instance for singleton pattern
_workflow_instance = None
_workflow_lock = threading.Lock()
_active_sessions = {}
_session_lock = threading.Lock()
_thread_pool = ThreadPoolExecutor(max_workers=settings.max_concurrent_users)

# Session metrics tracking
_session_metrics = {
    "total_sessions_created": 0,
    "total_sessions_completed": 0,
    "capacity_limit_hits": 0,
    "stale_sessions_cleaned": 0,
    "response_times": [],
    "error_counts": defaultdict(int),
    "peak_concurrent_users": 0,
    "startup_time": time.time()
}

# Initialize session persistence
def _initialize_session_persistence():
    """Load sessions from disk on startup"""
    global _active_sessions, _session_metrics
    
    pass  # Initialize session persistence
    loaded_sessions, loaded_metrics = load_sessions_from_disk()
    
    if loaded_sessions:
        _active_sessions.update(loaded_sessions)
        pass  # Restored sessions from backup
    
    if loaded_metrics:
        # Merge loaded metrics with defaults
        for key, value in loaded_metrics.items():
            if key in _session_metrics and key != "response_times":
                if key == "error_counts":
                    _session_metrics[key].update(value)
                else:
                    _session_metrics[key] = value
        pass  # Restored metrics from backup

# Initialize persistence on module load
_initialize_session_persistence()


def get_workflow_instance() -> IntentExtractionWorkflow:
    """Get or create the global workflow instance (thread-safe)"""
    global _workflow_instance
    if _workflow_instance is None:
        with _workflow_lock:
            if _workflow_instance is None:  # Double-check locking
                pass  # Creating workflow instance
                _workflow_instance = IntentExtractionWorkflow()
    return _workflow_instance


def _get_session_key(user_id: str, thread_id: str) -> str:
    """Generate session key for user/thread combination"""
    return f"{user_id}-{thread_id}"


def _register_session(user_id: str, thread_id: str) -> bool:
    """Register a new session (returns False if max sessions reached)"""
    session_key = _get_session_key(user_id, thread_id)
    
    with _session_lock:
        # Check if we're at max capacity
        if len(_active_sessions) >= settings.max_concurrent_users and session_key not in _active_sessions:
            pass  # Max concurrent users reached
            _session_metrics["capacity_limit_hits"] += 1
            return False
        
        current_time = asyncio.get_event_loop().time()
        _active_sessions[session_key] = {
            "user_id": user_id,
            "thread_id": thread_id,
            "last_activity": current_time,
            "start_time": current_time,
            "request_count": 0
        }
        
        # Update metrics
        _session_metrics["total_sessions_created"] += 1
        current_active = len(_active_sessions)
        if current_active > _session_metrics["peak_concurrent_users"]:
            _session_metrics["peak_concurrent_users"] = current_active
            
        pass  # Session registered
        return True


def _unregister_session(user_id: str, thread_id: str):
    """Unregister a session when complete"""
    session_key = _get_session_key(user_id, thread_id)
    
    with _session_lock:
        if session_key in _active_sessions:
            session_data = _active_sessions[session_key]
            
            # Calculate session duration for metrics
            if "start_time" in session_data:
                session_duration = asyncio.get_event_loop().time() - session_data["start_time"]
                _session_metrics["response_times"].append(session_duration)
                
                # Keep only last 100 response times to prevent memory growth
                if len(_session_metrics["response_times"]) > 100:
                    _session_metrics["response_times"] = _session_metrics["response_times"][-100:]
            
            del _active_sessions[session_key]
            _session_metrics["total_sessions_completed"] += 1
            pass  # Session unregistered


def _cleanup_stale_sessions(max_age_seconds=300):  # 5 minutes
    """Clean up sessions that haven't been active recently"""
    current_time = asyncio.get_event_loop().time()
    stale_sessions = []
    
    with _session_lock:
        for session_key, session_data in _active_sessions.items():
            if current_time - session_data["last_activity"] > max_age_seconds:
                stale_sessions.append(session_key)
        
        for session_key in stale_sessions:
            del _active_sessions[session_key]
            pass  # Cleaned up stale session
    
    if stale_sessions:
        _session_metrics["stale_sessions_cleaned"] += len(stale_sessions)
        pass  # Cleaned up stale sessions
    
    # Backup sessions to disk periodically
    _backup_sessions_to_disk()

def _backup_sessions_to_disk():
    """Backup current sessions to disk for persistence"""
    try:
        with _session_lock:
            # Only backup if we have active sessions or metrics to save
            if _active_sessions or _session_metrics["total_sessions_created"] > 0:
                save_sessions_to_disk(_active_sessions.copy(), dict(_session_metrics))
    except Exception as e:
        pass  # Error backing up sessions


async def generate_agent_response(
    message: str,
    chat_history: List[Message],
    user_id: str,
    thread_id: str,
    language: str = "ENG",
    use_web_search: bool = True,
    translated_history: str = None
) -> Dict[str, Any]:
    """
    Generate AI response using the multi-agent workflow system
    
    Returns:
        Dict containing response and metadata about the agent processing
    """
    
    pass  # Processing request
    
    # Clean up stale sessions periodically
    _cleanup_stale_sessions()
    
    # Register session (check capacity)
    if not _register_session(user_id, thread_id):
        return {
            "response": "I'm sorry, but the system is currently at maximum capacity. Please try again in a few moments.",
            "metadata": {
                "type": "capacity_limit",
                "agent_processing": False,
                "max_concurrent_users": settings.max_concurrent_users
            }
        }
    
    try:
        # Emit initial thinking state
        await emit_thinking(thread_id)
        
        # Get workflow instance
        workflow = get_workflow_instance()
        
        # Convert chat history to simple format
        history = []
        for msg in chat_history[-10:]:  # Last 10 messages for context
            history.append({
                "role": "user" if msg.author.value == "user" else "assistant",
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })
        
        pass  # Using chat history
        
        # Process query through workflow with language awareness
        try:
            workflow_result = await workflow.process_query(
                user_query=message,
                user_id=user_id,
                thread_id=thread_id,
                history=history,
                language=language,
                translated_history=translated_history
            )
            
        except Exception as e:
            pass  # Workflow processing error
            # Let the error fall through to the main exception handler
            raise e
        
        pass  # Workflow result processed
        
        # Handle workflow result - now all types are unified as "response"
        if workflow_result["type"] == "response":
            # Workflow generated complete response
            response_content = workflow_result["response"]
            response_metadata = {
                "type": workflow_result.get("response_type", "unknown"),  # clarification, domain_response, not_allowed
                "confidence": workflow_result.get("confidence", 0.5),
                "intent": workflow_result.get("intent"),
                "domain_relevance": workflow_result.get("domain_relevance"),
                "enhanced_question": workflow_result.get("enhanced_question"),
                "sub_questions_count": len(workflow_result.get("sub_questions", [])),
                "web_queries_count": len(workflow_result.get("web_queries", [])),
                "web_search_performed": workflow_result.get("web_search_needed", False),
                "web_results_count": len(workflow_result.get("web_search_results", [])),
                "scraped_sources_count": len(workflow_result.get("scraped_content", {})),
                "sources_used": workflow_result.get("sources_used", []),
                "iterations": workflow_result.get("iterations", 0),
                "re_evaluator_iterations": workflow_result.get("re_evaluator_iterations", 0),
                "agent_processing": True
            }
            
        elif workflow_result["type"] == "error":
            # Error occurred in workflow
            response_content = workflow_result["message"]
            response_metadata = {
                "type": "error",
                "error_details": workflow_result.get("error_details"),
                "agent_processing": True
            }
            
        else:
            # Unknown result type - fallback
            response_content = "I'm having trouble processing your request. Could you please rephrase your question?"
            response_metadata = {
                "type": "fallback",
                "agent_processing": True
            }
        
        # Trigger educational content agent independently with LTM processing (fire-and-forget)
        from .educational_agent import get_educational_agent
        educational_agent = get_educational_agent()
        asyncio.create_task(
            educational_agent.process_educational_trigger(
                user_id=user_id,
                user_query=message,
                response_type=response_metadata.get("type", "unknown"),
                conversation_history=history
            )
        )
        
        # Update memory with assistant response for educational agent only (run in background - non-blocking)
        asyncio.create_task(workflow.memory_manager.process_message(
            user_id, thread_id, "assistant", response_content, chat_history, for_educational_agent=True
        ))
        
        pass  # Generated response
        
        # Unregister session
        _unregister_session(user_id, thread_id)
        
        return {
            "response": response_content,
            "metadata": response_metadata
        }
        
    except Exception as e:
        pass  # Error in agent service
        
        # Track error in metrics
        error_type = type(e).__name__
        _session_metrics["error_counts"][error_type] += 1
        
        # Unregister session on error
        _unregister_session(user_id, thread_id)
        
        # Fallback to simple response
        fallback_response = _generate_fallback_response(message, language)
        return {
            "response": fallback_response,
            "metadata": {
                "type": "fallback",
                "error": str(e),
                "error_type": error_type,
                "agent_processing": False
            }
        }




def _generate_fallback_response(message: str, language: str = "ENG") -> str:
    """Generate fallback responses when agent service is unavailable"""
    
    message_lower = message.lower()
    
    # Cloud provider specific responses
    if any(term in message_lower for term in ["aws", "amazon", "ec2", "s3", "lambda"]):
        if language == "SIN":
            return "AWS සේවා පිළිබඳ ඔබගේ ප්‍රශ්නය සඳහා, AWS documentation හෝ AWS Support Center වෙතින් සහාය ගන්න."
        return "For AWS-related questions, I recommend checking the AWS Documentation or contacting AWS Support for detailed guidance on EC2, S3, Lambda, and other services."
    
    elif any(term in message_lower for term in ["azure", "microsoft", "virtual machine"]):
        if language == "SIN":
            return "Microsoft Azure සේවා පිළිබඳ, Azure Portal හෝ Microsoft Learn හරහා වැඩිදුර තොරතුරු ලබා ගන්න."
        return "For Microsoft Azure questions, please refer to the Azure Portal documentation or Microsoft Learn for comprehensive guides on virtual machines, storage, and other services."
    
    elif any(term in message_lower for term in ["gcp", "google cloud", "compute engine"]):
        if language == "SIN":
            return "Google Cloud Platform පිළිබඳ ඔබගේ ප්‍රශ්නය සඳහා, GCP Console හෝ Google Cloud Documentation බලන්න."
        return "For Google Cloud Platform questions, I suggest consulting the GCP Console documentation or Google Cloud guides for information about Compute Engine, Cloud Storage, and other services."
    
    elif any(term in message_lower for term in ["security", "firewall", "vpn", "ssl"]):
        if language == "SIN":
            return "ජාල ආරක්ෂාව පිළිබඳ, කරුණාකර ඔබගේ cloud provider ගේ security best practices ගණන් ගන්න."
        return "For security and network configuration questions, please follow your cloud provider's security best practices and consider consulting with your organization's security team."
    
    # General fallback
    if language == "SIN":
        return "මම වලාකුළු සේවා (AWS, Azure, GCP), ආරක්ෂාව, සහ ජාල වින්‍යාසය පිළිබඳ ප්‍රශ්න වලට උපකාර කරමි. කරුණාකර ඔබගේ ප්‍රශ්නය වඩාත් නිශ්චිතව නැවත ප්‍රකාශ කරන්න."
    
    return "I'm here to help with cloud services (AWS, Azure, GCP), security, and network configuration questions. Could you please provide more specific details about what you'd like assistance with?"


def get_agent_status() -> Dict[str, Any]:
    """Get current status of the agent system with detailed metrics"""
    try:
        workflow = get_workflow_instance()
        workflow_status = workflow.get_workflow_status()
        
        # Calculate response time statistics
        response_times = _session_metrics["response_times"]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # Add detailed session management info
        with _session_lock:
            current_active = len(_active_sessions)
            session_info = {
                "active_sessions": current_active,
                "max_concurrent_users": settings.max_concurrent_users,
                "capacity_utilization": current_active / settings.max_concurrent_users,
                "session_details": list(_active_sessions.keys()),
                
                # Performance metrics
                "metrics": {
                    "total_sessions_created": _session_metrics["total_sessions_created"],
                    "total_sessions_completed": _session_metrics["total_sessions_completed"],
                    "capacity_limit_hits": _session_metrics["capacity_limit_hits"],
                    "stale_sessions_cleaned": _session_metrics["stale_sessions_cleaned"],
                    "peak_concurrent_users": _session_metrics["peak_concurrent_users"],
                    "uptime_seconds": time.time() - _session_metrics["startup_time"],
                    
                    # Response time statistics
                    "response_times": {
                        "average_seconds": round(avg_response_time, 2),
                        "min_seconds": round(min_response_time, 2),
                        "max_seconds": round(max_response_time, 2),
                        "sample_count": len(response_times)
                    },
                    
                    # Error statistics
                    "error_counts": dict(_session_metrics["error_counts"]),
                    "total_errors": sum(_session_metrics["error_counts"].values()),
                    
                    # System health indicators
                    "health_indicators": {
                        "capacity_pressure": "HIGH" if current_active >= settings.max_concurrent_users * 0.8 else "NORMAL",
                        "error_rate": sum(_session_metrics["error_counts"].values()) / max(_session_metrics["total_sessions_created"], 1),
                        "avg_session_duration": round(avg_response_time, 2) if avg_response_time else 0
                    }
                },
                
                # Session persistence info
                "persistence": get_persistence_status(),
                
                # Circuit breaker status
                "circuit_breakers": circuit_manager.get_all_stats()
            }
        
        workflow_status["session_management"] = session_info
        return workflow_status
        
    except Exception as e:
        return {
            "error": str(e),
            "workflow_initialized": False,
            "session_management": {
                "active_sessions": 0,
                "max_concurrent_users": settings.max_concurrent_users,
                "error": str(e),
                "metrics": {
                    "total_sessions_created": _session_metrics.get("total_sessions_created", 0),
                    "error_counts": dict(_session_metrics.get("error_counts", {}))
                }
            }
        }