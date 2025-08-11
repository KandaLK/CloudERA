"""
Workflow State Broadcasting System

Provides real-time workflow state updates for frontend display.
Uses in-memory state management with fire-and-forget broadcasting.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class WorkflowStage(str, Enum):
    """Workflow stages for state tracking"""
    IDLE = "idle"
    THINKING = "thinking"
    TRANSLATION_PROCESSING = "translation_processing"
    INTENTION_EXTRACTION = "intention_extraction"
    QUESTION_ENHANCEMENT = "question_enhancement"
    QUESTION_DECOMPOSITION = "question_decomposition"
    RE_EVALUATION = "re_evaluation"
    PARALLEL_RETRIEVAL = "parallel_retrieval"
    KNOWLEDGE_BASE_SEARCH = "knowledge_base_search"
    WEB_SEARCH = "web_search"
    URL_SCRAPING = "url_scraping"
    DATA_PREPARATION = "data_preparation"
    RESPONSE_GENERATION = "response_generation"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class WorkflowState:
    """Current workflow state"""
    thread_id: str
    stage: WorkflowStage
    message: str
    progress: Optional[int] = None  # 0-100 percentage
    details: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class WorkflowStateBroadcaster:
    """Manages workflow state broadcasting for real-time updates"""
    
    def __init__(self):
        # In-memory state storage per thread
        self._thread_states: Dict[str, WorkflowState] = {}
        # SSE connections per thread
        self._connections: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()
    
    async def update_state(self, thread_id: str, stage: WorkflowStage, 
                          message: str, progress: Optional[int] = None,
                          details: Optional[Dict[str, Any]] = None) -> None:
        """Update workflow state for a thread (fire-and-forget)"""
        try:
            state = WorkflowState(
                thread_id=thread_id,
                stage=stage,
                message=message,
                progress=progress,
                details=details or {}
            )
            
            async with self._lock:
                self._thread_states[thread_id] = state
                
                # Broadcast to all connected clients for this thread
                if thread_id in self._connections:
                    disconnected_queues = []
                    for queue in self._connections[thread_id]:
                        try:
                            queue.put_nowait(state)
                        except asyncio.QueueFull:
                            pass
                        except Exception as e:
                            disconnected_queues.append(queue)
                    
                    # Clean up disconnected queues
                    for queue in disconnected_queues:
                        self._connections[thread_id].remove(queue)
                        
            
        except Exception as e:
            pass
    
    def get_current_state(self, thread_id: str) -> Optional[WorkflowState]:
        """Get current state for a thread"""
        return self._thread_states.get(thread_id)
    
    async def add_connection(self, thread_id: str) -> asyncio.Queue:
        """Add SSE connection for a thread"""
        async with self._lock:
            if thread_id not in self._connections:
                self._connections[thread_id] = []
            
            # Create queue with reasonable size limit
            queue = asyncio.Queue(maxsize=50)
            self._connections[thread_id].append(queue)
            
            # Send current state if available
            current_state = self._thread_states.get(thread_id)
            if current_state:
                try:
                    queue.put_nowait(current_state)
                except asyncio.QueueFull:
                    pass
                    
            return queue
    
    async def remove_connection(self, thread_id: str, queue: asyncio.Queue) -> None:
        """Remove SSE connection for a thread"""
        async with self._lock:
            if thread_id in self._connections and queue in self._connections[thread_id]:
                self._connections[thread_id].remove(queue)
                if not self._connections[thread_id]:
                    del self._connections[thread_id]
    
    async def cleanup_thread(self, thread_id: str) -> None:
        """Clean up thread state and connections"""
        async with self._lock:
            self._thread_states.pop(thread_id, None)
            self._connections.pop(thread_id, None)
    
    def get_status(self) -> Dict[str, Any]:
        """Get broadcaster status"""
        return {
            "active_threads": len(self._thread_states),
            "active_connections": sum(len(conns) for conns in self._connections.values()),
            "threads_with_connections": list(self._connections.keys()),
            "total_connection_queues": sum(len(conns) for conns in self._connections.values())
        }

# Global broadcaster instance
_broadcaster: Optional[WorkflowStateBroadcaster] = None

def get_workflow_broadcaster() -> WorkflowStateBroadcaster:
    """Get or create the global workflow broadcaster"""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = WorkflowStateBroadcaster()
    return _broadcaster

# Convenience functions for agents
async def emit_workflow_state(thread_id: str, stage: WorkflowStage, 
                             message: str, progress: Optional[int] = None,
                             details: Optional[Dict[str, Any]] = None) -> None:
    """Emit workflow state update (fire-and-forget)"""
    try:
        broadcaster = get_workflow_broadcaster()
        await broadcaster.update_state(thread_id, stage, message, progress, details)
    except Exception as e:
        pass  # Silently ignore errors for fire-and-forget emissions

# Stage-specific convenience functions
async def emit_thinking(thread_id: str) -> None:
    """Emit initial thinking state when user sends message"""
    await emit_workflow_state(thread_id, WorkflowStage.THINKING, "CloudERA Thinking...")

async def emit_translation_processing(thread_id: str) -> None:
    """Emit translation processing state for Sinhala messages"""
    await emit_workflow_state(thread_id, WorkflowStage.TRANSLATION_PROCESSING, "Translating User Question")

async def emit_intention_extraction(thread_id: str, message: str = "Extract User Intention") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.INTENTION_EXTRACTION, message)

async def emit_intention_extracted(thread_id: str, intent: str, domain_relevance: str, confidence: str) -> None:
    """Emit detailed intention extraction results"""
    message = f"Extract the Intent"
    details = {
        "extracted_intent": intent,
        "domain_relevance": domain_relevance,
        "confidence": confidence
    }
    await emit_workflow_state(thread_id, WorkflowStage.INTENTION_EXTRACTION, message, None, details)

async def emit_domain_classified(thread_id: str, domain_relevance: str, confidence_score: float) -> None:
    """Emit domain classification results - Combined with intention extraction"""
    # This is now part of intention extraction display
    pass

async def emit_question_enhancement(thread_id: str, message: str = "Now Enhance User Question") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.QUESTION_ENHANCEMENT, message)

async def emit_question_enhanced(thread_id: str, enhanced_question: str) -> None:
    """Emit enhanced question results"""
    message = "Enhanced Question"
    details = {
        "enhanced_question": enhanced_question
    }
    await emit_workflow_state(thread_id, WorkflowStage.QUESTION_ENHANCEMENT, message, None, details)

async def emit_question_decomposition(thread_id: str, message: str = "Sub Questions") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.QUESTION_DECOMPOSITION, message)

async def emit_question_decomposed(thread_id: str, sub_questions: list, web_queries: list) -> None:
    """Emit question decomposition results"""
    message = f"Sub Questions"
    details = {
        "sub_questions": sub_questions,
        "web_queries": web_queries,
        "sub_questions_count": len(sub_questions),
        "web_queries_count": len(web_queries)
    }
    await emit_workflow_state(thread_id, WorkflowStage.QUESTION_DECOMPOSITION, message, None, details)

async def emit_re_evaluation(thread_id: str, message: str = "Re Evaluvate Decisions") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.RE_EVALUATION, message)

async def emit_parallel_retrieval(thread_id: str, message: str = "Extract Relevant Data ") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.PARALLEL_RETRIEVAL, message)


async def emit_data_preparation(thread_id: str = "Preparing Data") -> None:
    """Emit data preparation state after parallel retrieval"""
    await emit_workflow_state(thread_id, WorkflowStage.DATA_PREPARATION, "Preparing response from collected data")

async def emit_response_generation(thread_id: str, message: str = "Generate The Response") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.RESPONSE_GENERATION, message)


# Clear the workflow state when completed
async def emit_completed(thread_id: str, message: str = "") -> None:
    """Mark workflow as completed and schedule cleanup"""
    try:
        broadcaster = get_workflow_broadcaster()
        
        # First emit completed state instead of immediately cleaning up
        await emit_workflow_state(thread_id, WorkflowStage.COMPLETED, "Processing Complete", 100)
        
        # Schedule cleanup after a brief delay to allow UI updates
        async def delayed_cleanup():
            await asyncio.sleep(2)  # 2 second delay
            await broadcaster.cleanup_thread(thread_id)
            print(f"[WorkflowState] Completed delayed cleanup for thread {thread_id}")
        
        # Run cleanup in background without blocking
        asyncio.create_task(delayed_cleanup())
        
        print(f"[WorkflowState] Marked thread {thread_id} as completed, scheduled cleanup")
    except Exception as e:
        print(f"[WorkflowState] Error in completion workflow: {e}")
        pass  # Silently ignore errors for fire-and-forget cleanup

async def emit_error(thread_id: str, message: str = "ERROR OCCURRED") -> None:
    await emit_workflow_state(thread_id, WorkflowStage.ERROR, message)