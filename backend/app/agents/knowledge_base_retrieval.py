"""
Knowledge Base Retrieval Service using LIGHTRAG
Integrates the provided LIGHTRAG retrieval functionality into the multi-agent system.
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import setup_logger

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class KnowledgeBaseRetriever:
    """
    Connects to the LightRAG knowledge base and retrieves answers.
    Uses centralized configuration from settings.
    """

    def __init__(self):
        self.rag: Optional[LightRAG] = None
        self.initialized = False
        logger.info(f"[KnowledgeBaseRetriever] Initialized with working directory: {settings.lightrag_working_dir}")

    async def initialize(self) -> bool:
        """
        Initializes the LightRAG instance for retrieval using centralized settings.
        """
        try:
            # Set environment variables from centralized settings
            if settings.neo4j_uri:
                os.environ["NEO4J_URI"] = settings.neo4j_uri
            if settings.neo4j_username:
                os.environ["NEO4J_USERNAME"] = settings.neo4j_username
            if settings.neo4j_password:
                os.environ["NEO4J_PASSWORD"] = settings.neo4j_password
            if settings.openai_api_key:
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key

            logger.info(f"[KnowledgeBaseRetriever] Initializing with working directory: {settings.lightrag_working_dir}")

            # Initialize LightRAG with centralized configuration
            self.rag = LightRAG(
                working_dir=str(settings.lightrag_working_dir),
                llm_model_func=gpt_4o_mini_complete,
                embedding_func=openai_embed,
                graph_storage="Neo4JStorage",
                vector_storage="FaissVectorDBStorage",
            )

            # Initialize storage systems for read-only access
            await self.rag.initialize_storages()
            self.initialized = True
            logger.info("[KnowledgeBaseRetriever] Initialized successfully.")
            return True

        except Exception as e:
            logger.error(f"[KnowledgeBaseRetriever] Failed to initialize: {e}")
            self.initialized = False
            return False

    async def query(self, query_text: str) -> Optional[str]:
        """
        Queries the knowledge base with a specific question and returns the final answer.

        Args:
            query_text: The question to ask.

        Returns:
            The generated answer as a string, or None if an error occurs.
        """
        if not self.initialized or not self.rag:
            logger.error("[KnowledgeBaseRetriever] Not initialized. Call initialize() first.")
            return None

        try:
            logger.info(f"[KnowledgeBaseRetriever] Querying with mix mode: '{query_text}'")

            # Define query parameters to get a generated response
            param = QueryParam(
                mode="mix",
                top_k=10,
                only_need_context=True,  # We want the final answer, not just the context
                response_type="Single Paragraph"  # Keep the answer concise
            )

            # Execute the query
            response = await self.rag.aquery(query_text, param=param)

            if response:
                logger.info("[KnowledgeBaseRetriever] Query successful.")
            else:
                logger.warning("[KnowledgeBaseRetriever] Query returned an empty response.")

            return response

        except Exception as e:
            logger.error(f"[KnowledgeBaseRetriever] Error during query: {e}")
            return None

    async def query_multiple(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple questions in parallel and return structured results.
        
        Args:
            questions: List of questions to query
            
        Returns:
            List of dictionaries with question, answer, and metadata
        """
        if not self.initialized or not self.rag:
            logger.error("[KnowledgeBaseRetriever] Not initialized. Call initialize() first.")
            return []

        if not questions:
            logger.warning("[KnowledgeBaseRetriever] No questions provided.")
            return []

        logger.info(f"[KnowledgeBaseRetriever] Processing {len(questions)} questions in parallel")

        async def query_single(question: str) -> Dict[str, Any]:
            """Process a single question and return structured result"""
            try:
                answer = await self.query(question)
                return {
                    "question": question,
                    "answer": answer,
                    "success": answer is not None,
                    "source": "knowledge_base",
                    "metadata": {
                        "query_mode": "mix",
                        "top_k": 10
                    }
                }
            except Exception as e:
                logger.error(f"[KnowledgeBaseRetriever] Error processing question '{question}': {e}")
                return {
                    "question": question,
                    "answer": None,
                    "success": False,
                    "source": "knowledge_base",
                    "error": str(e)
                }

        # Process all questions in parallel with reasonable concurrency limit
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent queries
        
        async def query_with_semaphore(question: str) -> Dict[str, Any]:
            async with semaphore:
                return await query_single(question)

        try:
            results = await asyncio.gather(
                *[query_with_semaphore(q) for q in questions],
                return_exceptions=True
            )
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"[KnowledgeBaseRetriever] Exception for question {i}: {result}")
                    processed_results.append({
                        "question": questions[i],
                        "answer": None,
                        "success": False,
                        "source": "knowledge_base",
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
            
            successful_queries = sum(1 for r in processed_results if r["success"])
            logger.info(f"[KnowledgeBaseRetriever] Completed {successful_queries}/{len(questions)} queries successfully")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"[KnowledgeBaseRetriever] Error in parallel query processing: {e}")
            return []
    
    async def finalize(self):
        """Properly close the retriever and storage connections"""
        if self.rag and self.initialized:
            try:
                logger.info("[KnowledgeBaseRetriever] Finalizing retriever...")
                await self.rag.finalize_storages()
                logger.info("[KnowledgeBaseRetriever] Retriever finalized successfully")
            except Exception as e:
                logger.error(f"[KnowledgeBaseRetriever] Error during finalization: {e}")
            finally:
                self.initialized = False
                self.rag = None


# Global instance for the agents to use
_retriever_instance: Optional[KnowledgeBaseRetriever] = None

async def get_knowledge_base_retriever() -> KnowledgeBaseRetriever:
    """Get or create the global knowledge base retriever instance"""
    global _retriever_instance
    
    if _retriever_instance is None:
        _retriever_instance = KnowledgeBaseRetriever()
        await _retriever_instance.initialize()
    
    return _retriever_instance

async def cleanup_knowledge_base_retriever():
    """Cleanup the global retriever instance"""
    global _retriever_instance
    
    if _retriever_instance is not None:
        await _retriever_instance.finalize()
        _retriever_instance = None