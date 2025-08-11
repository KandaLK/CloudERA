"""
LangGraph Workflow Implementation

Implements the complete multi-agent workflow using LangGraph StateGraph:
- AgentState: Complete state management for workflow
- IntentExtractionWorkflow: Main orchestrator with conditional routing
- Error handling and fallback mechanisms
"""

import asyncio
from typing import Dict, List, Optional, Any, TypedDict
from langgraph.graph import StateGraph, END

from app.core.config import settings
from .memory import MemoryManager
from .agents import IntentionExtractor, QuestionEnhancer, QuestionDecomposer, ReEvaluator, ParallelRetriever, ResponseGenerator
from .workflow_state import (
    emit_intention_extraction, emit_intention_extracted,
    emit_question_enhancement, emit_question_enhanced,
    emit_question_decomposition, emit_question_decomposed,
    emit_re_evaluation, emit_parallel_retrieval,
    emit_data_preparation,
    emit_response_generation, emit_completed, emit_error
)


class AgentState(TypedDict):
    """
    Complete state structure for the multi-agent workflow.
    Every field must be initialized and maintained throughout the workflow.
    """
    # Input state
    user_query: str
    user_id: str
    thread_id: str
    history: List[dict]
    memory_context: Dict[str, Any]
    thread_language: str  # Thread language (ENG/SIN)
    
    # Processing state  
    current_intent: Optional[str]
    domain_relevance: Optional[str]  # Domain relevance classification
    enhanced_question: Optional[str]
    sub_questions: List[str]
    web_queries: List[str]
    
    # Web search state
    web_search_results: List[Dict[str, Any]]
    scraped_content: Dict[str, str]
    url_confidence_scores: Dict[str, float]
    
    # Knowledge base retrieval state
    kb_results: List[Dict[str, Any]]
    kb_processed: bool
    
    # Combined retrieval state
    all_sources: List[Dict[str, Any]]
    retrieval_status: Dict[str, str]
    
    # Control state
    needs_clarification: bool
    clarification_question: Optional[str]
    confidence_score: float
    iteration_count: int
    max_iterations: int
    
    # Response state
    final_response: Optional[str]
    response_type: Optional[str]  # 'domain_response', 'not_allowed', 'clarification'
    response_confidence: float
    sources_used: List[str]


class IntentExtractionWorkflow:
    """Main workflow orchestrator using LangGraph"""
    
    def __init__(self):
        print("[Workflow] Initializing IntentExtractionWorkflow")
        
        # Initialize components
        self.memory_manager = MemoryManager()
        self.intention_extractor = IntentionExtractor()
        self.question_enhancer = QuestionEnhancer()
        self.question_decomposer = QuestionDecomposer()
        self.re_evaluator = ReEvaluator()
        self.parallel_retriever = ParallelRetriever()
        self.response_generator = ResponseGenerator()
        
        # Build the graph
        self.graph = self._build_graph()
        print("[Workflow] LangGraph workflow constructed successfully")
    
    async def _wrapped_intention_extractor(self, state: AgentState) -> AgentState:
        """Intention extractor with state emission"""
        thread_id = state.get("thread_id", "unknown")
        await emit_intention_extraction(thread_id)
        
        # Process with the intention extractor
        result = self.intention_extractor(state)
        
        # Emit detailed results
        if result.get("current_intent"):
            await emit_intention_extracted(
                thread_id,
                result.get("current_intent", ""),
                result.get("domain_relevance", "unknown"),
                "high" if result.get("confidence_score", 0.5) > 0.8 else "medium" if result.get("confidence_score", 0.5) > 0.5 else "low"
            )
        
        return result
    
    async def _wrapped_question_enhancer(self, state: AgentState) -> AgentState:
        """Question enhancer with state emission"""
        thread_id = state.get("thread_id", "unknown")
        await emit_question_enhancement(thread_id)
        
        # Process with the question enhancer
        result = self.question_enhancer(state)
        
        # Emit enhanced question if available
        if result.get("enhanced_question"):
            await emit_question_enhanced(
                thread_id,
                result.get("enhanced_question", "")
            )
        
        return result
    
    async def _wrapped_question_decomposer(self, state: AgentState) -> AgentState:
        """Question decomposer with state emission"""
        thread_id = state.get("thread_id", "unknown")
        await emit_question_decomposition(thread_id)
        
        # Process with the question decomposer
        result = self.question_decomposer(state)
        
        # Emit decomposition results if available
        if result.get("sub_questions") is not None or result.get("web_queries") is not None:
            await emit_question_decomposed(
                thread_id,
                result.get("sub_questions", []),
                result.get("web_queries", [])
            )
        
        return result
    
    async def _wrapped_re_evaluator(self, state: AgentState) -> AgentState:
        """Re-evaluator with state emission"""
        await emit_re_evaluation(state.get("thread_id", "unknown"))
        return self.re_evaluator(state)
    
    async def _wrapped_parallel_retriever(self, state: AgentState) -> AgentState:
        """Parallel retriever with state emission"""
        thread_id = state.get("thread_id", "unknown")
        await emit_parallel_retrieval(thread_id)
        
        # Process with the parallel retriever
        result = await self.parallel_retriever(state)
        
        
        # Emit data preparation state before moving to response generation
        await emit_data_preparation(thread_id)
        
        return result
    
    async def _wrapped_response_generator(self, state: AgentState) -> AgentState:
        """Response generator with state emission"""
        thread_id = state.get("thread_id", "unknown")
        await emit_response_generation(thread_id)
        
        # Process with the response generator
        result = await self.response_generator(state)
        
        # Emit completion to clear workflow state and hide card
        await emit_completed(thread_id)
        return result
    
    def _build_graph(self) -> StateGraph:
        """Construct the LangGraph workflow with conditional routing"""
        print("[Workflow] Building LangGraph StateGraph...")
        
        builder = StateGraph(AgentState)
        
        # Add nodes with state emission wrappers
        builder.add_node("intention_extractor", self._wrapped_intention_extractor)
        builder.add_node("question_enhancer", self._wrapped_question_enhancer)
        builder.add_node("question_decomposer", self._wrapped_question_decomposer)
        builder.add_node("re_evaluator", self._wrapped_re_evaluator)
        builder.add_node("parallel_retriever", self._wrapped_parallel_retriever)
        builder.add_node("response_generator", self._wrapped_response_generator)
        
        # Set entry point
        builder.set_entry_point("intention_extractor")
        
        # Add simple edges
        builder.add_edge("question_enhancer", "question_decomposer")
        builder.add_edge("question_decomposer", "re_evaluator")
        
        # Conditional routing functions
        def intention_router(state: AgentState) -> str:
            """Route after intention extraction"""
            intent = state.get('current_intent', 'Unknown')
            domain_relevance = state.get('domain_relevance', 'unknown')
            print(f"[Workflow] Intention router - Intent: {intent}")
            print(f"[Workflow] Intention router - Domain relevance: {domain_relevance}")
            print(f"[Workflow] Intention router - needs_clarification: {state['needs_clarification']}")
            
            if state["needs_clarification"]:
                print("[Workflow] Routing to response_generator (clarification)")
                return "response_generator"
            elif domain_relevance == "general":
                print("[Workflow] Routing to response_generator (not_allowed)")
                return "response_generator"
            else:
                print("[Workflow] Routing to question_enhancer")
                return "question_enhancer"
        
        def evaluator_router(state: AgentState) -> str:
            """Route after enhancement - direct path to parallel_retriever"""
            print("[Workflow] ReEvaluator completed enhancement, routing to parallel_retriever")
            return "parallel_retriever"
        
        # Add conditional edges
        builder.add_conditional_edges(
            "intention_extractor",
            intention_router,
            {
                "response_generator": "response_generator",
                "question_enhancer": "question_enhancer"
            }
        )
        
        builder.add_conditional_edges(
            "re_evaluator",
            evaluator_router,
            {
                "parallel_retriever": "parallel_retriever"
            }
        )
        
        # Add edge from parallel_retriever to response_generator
        builder.add_edge("parallel_retriever", "response_generator")
        
        # Add edge from response_generator to END
        builder.add_edge("response_generator", END)
        
        print("[Workflow] StateGraph construction complete")
        return builder.compile()
    
    async def process_query(self, user_query: str, user_id: str, thread_id: str, 
                     history: List[dict] = None, language: str = "ENG", translated_history: str = None) -> Dict[str, Any]:
        """Process a user query through the complete workflow"""
        
        print(f"[Workflow] Processing query from user {user_id}, thread {thread_id}")
        print(f"[Workflow] Query: {user_query[:100]}...")
        
        try:
            print(f"[Workflow] Language: {language}, Translated history available: {bool(translated_history)}")
            
            # Get memory context with language awareness and translated history
            memory_context = await self.memory_manager.get_context(
                user_id, thread_id, user_query, history, language, translated_history
            )
            
            # Initialize state
            initial_state: AgentState = {
                "user_query": user_query,
                "user_id": user_id,
                "thread_id": thread_id,
                "history": history or [],
                "memory_context": memory_context,
                "thread_language": language,  # Add thread language to state
                "current_intent": None,
                "domain_relevance": None,
                "enhanced_question": None,
                "sub_questions": [],
                "web_queries": [],
                # Web search initialization
                "web_search_results": [],
                "scraped_content": {},
                "url_confidence_scores": {},
                # Knowledge base initialization
                "kb_results": [],
                "kb_processed": False,
                # Combined retrieval initialization
                "all_sources": [],
                "retrieval_status": {"web_search": "pending", "knowledge_base": "pending"},
                # Control state
                "needs_clarification": False,
                "clarification_question": None,
                "confidence_score": 0.0,
                "iteration_count": 0,
                "max_iterations": settings.max_iterations,
                # Response state
                "final_response": None,
                "response_type": None,
                "response_confidence": 0.0,
                "sources_used": []
            }
            
            print("[Workflow] Initial state prepared, starting workflow execution...")
            
            # Run the workflow asynchronously
            final_state = await self.graph.ainvoke(initial_state)
            
            print(f"[Workflow] Workflow completed - iterations: {final_state.get('iteration_count', 0)}")
            
            # Trigger educational agent for general questions (non-blocking)
            asyncio.create_task(self._trigger_educational_agent_if_needed(final_state))
            
            # Process result - now all paths go through response_generator
            print("[Workflow] Workflow result: RESPONSE_GENERATED")
            print(f"[Workflow] Response type: {final_state.get('response_type', 'unknown')}")
            print(f"[Workflow] Final response length: {len(final_state.get('final_response', ''))}")
            print(f"[Workflow] Sources used: {len(final_state.get('sources_used', []))}")
            print(f"[Workflow] Final intent: {final_state.get('current_intent', 'None')}")
            print(f"[Workflow] Domain relevance: {final_state.get('domain_relevance', 'unknown')}")
            
            # Additional debug info for domain responses
            if final_state.get('response_type') == 'domain_response':
                print(f"[Workflow] Enhanced question: {final_state.get('enhanced_question', 'None')}")
                print(f"[Workflow] Generated {len(final_state.get('sub_questions', []))} sub-questions")
                print(f"[Workflow] Web results found: {len(final_state.get('web_search_results', []))}")
                print(f"[Workflow] KB results found: {len(final_state.get('kb_results', []))}")
            
            return {
                "type": "response",
                "response": final_state.get("final_response", "I apologize, but I couldn't generate a response."),
                "response_type": final_state.get("response_type", "unknown"),
                "confidence": final_state.get("response_confidence", 0.5),
                "sources_used": final_state.get("sources_used", []),
                "intent": final_state.get("current_intent"),
                "domain_relevance": final_state.get("domain_relevance"),
                "enhanced_question": final_state.get("enhanced_question"),
                "sub_questions": final_state.get("sub_questions", []),
                "web_queries": final_state.get("web_queries", []),
                "web_search_results": final_state.get("web_search_results", []),
                "scraped_content": final_state.get("scraped_content", {}),
                "url_confidence_scores": final_state.get("url_confidence_scores", {}),
                "kb_results": final_state.get("kb_results", []),
                "retrieval_status": final_state.get("retrieval_status", {}),
                "iterations": final_state.get("iteration_count", 0)
            }
                
        except Exception as e:
            print(f"[Workflow] Workflow execution error: {e}")
            import traceback
            traceback.print_exc()
            
            # Emit error state
            await emit_error(thread_id, "An error occurred while processing your request")
            
            return {
                "type": "error",
                "message": "I encountered an issue processing your request. Could you please rephrase your question?",
                "error_details": str(e)
            }
    
    async def _trigger_educational_agent_if_needed(self, final_state: Dict[str, Any]):
        """Trigger educational agent for appropriate response types (non-blocking)"""
        try:
            response_type = final_state.get("response_type")
            domain_relevance = final_state.get("domain_relevance")
            
            # Trigger conditions: general questions or encouragement responses
            should_trigger = (
                response_type in ["general_encouragement", "clarification"] or 
                domain_relevance == "general"
            )
            
            if not should_trigger:
                print(f"[Workflow] Educational agent not triggered - response_type: {response_type}, domain_relevance: {domain_relevance}")
                return
            
            print(f"[Workflow] Triggering educational agent for response_type: {response_type}")
            
            # Import and trigger educational agent
            from .educational_agent import get_educational_agent
            educational_agent = get_educational_agent()
            
            # Prepare context with memory information
            user_context = {
                "user_id": final_state.get("user_id"),
                "query": final_state.get("user_query", ""),
                "response_type": response_type,
                "memory_context": final_state.get("memory_context", {})
            }
            
            # Trigger educational content generation
            await educational_agent.process_educational_trigger(
                user_id=final_state.get("user_id"),
                user_query=final_state.get("user_query", ""),
                response_type=response_type,
                conversation_history=final_state.get("history", [])
            )
            
            print("[Workflow] Educational agent triggered successfully")
            
        except Exception as e:
            print(f"[Workflow] Error triggering educational agent: {e}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow system status"""
        return {
            "workflow_initialized": self.graph is not None,
            "memory_manager_active": self.memory_manager is not None,
            "agents_initialized": {
                "intention_extractor": self.intention_extractor.client is not None,
                "question_enhancer": self.question_enhancer.llm is not None,
                "question_decomposer": self.question_decomposer.llm is not None,
                "re_evaluator": self.re_evaluator.llm is not None,
                "parallel_retriever": self.parallel_retriever is not None
            },
            "configuration": {
                "max_iterations": settings.max_iterations,
                "max_concurrent_users": settings.max_concurrent_users,
                "vector_db_path": settings.vector_db_path,
                "openai_model": settings.openai_model,
                "has_openai_key": bool(settings.openai_api_key)
            },
            "web_search": {
                "tavily_configured": bool(settings.tavily_api_key),
                "jina_configured": bool(settings.jina_api_key),
                "max_results": settings.web_search_max_results,
                "token_limit": settings.web_scraping_token_limit,
                "timeout": settings.web_search_timeout
            }
        }