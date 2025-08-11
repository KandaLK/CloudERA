"""
Memory Management System for Multi-Agent Framework

Implements dual-layer memory:
- ShortTermMemory: ConversationSummaryBufferMemory with sliding window
- LongTermMemory: Vector database for persistent user knowledge
- MemoryManager: Coordinates both memory systems per user/thread
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import settings
from .models import LTMEntity, LTMEntityList


class ShortTermMemory:
    """Language-aware STM that handles both English and Sinhala threads with proper context"""
    
    def __init__(self, user_id: str, thread_id: str, thread_language: str = "ENG"):
        self.user_id = user_id
        self.thread_id = thread_id
        self.thread_language = thread_language
        print(f"[STM] Initializing language-aware STM for user {user_id}, thread {thread_id}, language: {thread_language}")
        
        # Setup STM context logger
        self._setup_stm_logger()
    
    def _setup_stm_logger(self):
        """Setup STM context logger for debugging and monitoring"""
        try:
            # Create logs directory if it doesn't exist
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Setup logger
            self.stm_logger = logging.getLogger(f"stm_context_{self.user_id}_{self.thread_id}")
            if not self.stm_logger.handlers:  # Avoid duplicate handlers
                self.stm_logger.setLevel(logging.INFO)
                
                # File handler with rotation
                handler = logging.FileHandler(os.path.join(log_dir, "stm_context.log"), encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
                handler.setFormatter(formatter)
                self.stm_logger.addHandler(handler)
                self.stm_logger.propagate = False
        except Exception as e:
            print(f"[STM] Warning: Could not setup STM logger: {e}")
            self.stm_logger = None
    
    def _log_stm_context(self, context: str):
        """Log STM context for debugging and monitoring"""
        if not self.stm_logger:
            return
        
        try:
            # Create context preview (first 200 characters)
            context_preview = context.replace('\n', ' ').replace('\r', ' ')
            if len(context_preview) > 1000:
                context_preview = context_preview[:1000] + "..."
            
            log_message = f"USER:{self.user_id} | THREAD:{self.thread_id} | LANG:{self.thread_language} | STM_CONTEXT: {context_preview}"
            self.stm_logger.info(log_message)
        except Exception as e:
            print(f"[STM] Warning: Could not log STM context: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (rough estimate: 4 chars per token)"""
        return len(text) // 4
    
    def _create_openai_summary(self, messages: List[str]) -> str:
        """
        Create intelligent summary of messages using OpenAI API
        Focuses on technical details and important information
        Token limit: 1500 tokens
        """
        if not messages:
            return "No messages to summarize"
        
        try:
            # Initialize OpenAI client for summarization
            if not settings.openai_api_key:
                print("[STM] No OpenAI API key available")
                return "No messages to summarize - OpenAI API key not configured"
            
            llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0.3,  # Lower temperature for consistent summaries
                api_key=settings.openai_api_key,
                max_tokens=1500  # Enforce 1500 token limit
            )
            
            # Create technical summarization prompt
            prompt = ChatPromptTemplate.from_template("""
You are summarizing conversation history for a cloud and security AI assistant. 
Create a concise summary that preserves the most important technical information.

CONVERSATION TO SUMMARIZE:
{messages}

INSTRUCTIONS:
- Focus on technical details, configurations, and specific solutions
- Preserve cloud service names, error messages, and troubleshooting steps
- Include important user preferences and decisions
- Maintain security-related discussions and concerns
- Keep code snippets and command examples if mentioned
- Ignore pleasantries and non-technical conversation
- Maximum length: 1500 tokens
- Format as a coherent paragraph summary

SUMMARY:""")
            
            # Combine messages into single text
            messages_text = "\n".join(messages)
            
            # Create the chain and invoke
            chain = prompt | llm
            response = chain.invoke({
                "messages": messages_text
            })
            
            summary = response.content.strip()
            return summary
            
        except Exception as e:
            print(f"[STM] OpenAI summarization failed: {e}")
            return "Failed to summarize messages - OpenAI API error"
    
    
    def get_context_from_messages(self, messages: List[Any], translated_history: str = None) -> str:
        """
        Get STM context from database messages with language awareness
        For Sinhala threads, uses translated_history if provided
        For English threads, processes messages normally
        """
        if not messages:
            return "No conversation history available"
        
        # For Sinhala threads, use translated history if available
        if self.thread_language == "SIN" and translated_history:
            print(f"[STM] Using translated history for Sinhala thread: {len(translated_history)} characters")
            self._log_stm_context(translated_history)
            return translated_history
        
        # For English threads or fallback, process messages normally
        print(f"[STM] Processing {len(messages)} messages for {self.thread_language} thread")
        
        # Get last 6 messages
        last_6_messages = messages[-6:] if len(messages) >= 6 else messages
        
        # Format messages for context
        formatted_messages = []
        total_tokens = 0
        
        for msg in last_6_messages:
            # Handle both Message objects and dictionary format
            if isinstance(msg, dict):
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
            else:
                # Handle Message objects
                role = "USER" if msg.author.value == "user" else "ASSISTANT"
                content = msg.content
            
            message_text = f"{role}: {content}"
            formatted_messages.append(message_text)
            total_tokens += self.count_tokens(message_text)
        
        context = "\n".join(formatted_messages)
        
        # Check if we exceed 6000 token limit
        if total_tokens > 6000:
            print(f"[STM] Token limit exceeded ({total_tokens} > 6000), summarizing first 3 messages with OpenAI")
            
            # Keep first 3 messages as is, summarize last 3
            first_3 = formatted_messages[:3]
            last_3 = formatted_messages[3:]
            
            # Create OpenAI-powered summary of first 3 messages
            first_3_summary = self._create_openai_summary(first_3)
            
            # Combine summarized history + last 3 messages for short-term memory
            context_parts = [f"SUMMARY: {first_3_summary}"] + last_3
            context = "\n".join(context_parts)
            
            print(f"[STM] Context after summarization: {self.count_tokens(context)} tokens")
        else:
            print(f"[STM] Context within token limit: {total_tokens} tokens")
        
        # Log the STM context
        self._log_stm_context(context)
        
        return context
    

class LongTermMemory:
    """Manages persistent user knowledge using vector database"""
    
    def __init__(self, persist_directory=None):
        self.persist_directory = persist_directory or settings.vector_db_path
        print(f"[LTM] Initializing LongTermMemory with path: {self.persist_directory}")
        
        # Initialize components
        if settings.openai_api_key:
            self.embedding_model = OpenAIEmbeddings(
                model="text-embedding-3-large",
                api_key=settings.openai_api_key
            )
            self.llm = ChatOpenAI(
                model=settings.openai_model, 
                temperature=0.5,
                api_key=settings.openai_api_key
            )
            
            # Initialize Chroma vector store
            try:
                self.db = Chroma(
                    collection_name="ltm_store",
                    embedding_function=self.embedding_model,
                    persist_directory=self.persist_directory
                )
                print("[LTM] ChromaDB initialized successfully")
            except Exception as e:
                print(f"[LTM] Error initializing ChromaDB: {e}")
                self.db = None
        else:
            print("[LTM] Warning: No OpenAI API key, LTM disabled")
            self.embedding_model = None
            self.llm = None
            self.db = None
    
    async def extract_entities(self, context: str) -> List[Dict]:
        """Use LLM to extract memory entities"""
        print(f"[LTM] Extracting entities from context: {len(context)} characters")
        parser = PydanticOutputParser(pydantic_object=LTMEntityList)
        
        prompt = ChatPromptTemplate.from_template("""
        Extract key entities from this conversation for long-term memory:
        
        {context}
        
        Instructions:
        - Identify user preferences, expertise levels, services mentioned, and important facts
        - Only extract information that would be useful for future conversations
        - Be selective - don't extract every detail
        - Return the results in the specified JSON format with an "entities" array
        
        Entity types:
        - preference: User's stated preferences and more interests or User personal details
        - service: Tools, platforms, or services the user more ask about or talked about
        - Knowledgegaps: Topics that users having issues, Security relted questions
        - Response: Preferd type of response, such as brief description, in point format and etc 
        
        {format_instructions}
        """)
        
        try:
            chain = prompt | self.llm | parser
            result = await chain.ainvoke({
                "context": context,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Extract entities from the wrapper object
            if hasattr(result, 'entities'):
                # Result is LTMEntityList object
                entity_objects = result.entities
            elif isinstance(result, dict) and 'entities' in result:
                # Result is dict with entities key
                entity_objects = result['entities']
            else:
                print(f"[LTM] Unexpected result structure: {type(result)}")
                return []
            
            # Convert entities to dictionaries
            entities = []
            for entity in entity_objects:
                if isinstance(entity, dict):
                    entities.append(entity)
                else:
                    # Convert Pydantic object to dict
                    entities.append(entity.dict() if hasattr(entity, 'dict') else entity.__dict__)
            
            print(f"[LTM] Extracted {len(entities)} entities")
            return entities
        except Exception as e:
            print(f"[LTM] Entity extraction error: {e}")
            return []
    
    async def _test_db_connection(self) -> bool:
        """Test if ChromaDB is accessible"""
        if not self.db:
            return False
        try:
            # Try a simple operation to test connection
            await asyncio.to_thread(
                self.db.similarity_search,
                query="test",
                k=1
            )
            return True
        except Exception as e:
            print(f"[LTM] Database connection test failed: {e}")
            return False
    
    async def _ensure_db_health(self) -> bool:
        """Ensure database is healthy before operations"""
        if not self.db:
            print("[LTM] No database available")
            return False
        
        try:
            # Quick health check with timeout
            is_healthy = await asyncio.wait_for(
                self._test_db_connection(),
                timeout=5.0
            )
            if not is_healthy:
                print("[LTM] Database health check failed")
            return is_healthy
        except asyncio.TimeoutError:
            print("[LTM] Database health check timed out")
            return False
        except Exception as e:
            print(f"[LTM] Database health check error: {e}")
            return False
    
    async def update_memory(self, user_id: str, thread_id: str, entities: List[Dict]):
        """Store entities in vector DB with metadata"""
        if not entities:
            print("[LTM] No entities to update")
            return
        
        # Check database health before attempting update
        if not await self._ensure_db_health():
            print("[LTM] Skipping memory update - database not healthy")
            return
            
        print(f"[LTM] Updating memory with {len(entities)} entities for user {user_id}")
        
        documents = []
        metadatas = []
        ids = []
        
        for i, entity in enumerate(entities):
            documents.append(entity["content"])
            metadatas.append({
                "user_id": user_id,
                "thread_id": thread_id,
                "type": entity["entity_type"],
                "confidence": entity["confidence"],
                "timestamp": datetime.now().isoformat(),
                "source": entity["source_context"][:100]
            })
            ids.append(f"{user_id}-{thread_id}-{datetime.now().timestamp()}-{i}")
        
        try:
            # Run blocking operation in thread pool
            await asyncio.to_thread(
                self.db.add_texts,
                texts=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[LTM] Successfully stored {len(documents)} entities")
        except Exception as e:
            print(f"[LTM] Memory update error: {e}")
    
    async def retrieve_memory(self, user_id: str, thread_id: str, query: str, k=5) -> List[Tuple]:
        """Retrieve relevant memories with similarity search"""
        # Check database health before attempting retrieval
        if not await self._ensure_db_health():
            print("[LTM] Skipping memory retrieval - database not healthy")
            return []
            
        print(f"[LTM] Retrieving memories for user {user_id}, query: {query[:50]}...")
        
        try:
            # Run blocking operation in thread pool
            results = await asyncio.to_thread(
                self.db.similarity_search,
                query=query,
                k=k,
                filter={"user_id": user_id}
            )
            memories = [(doc.page_content, doc.metadata) for doc in results]
            print(f"[LTM] Retrieved {len(memories)} relevant memories")
            return memories
        except Exception as e:
            print(f"[LTM] Memory retrieval error: {e}")
            return []


class MemoryManager:
    """Simplified memory management system"""
    
    def __init__(self):
        print("[MemoryManager] Initializing simplified memory management system")
        self.ltm = LongTermMemory()
        self.message_counters: Dict[str, int] = {}  # Track message count per user
        self.ltm_update_interval = 20  # Update LTM every 20 messages
        print(f"[MemoryManager] LTM update interval: {self.ltm_update_interval} messages")
    
    def get_stm_context(self, user_id: str, thread_id: str, messages: List[Any], thread_language: str = "ENG", translated_history: str = None) -> str:
        """Get STM context with language awareness and translated history support"""
        stm = ShortTermMemory(user_id, thread_id, thread_language)
        return stm.get_context_from_messages(messages, translated_history)
    
    async def process_message(self, user_id: str, thread_id: str, role: str, content: str, all_messages: List[Any], for_educational_agent: bool = False):
        """Process new message and handle LTM updates only for educational agent"""
        try:
            print(f"[MemoryManager] Processing message from {role} for {user_id}-{thread_id}, educational: {for_educational_agent}")
            
            # Only process LTM for educational agent
            if not for_educational_agent:
                print(f"[MemoryManager] Skipping LTM processing - not for educational agent")
                return
            
            # Track message count per user for educational agent only
            user_key = f"{user_id}-{thread_id}"
            self.message_counters[user_key] = self.message_counters.get(user_key, 0) + 1
            
            # Check if we need to update LTM (every 20 messages)
            if self.message_counters[user_key] % self.ltm_update_interval == 0:
                print(f"[MemoryManager] Triggering LTM update for educational agent at {self.message_counters[user_key]} messages")
                # Run LTM update in parallel (non-blocking)
                import asyncio
                asyncio.create_task(self._update_ltm_async(user_id, thread_id, all_messages))
        except Exception as e:
            print(f"[MemoryManager] Error processing message: {e}")
            # Don't propagate errors to avoid blocking main workflow
    
    async def _update_ltm_async(self, user_id: str, thread_id: str, messages: List[Any]):
        """Extract and store entities from recent messages (runs in parallel with timeout)"""
        try:
            print(f"[MemoryManager] Async LTM update for {user_id}-{thread_id}")
            
            # Get context from recent messages
            stm_context = self.get_stm_context(user_id, thread_id, messages)
            
            # Extract entities with timeout (30 seconds max)
            try:
                entities = await asyncio.wait_for(
                    self.ltm.extract_entities(stm_context), 
                    timeout=30.0
                )
                if entities:
                    # Update memory with timeout (15 seconds max)
                    await asyncio.wait_for(
                        self.ltm.update_memory(user_id, thread_id, entities),
                        timeout=15.0
                    )
                    print(f"[MemoryManager] LTM updated with {len(entities)} new entities")
                else:
                    print("[MemoryManager] No entities extracted for LTM")
            except asyncio.TimeoutError:
                print(f"[MemoryManager] LTM update timed out for {user_id}-{thread_id}")
            except Exception as ltm_error:
                print(f"[MemoryManager] LTM operation error: {ltm_error}")
                
        except Exception as e:
            print(f"[MemoryManager] Async LTM update error: {e}")
    
    async def get_context(self, user_id: str, thread_id: str, query: str, messages: List[Any], thread_language: str = "ENG", translated_history: str = None) -> Dict:
        """Get full memory context for agent with language awareness and fallback handling"""
        print(f"[MemoryManager] Getting full context for {user_id}-{thread_id}, language: {thread_language}")
        
        # Get STM context with language awareness
        stm_context = self.get_stm_context(user_id, thread_id, messages, thread_language, translated_history)
        
        # Get LTM context with timeout and fallback - only for educational agent
        ltm_results = []
        try:
            ltm_results = await asyncio.wait_for(
                self.ltm.retrieve_memory(user_id, thread_id, query),
                timeout=10.0  # 10 second timeout for LTM retrieval
            )
        except asyncio.TimeoutError:
            print(f"[MemoryManager] LTM retrieval timed out for {user_id}-{thread_id}")
        except Exception as e:
            print(f"[MemoryManager] LTM retrieval error: {e}")
        
        context = {
            "short_term": stm_context,
            "long_term": ltm_results,
            "ltm_summary": self._summarize_ltm(ltm_results)
        }
        
        print(f"[MemoryManager] Context prepared - STM: {len(context['short_term'])} chars, LTM: {len(ltm_results)} items, Language: {thread_language}")
        return context
    
    def _summarize_ltm(self, ltm_results: List[Tuple]) -> str:
        """Create a concise summary of relevant LTM"""
        if not ltm_results:
            return "No relevant long-term context available."
        
        summary_parts = []
        for content, meta in ltm_results[:3]:  # Top 3 most relevant
            summary_parts.append(f"[{meta['type']}] {content}")
        
        summary = " | ".join(summary_parts)
        print(f"[MemoryManager] LTM summary created: {len(summary)} characters")
        return summary