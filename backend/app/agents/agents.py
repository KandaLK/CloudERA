"""
Individual Agent Implementations

Four core agents:
1. IntentionExtractor - Extracts and clarifies user intentions
2. QuestionEnhancer - Enhances and simplifies extracted intents
3. QuestionDecomposer - Decomposes questions into sub-questions and web queries
4. ReEvaluator - Validates and provides feedback on agent outputs
"""

import asyncio
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from openai import OpenAI

from app.core.config import settings
from .models import IntentExtractionResult, QuestionEnhancement, QuestionDecomposition, ValidationResult, WebSearchResultEvaluation, ResponseGeneration, URLRelevanceEvaluation
from .web_search import WebSearchService
from .knowledge_base_retrieval import get_knowledge_base_retriever


class IntentionExtractor:
    """Extracts and clarifies user intentions"""
    
    def __init__(self):
        print("[IntentionExtractor] Initializing intention extraction agent")
        if settings.deepseek_api_key:
            self.client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
            self.parser = PydanticOutputParser(pydantic_object=IntentExtractionResult)
        else:
            print("[IntentionExtractor] Warning: No DeepSeek API key available")
            self.client = None
            self.parser = None
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[IntentionExtractor] Processing query: {state['user_query'][:50]}...")
        
        if not self.client:
            print("[IntentionExtractor] Falling back to simple intent extraction")
            # Fallback behavior
            state["current_intent"] = state["user_query"]
            state["needs_clarification"] = False
            state["clarification_question"] = None
            state["confidence_score"] = 0.5
            return state
        
        
        try:
            # Format the prompt with the data
            prompt_text = f"""
            You are an expert intent analyzer for user queries in a conversational AI system focused on cloud services and related technical topics. Your task is to deeply understand the user's true intention behind their query by analyzing the thinking process implied in their words and the conversation history, rather than just keywords. Do not perform superficial keyword matching; instead, reason step by step about the user's likely goals, context from prior exchanges, any implied needs, and how the query fits into ongoing dialogue.
            Input:

            User Query: {state["user_query"]}
            Conversation History: {str(state["history"][-6:])}

            Step-by-Step Reasoning Process:

            Review the Conversation History: Examine the last 6 exchanges to understand the context, flow, and any evolving topics. Consider how previous responses or questions might influence the current query's meaning.
            Infer True Intention: Think critically about what the user is really seeking. Break down the query's structure, tone, and implications. Ask yourself: What problem are they trying to solve? What outcome do they expect? How does this build on history? Avoid assumptions based on isolated words; focus on holistic reasoning.
            Classify Relevance Type: Based on the inferred intention, classify into one of these categories:

            domain: If the intention involves cloud service-related topics (e.g., AWS, Azure, GCP services), simple network topics (e.g., basic networking concepts like IP, subnets), data security (e.g., encryption, access controls), cloud security (e.g., IAM, firewalls in cloud), troubleshooting cloud service issues (e.g., deployment failures, connectivity problems), or identifying errors specifically in these areas.
            general: If the intention is outside the domain topics, such as general knowledge questions, greetings (e.g., "Hi", "How are you?", "Thanks"), misuse of system prompts/commands, paraphrasing, grammar checking, writing requests unrelated to domain, or generating/solving/debugging code in any programming language (except Linux/Windows CLI, AWS/Azure CLI commands).


            Assess Confidence Level: Evaluate your confidence in the intention extraction and classification:

            HIGH: Clear, unambiguous intention with strong alignment to history.
            MEDIUM: Reasonable inference but some ambiguity.
            LOW: Unclear, vague, or conflicting signals (e.g., misspellings, unidentified content).


            Determine Clarification Need: If confidence is LOW or the query has misspelled/unidentified content making intention hard to discern, set clarification_needed=true. Otherwise, set to false.
            Generate Clarification Question (if needed): If clarification_needed=true, create one concise, helpful question to guide the user toward clarifying their intent. This question must encourage them to rephrase in terms of domain topics (e.g., cloud services, security, troubleshooting) if possible, helping them express a clearer idea without leading too much.
                        
            {self.parser.get_format_instructions()}
            """
            
            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.5
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            result = self.parser.parse(response_text)
            
            # Handle both dict and object responses defensively
            if isinstance(result, dict):
                print("[IntentionExtractor] Warning: Received dict instead of Pydantic object, handling gracefully")
                intent = result.get("intent", state["user_query"])
                confidence = result.get("confidence", "low") 
                domain_relevance = result.get("domain_relevance", "followup")
                clarification_needed = result.get("clarification_needed", True)
                clarification_question = result.get("clarification_question", "Could you please provide more details about what you're trying to accomplish ?")
            else:
                intent = result.intent
                confidence = result.confidence
                domain_relevance = result.domain_relevance
                clarification_needed = result.clarification_needed
                clarification_question = result.clarification_question
            
            print(f"[IntentionExtractor] Extracted intent: {intent}")
            print(f"[IntentionExtractor] Confidence: {confidence}")
            print(f"[IntentionExtractor] Domain relevance: {domain_relevance}")
            print(f"[IntentionExtractor] Needs clarification: {clarification_needed}")
            
            # Update state
            state["current_intent"] = intent
            state["domain_relevance"] = domain_relevance
            state["needs_clarification"] = clarification_needed
            state["clarification_question"] = clarification_question
            state["confidence_score"] = 0.9 if confidence == "high" else 0.6 if confidence == "medium" else 0.3
            
            return state
            
        except Exception as e:
            print(f"[IntentionExtractor] Error during intent extraction: {e}")
            # Fallback
            state["current_intent"] = state["user_query"]
            state["domain_relevance"] = "followup"  # Default to followup on error
            state["needs_clarification"] = True
            state["clarification_question"] = "Could you please provide more details about what you're trying to accomplish ? I can help you !"
            state["confidence_score"] = 0.2
            return state


class QuestionEnhancer:
    """Enhances and simplifies extracted intents into clear questions"""
    
    def __init__(self):
        print("[QuestionEnhancer] Initializing question enhancement agent")
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model, 
                temperature=0,
                api_key=settings.openai_api_key
            )
            self.parser = PydanticOutputParser(pydantic_object=QuestionEnhancement)
        else:
            print("[QuestionEnhancer] Warning: No OpenAI API key available")
            self.llm = None
            self.parser = None
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if not state["current_intent"]:
            print("[QuestionEnhancer] No intent to enhance, skipping")
            return state
            
        print(f"[QuestionEnhancer] Enhancing intent: {state['current_intent'][:50]}...")
        
        # Check if we have feedback to incorporate
        feedback_context = ""
        if state.get("evaluator_feedback") and state.get("revision_instructions"):
            feedback_context = f"""
        
        PREVIOUS FEEDBACK FROM EVALUATOR:
        {state["evaluator_feedback"]}
        
        IMPROVEMENT INSTRUCTIONS:
        {state["revision_instructions"]}
        
        Please incorporate this feedback to improve your enhancement approach.
        """
        
        prompt = ChatPromptTemplate.from_template("""
        You are a question enhancement specialist for cloud services (AWS, Azure), network configuration, Data Security and compliance security, or troubleshooting. Transform the extracted intent into a clear, actionable question.
        
        Extracted Intent: {intent}
        Memory Context: {memory_context}
        {feedback_context}
        
        Instructions:
        1. Rewrite the intent as a focused, unambiguous question about cloud services, network configuration, Data Security and compliance security, or troubleshooting
        2. Make it specific and actionable for related topic contexts
        3. Consider the user's expertise level and preferences from memory
        4. Keep it concise but complete
        5. Remove any ambiguity or vagueness
        6. If feedback is provided above, carefully incorporate those improvements
        7. Avoid halucination an keep the question simple align with user actual intention
        
                                                  
        Examples:
        - Intent: "having issues with cloud setup" → Enhanced: "How do I troubleshoot cloud infrastructure deployment issues in AWS/Azure ?"
        - Intent: "need help with database performance" → Enhanced: "What are the steps to optimize database query performance in cloud environments?"
        - Intent: "security concerns" → Enhanced: "What are the best practices for securing cloud infrastructure and network configurations?"
        
        {format_instructions}
        """)
        
        try:
            chain = prompt | self.llm | self.parser
            result = chain.invoke({
                "intent": state["current_intent"],
                "memory_context": state["memory_context"].get("ltm_summary", ""),
                "feedback_context": feedback_context,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Handle both dict and object responses defensively
            if isinstance(result, dict):
                print("[QuestionEnhancer] Warning: Received dict instead of Pydantic object, handling gracefully")
                enhanced_question = result.get("enhanced_question", state["current_intent"])
            else:
                enhanced_question = result.enhanced_question
                
            print(f"[QuestionEnhancer] Enhanced question: {enhanced_question}")
            state["enhanced_question"] = enhanced_question
            return state
            
        except Exception as e:
            print(f"[QuestionEnhancer] Error during question enhancement: {e}")
            # Fallback
            state["enhanced_question"] = state["current_intent"]
            return state


class QuestionDecomposer:
    """Decomposes enhanced questions into sub-questions and web queries"""
    
    def __init__(self):
        print("[QuestionDecomposer] Initializing question decomposition agent")
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model, 
                temperature=0.1,
                api_key=settings.openai_api_key
            )
            self.parser = PydanticOutputParser(pydantic_object=QuestionDecomposition)
        else:
            print("[QuestionDecomposer] Warning: No OpenAI API key available")
            self.llm = None
            self.parser = None
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if not state["enhanced_question"]:
            print("[QuestionDecomposer] No enhanced question to decompose, skipping")
            return state
            
        print(f"[QuestionDecomposer] Decomposing question: {state['enhanced_question'][:50]}...")
        
        prompt = ChatPromptTemplate.from_template("""
        You are a question decomposition specialist. Break down the enhanced question into comprehensive sub-questions and web queries for optimal context retrieval.
        
        ENHANCED QUESTION: {question}
        USER INTENT: {intent}
        USER PREFERENCES & EXPERTISE: {memory_context}
        
        INSTRUCTIONS:
        1. Use the Enhanced Question and User Intent as your primary inputs
        2. Create sub-questions that cover broader areas related to the question for comprehensive context retrieval
        3. Sub-questions should describe more areas related to the topic to help retrieve relevant information
        4. Web queries must cover sub-question details and user question needs for better content retrieval
        5. Focus on being helpful for retrieving more relevant content to answer the enhanced question
        
        SUB-QUESTION CREATION:
        - Derive from enhanced question and user intent
        - Cover broader related areas to capture comprehensive context
        - Consider user's expertise level and platform preferences
        - Make them descriptive to help with information retrieval
        - Generate 2-4 sub-questions that expand coverage of the topic
        
        WEB QUERY CREATION:
        - Must cover sub-question details comprehensively
        - Target user question needs specifically
        - Help retrieve more relevant content for the enhanced question
        - Use specific technical terms and context from enhanced question
        - Generate 2-3 focused web queries for optimal content retrieval
        
        {format_instructions}
        """)
        
        try:
            chain = prompt | self.llm | self.parser
            result = chain.invoke({
                "question": state["enhanced_question"],
                "intent": state["current_intent"],
                "memory_context": state["memory_context"].get("ltm_summary", ""),
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Handle both dict and object responses defensively
            if isinstance(result, dict):
                print("[QuestionDecomposer] Warning: Received dict instead of Pydantic object, handling gracefully")
                sub_questions = result.get("sub_questions", [state["enhanced_question"]])
                sub_question_reasoning = result.get("sub_question_reasoning", ["Default reasoning"])
                web_queries = result.get("web_queries", [state["enhanced_question"]])
                reasoning = result.get("reasoning", "Default decomposition")
            else:
                sub_questions = result.sub_questions
                sub_question_reasoning = result.sub_question_reasoning
                web_queries = result.web_queries
                reasoning = result.reasoning
            
            print(f"[QuestionDecomposer] Generated {len(sub_questions)} sub-questions:")
            for i, (sq, reasoning_text) in enumerate(zip(sub_questions, sub_question_reasoning), 1):
                print(f"  {i}. {sq}")
                print(f"     → Reasoning: {reasoning_text}")
            
            print(f"[QuestionDecomposer] Generated {len(web_queries)} web queries:")
            for i, wq in enumerate(web_queries, 1):
                print(f"  {i}. {wq}")
            
            print(f"[QuestionDecomposer] Overall reasoning: {reasoning}")
            
            state["sub_questions"] = sub_questions
            state["web_queries"] = web_queries
            return state
            
        except Exception as e:
            print(f"[QuestionDecomposer] Error during question decomposition: {e}")
            # Fallback
            state["sub_questions"] = [state["enhanced_question"]]
            state["web_queries"] = [state["enhanced_question"]]
            return state


class ReEvaluator:
    """Enhances and improves sub-questions and web queries for better retrieval"""
    
    def __init__(self):
        print("[ReEvaluator] Initializing re-evaluation enhancement agent")
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model, 
                temperature=0.1,
                api_key=settings.openai_api_key
            )
            self.parser = PydanticOutputParser(pydantic_object=QuestionDecomposition)
        else:
            print("[ReEvaluator] Warning: No OpenAI API key available")
            self.llm = None
            self.parser = None
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[ReEvaluator] Enhancing sub-questions and web queries for better retrieval...")
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert question enhancement specialist. Analyze the current outputs, ONLY IF its need to enhanced then, generate enhanced versions of both sub-questions and web search queries for optimal content retrieval.
        
        ORIGINAL USER QUERY: {query}
        EXTRACTED INTENT: {intent}
        ENHANCED QUESTION: {enhanced_question}
        CURRENT SUB-QUESTIONS: {sub_questions}
        CURRENT WEB QUERIES: {web_queries}
        
        YOUR TASK:
        Evaluate the current outputs, ONLY If they need to enhanced then, create enhanced versions that will retrieve more comprehensive and relevant content.
        
        ENHANCEMENT CRITERIA:
        
        1. SUB-QUESTION ENHANCEMENT:
           - Make sub-questions more comprehensive to capture broader context
           - Ensure they cover different aspects needed to fully answer the enhanced question
           - Focus on areas that will help retrieve the most relevant information
           - Expand coverage while maintaining focus on the enhanced question
        
        2. WEB QUERY ENHANCEMENT:
           - Create more specific and targeted web search queries
           - Use technical terminology that will find high-quality sources
           - Include variations and synonyms for better search coverage
           - Focus on finding authoritative and current information
           - Ensure queries will retrieve content that addresses user needs comprehensively
        
        INSTRUCTIONS:
        1. Analyze the current sub-questions and web queries
        2. Identify areas for improvement in terms of coverage and specificity
        3. Generate enhanced sub-questions (2-4) that provide better context retrieval
        4. Generate enhanced web queries (2-3) that will find more relevant content
        5. Focus on practical improvements without hallucination
        
        OUTPUTS:
        - ONLY Enhanced sub-questions that improve information retrieval scope
        - ONLY Enhanced web search queries that target relevant content better

        
        {format_instructions}
        """)
        
        try:
            chain = prompt | self.llm | self.parser
            result = chain.invoke({
                "query": state["user_query"],
                "intent": state["current_intent"],
                "enhanced_question": state["enhanced_question"],
                "sub_questions": "\n".join([f"- {sq}" for sq in state["sub_questions"]]),
                "web_queries": "\n".join([f"- {wq}" for wq in state["web_queries"]]),
                "memory_context": state["memory_context"].get("ltm_summary", "No user context available"),
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Handle both dict and object responses defensively
            if isinstance(result, dict):
                print("[ReEvaluator] Warning: Received dict instead of Pydantic object, handling gracefully")
                enhanced_sub_questions = result.get("sub_questions", state["sub_questions"])
                enhanced_web_queries = result.get("web_queries", state["web_queries"])
                reasoning = result.get("reasoning", "Enhanced outputs generated")
            else:
                enhanced_sub_questions = result.sub_questions
                enhanced_web_queries = result.web_queries
                reasoning = result.reasoning
            
            print(f"[ReEvaluator] ============ ENHANCEMENT RESULT ============")
            print(f"[ReEvaluator] Original Sub-questions: {len(state['sub_questions'])}")
            for i, sq in enumerate(state["sub_questions"], 1):
                print(f"  {i}. {sq}")
            print(f"[ReEvaluator] Enhanced Sub-questions: {len(enhanced_sub_questions)}")
            for i, sq in enumerate(enhanced_sub_questions, 1):
                print(f"  {i}. {sq}")
            
            print(f"[ReEvaluator] Original Web queries: {len(state['web_queries'])}")
            for i, wq in enumerate(state["web_queries"], 1):
                print(f"  {i}. {wq}")
            print(f"[ReEvaluator] Enhanced Web queries: {len(enhanced_web_queries)}")
            for i, wq in enumerate(enhanced_web_queries, 1):
                print(f"  {i}. {wq}")
            
            print(f"[ReEvaluator] Enhancement reasoning: {reasoning}")
            print(f"[ReEvaluator] ============================================")
            
            # Update state with enhanced outputs
            state["sub_questions"] = enhanced_sub_questions
            state["web_queries"] = enhanced_web_queries
            
            # Remove revision-related fields since we don't loop anymore
            state["needs_revision"] = False
            state["revision_target"] = None
            
            return state
            
        except Exception as e:
            print(f"[ReEvaluator] Error during enhancement: {e}")
            # Fallback - proceed with original outputs
            state["needs_revision"] = False
            state["revision_target"] = None
            return state




class ParallelRetriever:
    """Executes both knowledge base and web search retrieval in parallel"""
    
    def __init__(self):
        print("[ParallelRetriever] Initializing parallel retrieval agent")
        self.web_service = WebSearchService()
        self.kb_retriever = None  # Will be initialized on first use
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute both knowledge base and web search retrieval in parallel"""
        print("[ParallelRetriever] Starting parallel retrieval process")
        
        try:
            # Get questions for both retrieval systems
            sub_questions = state.get("sub_questions", [])
            web_queries = state.get("web_queries", [])
            
            print(f"[ParallelRetriever] Sub-questions for KB: {len(sub_questions)}")
            print(f"[ParallelRetriever] Web queries: {len(web_queries)}")
            
            # Initialize knowledge base retriever if needed
            if self.kb_retriever is None:
                self.kb_retriever = await get_knowledge_base_retriever()
            
            # Prepare tasks for parallel execution
            tasks = []
            task_names = []
            
            # Add knowledge base retrieval task
            if sub_questions and self.kb_retriever.initialized:
                tasks.append(self._retrieve_knowledge_base(sub_questions))
                task_names.append("knowledge_base")
                state["retrieval_status"]["knowledge_base"] = "running"
            else:
                print("[ParallelRetriever] Skipping KB retrieval - no questions or not initialized")
                state["kb_results"] = []
                state["retrieval_status"]["knowledge_base"] = "skipped"
            
            # Always add web search task (no decision needed)
            if web_queries:
                tasks.append(self._retrieve_web_search(web_queries, state))
                task_names.append("web_search")
                state["retrieval_status"]["web_search"] = "running"
            else:
                print("[ParallelRetriever] Skipping web search - no queries")
                state["web_search_results"] = []
                state["scraped_content"] = {}
                state["url_confidence_scores"] = {}
                state["retrieval_status"]["web_search"] = "skipped"
            
            # Execute tasks in parallel
            if tasks:
                print(f"[ParallelRetriever] Executing {len(tasks)} retrieval tasks in parallel")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    task_name = task_names[i]
                    if isinstance(result, Exception):
                        print(f"[ParallelRetriever] Error in {task_name}: {result}")
                        state["retrieval_status"][task_name] = "error"
                        if task_name == "knowledge_base":
                            state["kb_results"] = []
                        elif task_name == "web_search":
                            state["web_search_results"] = []
                            state["scraped_content"] = {}
                            state["url_confidence_scores"] = {}
                    else:
                        print(f"[ParallelRetriever] {task_name} completed successfully")
                        state["retrieval_status"][task_name] = "completed"
                        
                        # Update state with results
                        if task_name == "knowledge_base":
                            state["kb_results"] = result
                        elif task_name == "web_search":
                            # Update state with enhanced web search results
                            state["web_search_results"] = result.get("search_results", [])
                            state["scraped_content"] = result.get("scraped_content", {})
                            state["url_confidence_scores"] = result.get("url_confidence_scores", {})
            
            # Combine all sources
            all_sources = []
            
            # Add KB results
            for kb_result in state.get("kb_results", []):
                if kb_result.get("success") and kb_result.get("answer"):
                    all_sources.append({
                        "source_type": "knowledge_base",
                        "content": kb_result["answer"],
                        "question": kb_result["question"],
                        "metadata": kb_result.get("metadata", {})
                    })
            
            # Add web search results
            for web_result in state.get("web_search_results", []):
                all_sources.append({
                    "source_type": "web_search",
                    "content": web_result.get("description", ""),
                    "title": web_result.get("title", ""),
                    "url": web_result.get("url", ""),
                    "metadata": {"score": web_result.get("score", 0)}
                })
            
            # Add scraped content
            for url, content in state.get("scraped_content", {}).items():
                all_sources.append({
                    "source_type": "scraped_content",
                    "content": content,  # Use full content for comprehensive context
                    "url": url,
                    "metadata": {"type": "scraped"}
                })
            
            state["all_sources"] = all_sources
            
            print(f"[ParallelRetriever] Retrieval complete:")
            print(f"  - KB results: {len(state.get('kb_results', []))}")
            print(f"  - Web results: {len(state.get('web_search_results', []))}")
            print(f"  - Scraped pages: {len(state.get('scraped_content', {}))}")
            print(f"  - Combined sources: {len(all_sources)}")
            
            return state
            
        except Exception as e:
            print(f"[ParallelRetriever] Error in parallel retrieval: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback - ensure all fields are set
            state["kb_results"] = []
            state["web_search_results"] = []
            state["scraped_content"] = {}
            state["url_confidence_scores"] = {}
            state["all_sources"] = []
            state["retrieval_status"] = {"knowledge_base": "error", "web_search": "error"}
            
            return state
    
    async def _retrieve_knowledge_base(self, sub_questions: List[str]) -> List[Dict[str, Any]]:
        """Retrieve information from knowledge base"""
        print(f"[ParallelRetriever] Querying knowledge base with {len(sub_questions)} questions")
        
        try:
            if self.kb_retriever and self.kb_retriever.initialized:
                results = await self.kb_retriever.query_multiple(sub_questions)
                successful_results = sum(1 for r in results if r.get("success"))
                print(f"[ParallelRetriever] KB retrieval: {successful_results}/{len(results)} successful")
                return results
            else:
                print("[ParallelRetriever] KB retriever not available")
                return []
        except Exception as e:
            print(f"[ParallelRetriever] KB retrieval error: {e}")
            return []
    
    async def _retrieve_web_search(self, web_queries: List[str], state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve information from enhanced web search with fallback"""
        print("[ParallelRetriever] Executing enhanced web search with enhanced question context")
        
        original_query = state["user_query"]
        enhanced_question = state.get("enhanced_question", original_query)
        sub_questions = state.get("sub_questions", [])
        
        print(f"[ParallelRetriever] Enhanced question: {enhanced_question}")
        print(f"[ParallelRetriever] Sub-questions: {len(sub_questions)}")
        
        try:
            # Use enhanced web search service with enhanced questions context
            search_results = await self.web_service.full_search_and_scrape(
                web_queries=web_queries[:3],  # Limit to 3 queries
                original_query=original_query,
                enhanced_question=enhanced_question,
                sub_questions=sub_questions,
                thread_id=state.get("thread_id", "unknown")
            )
            return search_results
        except Exception as e:
            print(f"[ParallelRetriever] Enhanced web search error: {e}")
            return {
                "search_results": [],
                "scraped_content": {},
                "url_confidence_scores": {},
                "status": "error",
                "error": str(e)
            }


class ResponseGenerator:
    """Generates final responses using all processed data and web search results"""
    
    def __init__(self):
        print("[ResponseGenerator] Initializing response generation agent")
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model, 
                temperature=0.3,  # Slightly more creative for response generation
                api_key=settings.openai_api_key
            )
            self.parser = PydanticOutputParser(pydantic_object=ResponseGeneration)
        else:
            print("[ResponseGenerator] Warning: No OpenAI API key available")
            self.llm = None
            self.parser = None
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final response based on all workflow data"""
        print("[ResponseGenerator] Generating final response...")
        
        # Extract thread language from state
        thread_language = state.get("thread_language", "ENG")
        print(f"[ResponseGenerator] Thread language: {thread_language}")
        
        # Handle different paths
        if state.get("needs_clarification"):
            return self._generate_clarification_response(state, thread_language)
        
        # Check if this is a domain-relevant question
        domain_relevance = state.get("domain_relevance", "unknown")
        if domain_relevance == "general":
            return await self._generate_general_domain_response(state, thread_language)
        
        # Generate domain response
        return await self._generate_domain_response(state, thread_language)
    
    def _generate_clarification_response(self, state: Dict[str, Any], thread_language: str = "ENG") -> Dict[str, Any]:
        """Generate clarification response with language awareness"""
        print(f"[ResponseGenerator] Generating clarification response for language: {thread_language}")
        
        clarification_question = state.get("clarification_question", 
            "Could you please provide more details about what you're trying to accomplish with your Question?")
        
        # For Sinhala threads, use a different clarification approach
        if thread_language == "SIN":
            clarification_question = state.get("clarification_question", 
                "කරුණාකර ඔබගේ cloud infrastructure සම්බන්ධයෙන් ඔබ කළ යුතු දේ ගැන වැඩි විස්තර ලබා දෙන්න?")
        
        state["final_response"] = clarification_question
        state["response_type"] = "clarification"
        state["response_confidence"] = state.get("confidence_score", 0.5)
        state["sources_used"] = []
        
        return state
    
    async def _generate_general_domain_response(self, state: Dict[str, Any], thread_language: str = "ENG") -> Dict[str, Any]:
        """Generate intelligent response for general questions using prompt template and trigger educational agent"""
        print(f"[ResponseGenerator] Generating general domain response for language: {thread_language}")
        
        # Trigger educational agent asynchronously (non-blocking)
        asyncio.create_task(self._trigger_educational_agent(state))
        
        # Get user context and memory
        user_query = state.get("user_query", "")
        memory_context = state.get("memory_context", {})
        ltm_summary = memory_context.get("ltm_summary", "No previous interaction history")
        
        # Use English prompt template (simplified)
        if thread_language == "SIN" or "ENG":

            prompt = ChatPromptTemplate.from_template("""
            You are Cloud ERA, a specialized AI assistant for cloud services and network infrastructure. Analyze the user's query and provide an intelligent response using ONLY the prompt template approach.

            User Query: "{user_query}"
            Thread Language: {thread_language}

            CRITICAL INSTRUCTIONS - Handle ALL logic through this prompt (no custom code logic):

            1. GREETING DETECTION & RESPONSE: 
               - If user query is a greeting (hello, hi, good morning,thank you etc.), respond with a polite greeting
               - For greetings, avoid other tasks and focus on welcoming the user

            2. DOMAIN EXPLANATION FOR NON-GREETINGS:
               - Explain that you specialize in cloud services and networking
               - List your expertise areas with examples
               - Describe how the chat threads work with specific examples

            3. CHAT THREAD DESCRIPTIONS (very important):
               - AWS Thread: Use this for Amazon Web Services questions 
               - Azure Thread: Use this for Microsoft Azure questions 
               - Smart Learner Thread: This thread provides personalized learning content and educational insights in Domain related topics

            RESPONSE FORMAT:
            - Start with appropriate greeting response OR domain explanation
            - Include thread usage examples with specific services
            - End with encouragement to ask domain-related questions
            - Keep response friendly, informative, and actionable
            - If User Question is in Sinhala Response must be in Sinhala
            - If user Question is in English Response must be in English

            Generate the response now:
            """)
        
        try:
            chain = prompt | self.llm
            result = await chain.ainvoke({
                "user_query": user_query,
                "ltm_summary": ltm_summary,
                "thread_language": thread_language
            })
            
            response = result.content.strip()
            
            print(f"[ResponseGenerator] Generated prompt-based general response: {len(response)} characters")
            
            state["final_response"] = response
            state["response_type"] = "general_encouragement"
            state["response_confidence"] = 1.0
            state["sources_used"] = []
            
            return state
            
        except Exception as e:
            print(f"[ResponseGenerator] Error generating prompt-based general response: {e}")
            # Simple fallback
            if thread_language == "SIN":
                response = "මම cloud services සහ network infrastructure සඳහා විශේෂඥයෙක්. ඔබේ ප්‍රශ්නය අසන්න!"
            else:
                response = "I specialize in cloud services and network infrastructure. How can I help you?"
            
            state["final_response"] = response
            state["response_type"] = "general_encouragement"
            state["response_confidence"] = 0.6
            state["sources_used"] = []
            return state
    
    def _print_response_context(self, state: Dict[str, Any]) -> None:
        """Print comprehensive context before final response generation"""
        print(f"[ResponseGenerator] ENHANCED QUESTION:")
        print(f"[ResponseGenerator]    {state.get('enhanced_question', 'None')}")
        print(f"[ResponseGenerator] ")
        
        print(f"[ResponseGenerator] USER MEMORY CONTEXT:")
        memory_context = state.get("memory_context", {})
        ltm_summary = memory_context.get("ltm_summary", "No user preferences/expertise stored")
        print(f"[ResponseGenerator]    {ltm_summary}")
        print(f"[ResponseGenerator] ")
        
        print(f"[ResponseGenerator] SUB-QUESTIONS (from decomposition):")
        sub_questions = state.get("sub_questions", [])
        if sub_questions:
            for i, sq in enumerate(sub_questions, 1):
                print(f"[ResponseGenerator]    {i}. {sq}")
        else:
            print(f"[ResponseGenerator]    No sub-questions generated")
        print(f"[ResponseGenerator] ")
        
        print(f"[ResponseGenerator] KNOWLEDGE BASE RESULTS:")
        kb_results = state.get("kb_results", [])
        successful_kb = sum(1 for r in kb_results if r.get("success"))
        print(f"[ResponseGenerator]    KB queries: {len(kb_results)}")
        print(f"[ResponseGenerator]    Successful KB results: {successful_kb}")
        if kb_results:
            for i, kb_result in enumerate(kb_results[:3], 1):  # Show first 3
                status = "SUCCESS" if kb_result.get("success") else "FAILED"
                print(f"[ResponseGenerator]    {i}. {status} {kb_result['question'][:60]}...")
        print(f"[ResponseGenerator] ")
        
        print(f"[ResponseGenerator] WEB SEARCH RESULTS:")
        web_search_results = state.get("web_search_results", [])
        scraped_content = state.get("scraped_content", {})
        web_results_count = len(state.get("web_search_results", []))
        
        print(f"[ResponseGenerator]    Web results found: {web_results_count}")
        print(f"[ResponseGenerator]    Search results found: {len(web_search_results)}")
        print(f"[ResponseGenerator]    Pages scraped: {len(scraped_content)}")
        
        if web_search_results:
            print(f"[ResponseGenerator]    Search results:")
            for i, result in enumerate(web_search_results[:3], 1):
                print(f"[ResponseGenerator]      {i}. {result.get('title', 'No title')}")
                print(f"[ResponseGenerator]         URL: {result.get('url', 'No URL')}")
                print(f"[ResponseGenerator]         Score: {result.get('score', 0.0)}")
        
        if scraped_content:
            print(f"[ResponseGenerator]    Scraped content:")
            for i, (url, content) in enumerate(list(scraped_content.items())[:2], 1):
                content_preview = content[:150] + "..." if len(content) > 150 else content
                print(f"[ResponseGenerator]      {i}. URL: {url}")
                print(f"[ResponseGenerator]         Length: {len(content)} characters")
                print(f"[ResponseGenerator]         Preview: {content_preview}")
        
        print(f"[ResponseGenerator] ")
        print(f"[ResponseGenerator] WORKFLOW METADATA:")
        print(f"[ResponseGenerator]    Iterations completed: {state.get('iteration_count', 0)}")
        print(f"[ResponseGenerator]    Re-evaluator iterations: {state.get('re_evaluator_iterations', 0)}")
        print(f"[ResponseGenerator]    Confidence score: {state.get('confidence_score', 0.0)}")
        print(f"[ResponseGenerator] ")
        print(f"[ResponseGenerator] NOW GENERATING FINAL RESPONSE...")
        print(f"[ResponseGenerator] ================================================================")
    
    async def _generate_domain_response(self, state: Dict[str, Any], thread_language: str = "ENG") -> Dict[str, Any]:
        """Generate comprehensive domain response using all processed data"""
        print("[ResponseGenerator] ================ FINAL RESPONSE GENERATION ================")
        
        # Print detailed context before generating response
        self._print_response_context(state)
        
        # Prepare context from workflow
        intent = state.get("current_intent", "")
        enhanced_question = state.get("enhanced_question", "")
        sub_questions = state.get("sub_questions", [])
        web_search_results = state.get("web_search_results", [])
        scraped_content = state.get("scraped_content", {})
        kb_results = state.get("kb_results", [])
        all_sources = state.get("all_sources", [])
        
        # Prepare combined content summary
        content_summary = ""
        sources_used = []
        
        # Prepare knowledge base content summary
        if kb_results:
            content_summary += "\n\nKNOWLEDGE BASE RESULTS:\n"
            for kb_result in kb_results:
                if kb_result.get("success") and kb_result.get("answer"):
                    sources_used.append(f"Knowledge Base: {kb_result['question']}")
                    content_summary += f"Question: {kb_result['question']}\n"
                    content_summary += f"Answer: {kb_result['answer']}\n\n"
        
        # Prepare web search content summary
        if scraped_content:
            content_summary += "\n\nWEB SEARCH RESULTS:\n"
            for url, content in scraped_content.items():
                sources_used.append(url)
                # Use full content instead of truncating to provide complete context
                summary = content
                content_summary += f"Source: {url}\nContent: {summary}\n\n"
        
        if web_search_results and not scraped_content:
            content_summary += "\n\nWEB SEARCH RESULTS:\n"
            for result in web_search_results[:3]:
                sources_used.append(result.get("url", ""))
                content_summary += f"Title: {result.get('title', '')}\n"
                content_summary += f"URL: {result.get('url', '')}\n"
                content_summary += f"Description: {result.get('description', '')}\n\n"
        
        # Add language instruction for Sinhala threads
        language_instruction = ""
        if thread_language == "SIN":
            language_instruction = "\n\nIMPORTANT: Provide your response ONLY in Sinhala language."
        
        prompt = ChatPromptTemplate.from_template(f"""
        You are a specialized Cloud Services and Network Infrastructure assistant. Generate a comprehensive response using ONLY the provided sources and context.

        User's Original Question: {{original_query}}
        Extracted Intent: {{intent}}
        Enhanced Question: {{enhanced_question}}
        
        Sub-questions to address:
        {{sub_questions}}
        
        AVAILABLE CONTEXT SOURCES:
        {{content_sources}}
        
        CRITICAL CONTEXT-ONLY RESTRICTIONS:
        1. **ONLY USE PROVIDED CONTEXT**: Base your response EXCLUSIVELY on the knowledge base results and web search results provided above. Do NOT use general knowledge or information not present in the provided sources.
        
        2. **INSUFFICIENT CONTEXT HANDLING**: If the provided context does not contain enough information to answer the question comprehensively, explicitly state: "Based on the available information, I can provide the following..." and then note what additional information would be helpful.
        
        3. **SOURCE-BASED REASONING**: Every statement in your response must be traceable to the provided knowledge base results or web search content. If you cannot trace a fact to the provided sources, do not include it.
        
        4. **NO HALLUCINATION**: Do not add information about cloud platforms, services, or technical details that are not explicitly mentioned in the provided context sources.
        
        Response Instructions:
        1. Analyze the provided knowledge base and web search results carefully
        2. Use ONLY information found in these sources to construct your response
        3. Structure the response clearly with headings or bullet points where appropriate
        4. Cite which sources (knowledge base or specific URLs) provide each piece of information
        5. If the provided context lacks sufficient detail, acknowledge this limitation
        6. Address each sub-question area using only the available context
        7. If no relevant context is provided for a sub-question, state "The provided sources do not contain information about [specific topic]"
        
        Response format:
        - Start with a direct answer based on available context
        - Address each sub-question using only provided information
        - Include relevant examples or details ONLY if they appear in the sources
        - End with acknowledgment of any information gaps if context is insufficient
        - Always cite sources for major points (e.g., "According to the knowledge base..." or "Based on the web search results...")
        
        Remember: Your response quality depends on staying within the provided context boundaries rather than drawing from general knowledge.{language_instruction}
        
        {{format_instructions}}
        """)
        
        try:
            sub_questions_text = "\n".join([f"• {sq}" for sq in sub_questions])
            
            chain = prompt | self.llm | self.parser
            result = await chain.ainvoke({
                "original_query": state["user_query"],
                "intent": intent,
                "enhanced_question": enhanced_question,
                "sub_questions": sub_questions_text,
                "content_sources": content_summary,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Handle both dict and object responses
            if isinstance(result, dict):
                response = result.get("response", "I can help with your cloud and network question, but I need more specific details.")
                confidence = result.get("confidence", 0.7)
            else:
                response = result.response
                confidence = result.confidence
            
            # Simple language handling - no translation needed
            
            print(f"[ResponseGenerator] Generated response: {len(response)} characters")
            print(f"[ResponseGenerator] Using {len(sources_used)} total sources")
            print(f"[ResponseGenerator] - KB results: {len(kb_results)}")
            print(f"[ResponseGenerator] - Web results: {len(web_search_results)}")
            print(f"[ResponseGenerator] - Scraped pages: {len(scraped_content)}")
            
            state["final_response"] = response
            state["response_type"] = "domain_response"
            state["response_confidence"] = confidence
            state["sources_used"] = sources_used
            
            return state
            
        except Exception as e:
            print(f"[ResponseGenerator] Error generating response: {e}")
            print(f"[ResponseGenerator] Error type: {type(e).__name__}")
            print(f"[ResponseGenerator] Error details: {str(e)}")
            import traceback
            print(f"[ResponseGenerator] Traceback: {traceback.format_exc()}")
            raise
    
    async def _trigger_educational_agent(self, state: Dict[str, Any]):
        """Trigger educational agent for general questions (non-blocking)"""
        try:
            from .educational_agent import get_educational_agent
            educational_agent = get_educational_agent()
            
            # Extract necessary info
            user_id = state.get("user_id")
            user_query = state.get("user_query", "")
            history = state.get("history", [])
            memory_context = state.get("memory_context", {})
            
            # Trigger educational content generation with memory context
            await educational_agent.process_educational_trigger(
                user_id=user_id,
                user_query=user_query,
                response_type="general",
                conversation_history=history,
                memory_context=memory_context
            )
            
        except Exception as e:
            print(f"[ResponseGenerator] Error triggering educational agent: {e}")
    
    def _generate_debug_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate debug response showing all system data instead of LLM response"""
        print("[ResponseGenerator] Generating DEBUG response with all system data")
        
        # Extract all data from state
        user_query = state.get("user_query", "")
        enhanced_question = state.get("enhanced_question", "")
        current_intent = state.get("current_intent", "")
        sub_questions = state.get("sub_questions", [])
        web_queries = state.get("web_queries", [])
        
        # Knowledge base results
        kb_results = state.get("kb_results", [])
        
        # Web search results
        web_search_results = state.get("web_search_results", [])
        scraped_content = state.get("scraped_content", {})
        url_confidence_scores = state.get("url_confidence_scores", {})
        
        # Memory context
        memory_context = state.get("memory_context", {})
        conversation_history = state.get("history", [])
        
        # Build debug response
        debug_sections = []
        
        # 1. User Questions Section
        debug_sections.append("=== USER QUESTIONS ===")
        debug_sections.append(f"Original Question: {user_query}")
        debug_sections.append(f"Enhanced Question: {enhanced_question}")
        debug_sections.append(f"Extracted Intent: {current_intent}")
        debug_sections.append("")
        
        # 2. Sub-questions and Web Queries
        debug_sections.append("=== SUB-QUESTIONS & WEB QUERIES ===")
        debug_sections.append("Sub-questions from Decomposer:")
        if sub_questions:
            for i, sq in enumerate(sub_questions, 1):
                debug_sections.append(f"  {i}. {sq}")
        else:
            debug_sections.append("  (No sub-questions generated)")
        
        debug_sections.append("")
        debug_sections.append("Web Search Queries:")
        if web_queries:
            for i, wq in enumerate(web_queries, 1):
                debug_sections.append(f"  {i}. {wq}")
        else:
            debug_sections.append("  (No web queries generated)")
        debug_sections.append("")
        
        # 3. Knowledge Base Results
        debug_sections.append("=== KNOWLEDGE BASE RESULTS ===")
        if kb_results:
            for i, kb_result in enumerate(kb_results, 1):
                status = "SUCCESS" if kb_result.get("success") else "FAILED"
                debug_sections.append(f"KB Query {i}: {status}")
                debug_sections.append(f"  Question: {kb_result.get('question', 'N/A')}")
                if kb_result.get("success") and kb_result.get("answer"):
                    answer = kb_result["answer"][:200] + "..." if len(kb_result["answer"]) > 200 else kb_result["answer"]
                    debug_sections.append(f"  Answer: {answer}")
                else:
                    debug_sections.append(f"  Error: {kb_result.get('error', 'Unknown error')}")
                debug_sections.append("")
        else:
            debug_sections.append("(No knowledge base results)")
            debug_sections.append("")
        
        # 4. Enhanced Web Search Results
        debug_sections.append("=== ENHANCED WEB SEARCH RESULTS ===")
        debug_sections.append(f"Search Results Found: {len(web_search_results)}")
        debug_sections.append(f"Pages Scraped: {len(scraped_content)}")
        debug_sections.append(f"URLs with Confidence Scores: {len(url_confidence_scores)}")
        debug_sections.append("")
        
        if web_search_results:
            debug_sections.append("Search Results with Confidence Scores:")
            for i, result in enumerate(web_search_results, 1):  # Show ALL results
                url = result.get('url', 'No URL')
                confidence = url_confidence_scores.get(url, 0.0)
                debug_sections.append(f"  {i}. {result.get('title', 'No title')}")
                debug_sections.append(f"     URL: {url}")
                debug_sections.append(f"     Search Score: {result.get('score', 0.0):.3f}")
                debug_sections.append(f"     Confidence Score: {confidence:.3f}")
                description = result.get('description', '')[:150] + "..." if len(result.get('description', '')) > 150 else result.get('description', '')
                debug_sections.append(f"     Description: {description}")
                debug_sections.append("")
        
        # Show URL confidence ranking
        if url_confidence_scores:
            debug_sections.append("URL Confidence Ranking:")
            sorted_urls = sorted(url_confidence_scores.items(), key=lambda x: x[1], reverse=True)
            for i, (url, confidence) in enumerate(sorted_urls, 1):
                debug_sections.append(f"  {i}. Confidence {confidence:.3f}: {url}")
            debug_sections.append("")
        
        # 5. Scraped Web Content with Confidence
        if scraped_content:
            debug_sections.append("=== SCRAPED WEB CONTENT ===")
            for i, (url, content) in enumerate(scraped_content.items(), 1):
                confidence = url_confidence_scores.get(url, 0.0)
                debug_sections.append(f"Scraped Content {i} (Confidence: {confidence:.3f}):")
                debug_sections.append(f"  URL: {url}")
                content_preview = content[:300] + "..." if len(content) > 300 else content
                debug_sections.append(f"  Content: {content_preview}")
                debug_sections.append(f"  Total Length: {len(content)} characters")
                debug_sections.append("")
        
        # 6. Memory Context
        debug_sections.append("=== MEMORY CONTEXT ===")
        debug_sections.append("Short-term Memory (STM):")
        stm_summary = memory_context.get("stm_summary", "No STM summary available")
        debug_sections.append(f"  {stm_summary}")
        debug_sections.append("")
        
        debug_sections.append("Long-term Memory (LTM):")
        ltm_summary = memory_context.get("ltm_summary", "No LTM summary available")
        debug_sections.append(f"  {ltm_summary}")
        debug_sections.append("")
        
        # 7. Conversation History
        debug_sections.append("=== CONVERSATION HISTORY ===")
        if conversation_history:
            debug_sections.append(f"Recent messages ({len(conversation_history)} total):")
            for i, msg in enumerate(conversation_history[-3:], 1):  # Show last 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100] + "..." if len(msg.get('content', '')) > 100 else msg.get('content', '')
                debug_sections.append(f"  {i}. [{role.upper()}]: {content}")
        else:
            debug_sections.append("(No conversation history)")
        debug_sections.append("")
        
        # 8. Enhanced System Status
        debug_sections.append("=== ENHANCED SYSTEM STATUS ===")
        retrieval_status = state.get("retrieval_status", {})
        debug_sections.append(f"Knowledge Base Status: {retrieval_status.get('knowledge_base', 'unknown')}")
        debug_sections.append(f"Enhanced Web Search Status: {retrieval_status.get('web_search', 'unknown')}")
        debug_sections.append(f"Total Sources Combined: {len(state.get('all_sources', []))}")
        debug_sections.append(f"Tavily-JINA Fallback: Active")
        debug_sections.append(f"URL Confidence Evaluation: {'Active' if url_confidence_scores else 'No URLs evaluated'}")
        debug_sections.append(f"High Confidence URLs (>0.7): {sum(1 for score in url_confidence_scores.values() if score > 0.7)}")
        debug_sections.append("")
        
        # Combine all sections
        debug_response = "\n".join(debug_sections)
        
        # Set response in state
        state["final_response"] = debug_response
        state["response_type"] = "debug_response"
        state["response_confidence"] = 1.0
        # Include confidence scores in sources
        confidence_sources = [f"{url} (confidence: {url_confidence_scores.get(url, 0.0):.2f})" for url in scraped_content.keys()]
        kb_sources = [f"KB: {r.get('question', 'N/A')}" for r in kb_results if r.get("success")]
        state["sources_used"] = confidence_sources + kb_sources
        
        print(f"[ResponseGenerator] Debug response generated: {len(debug_response)} characters")
        
        return state