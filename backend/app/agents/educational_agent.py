"""
Educational Content Agent

Independent agent that generates educational content about GDPR, PDPA, and Cloud Security
when users ask non-domain questions or need clarification. Posts content to SMART_LEARNER thread.
"""

import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from datetime import datetime, timezone
import uuid
import random

from app.core.config import settings
from .circuit_breaker import circuit_manager
from app.models.chat_thread import ChatThread, ThreadType
from app.models.message import Message, MessageAuthor
from app.database.database import get_db
from sqlalchemy.orm import Session


class EducationalContentAgent:
    """
    Independent agent for generating educational content about GDPR, PDPA, and Cloud Security.
    Operates independently of main workflow without blocking user responses.
    """

    def __init__(self):
        print("[EducationalAgent] Initializing Educational Content Agent")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.circuit_breaker = circuit_manager.get_breaker("educational_agent")
        
        # Simplified content categories for creative ideas
        self.content_categories = [
            "cloud architecture patterns",
            "security best practices", 
            "compliance frameworks",
            "emerging cloud technologies",
            "data protection strategies (GDPR/PDPR , .etc)",
            "network optimization techniques"
        ]


    async def generate_creative_educational_post(
        self,
        user_context: Dict[str, Any],
        smart_thread_history: List[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate creative educational content using LTM context and smart thread history.
        Simplified approach focusing only on creative post generation.
        
        Args:
            user_context: User information including memory_context with LTM
            smart_thread_history: Recent messages from Smart Learner thread for context
            
        Returns:
            Generated creative educational content or None if generation fails
        """
        try:
            # Get random creative topic
            topic = random.choice(self.content_categories)
            
            # Extract LTM context
            memory_context = user_context.get("memory_context", {})
            ltm_summary = memory_context.get("ltm_summary", "New user exploring cloud technologies")
            
            # Build context from smart thread history
            thread_context = ""
            if smart_thread_history:
                recent_topics = []
                for msg in smart_thread_history[-3:]:  # Last 3 messages
                    if msg.get("content"):
                        # Extract key topics from previous educational content
                        content = msg.get("content", "")[:400]
                        recent_topics.append(content)
                thread_context = " | ".join(recent_topics) if recent_topics else "Starting educational journey"
            else:
                thread_context = "Fresh start in learning journey"
            
            prompt = f"""
            Create a brief, engaging educational post in "Did you know?" Q&A format for a Smart Learner thread.
            
            Topic Focus: {topic}
            User's Learning History (LTM): {ltm_summary}
            Smart Thread Context: {thread_context}
            
            Requirements:
            1. Start with "Did you know?" followed by an interesting question
            2. Provide a clear, concise answer (2-3 sentences max)
            3. Focus on practical cloud services, DevOps, security, and data protection insights
            4. Make it relevant to user's learning context
            5. Keep it brief but resourceful - users should be attracted, not overwhelmed
            6. Include a credible source link if possible (optional)
            
            Format:
            **Did you know?** [Engaging question about the topic]
            
            [Brief, practical answer with real-world relevance]
            
            💡 **Key Takeaway:** [One actionable insight]
            
            [Optional: 📚 **Source:** [Credible link or reference]]
            
            Focus Areas:
            - Build on their previous learning context
            - Avoid repeating recent Smart Thread topics  
            - Provide immediately applicable knowledge
            - Connect to practical cloud/security scenarios
            """
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.8  # Higher creativity for educational posts
            )
            
            content = response.choices[0].message.content.strip()
            
            print(f"[EducationalAgent] Generated creative post on: {topic}, length: {len(content)}")
            return content
            
        except Exception as e:
            print(f"[EducationalAgent] Error generating creative post: {e}")
            return None

    async def post_to_smart_learner_thread(
        self, 
        user_id: str, 
        content: str,
        db: Session
    ) -> bool:
        """
        Post educational content to user's SMART_LEARNER thread.
        Creates thread if it doesn't exist.
        
        Args:
            user_id: Target user ID
            content: Educational content to post
            db: Database session
            
        Returns:
            True if posting successful, False otherwise
        """
        try:
            # Find or create SMART_LEARNER thread for user
            smart_learner_thread = db.query(ChatThread).filter(
                ChatThread.user_id == user_id,
                ChatThread.thread_type == ThreadType.SMART_LEARNER
            ).first()
            
            if not smart_learner_thread:
                # Create SMART_LEARNER thread
                smart_learner_thread = ChatThread(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    name="Smart Learner - Educational Content",
                    thread_type=ThreadType.SMART_LEARNER,
                    language="ENG",
                    is_permanent=True
                )
                db.add(smart_learner_thread)
                db.flush()  # Ensure thread ID is available
                print(f"[EducationalAgent] Created SMART_LEARNER thread for user: {user_id}")
            
            # Create educational message
            educational_message = Message(
                id=uuid.uuid4(),
                thread_id=smart_learner_thread.id,
                user_id=user_id,
                author=MessageAuthor.ASSISTANT,
                content=f"{content}\n\n---\n*🎓 Generated based on your learning journey to expand your cloud and security knowledge.*"
            )
            
            db.add(educational_message)
            
            # Update thread's last_modified
            smart_learner_thread.last_modified = datetime.now(timezone.utc)
            
            db.commit()
            print(f"[EducationalAgent] Posted educational content to SMART_LEARNER thread: {smart_learner_thread.id}")
            return True
            
        except Exception as e:
            print(f"[EducationalAgent] Error posting to SMART_LEARNER thread: {e}")
            db.rollback()
            return False

    async def get_smart_thread_history(self, user_id: str, db) -> List[Dict[str, Any]]:
        """Get recent messages from Smart Learner thread for context"""
        try:
            # Find Smart Learner thread
            smart_thread = db.query(ChatThread).filter(
                ChatThread.user_id == user_id,
                ChatThread.thread_type == ThreadType.SMART_LEARNER
            ).first()
            
            if not smart_thread:
                return []
            
            # Get recent messages
            messages = db.query(Message).filter(
                Message.thread_id == smart_thread.id
            ).order_by(Message.created_at.desc()).limit(5).all()
            
            # Convert to dict format
            history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                history.append({
                    "role": msg.author.value,
                    "content": msg.content,
                    "created_at": msg.created_at
                })
            
            return history
            
        except Exception as e:
            print(f"[EducationalAgent] Error getting smart thread history: {e}")
            return []

    async def process_educational_trigger(
        self,
        user_id: str,
        user_query: str,
        response_type: str,
        conversation_history: List[Dict[str, Any]],
        memory_context: Dict[str, Any] = None
    ):
        """
        Simplified main entry point for educational content processing.
        Creates creative posts using LTM context and Smart Thread history.
        
        Args:
            user_id: User ID for targeting
            user_query: Original user query (for context)
            response_type: Type of response generated by main workflow
            conversation_history: Recent conversation context
            memory_context: LTM context for personalization
        """
        try:
            print(f"[EducationalAgent] Processing educational trigger for user: {user_id}")
            
            # Create educational content only for general or followup questions
            if response_type not in ["general", "followup"]:
                print(f"[EducationalAgent] Response type '{response_type}' not eligible for educational post, skipping")
                return
            
            # Prepare user context with memory
            user_context = {
                "user_id": user_id,
                "query": user_query,
                "response_type": response_type,
                "memory_context": memory_context or {}
            }
            
            # Get smart thread history and generate content using a database session
            from app.database.database import SessionLocal
            db = SessionLocal()
            try:
                # Get Smart Thread history for context
                smart_thread_history = await self.get_smart_thread_history(user_id, db)
                
                # Generate creative educational content
                content = await self.generate_creative_educational_post(
                    user_context, smart_thread_history
                )
                
                if not content:
                    print("[EducationalAgent] Failed to generate creative educational content")
                    return
                
                # Post to Smart Learner thread
                success = await self.post_to_smart_learner_thread(user_id, content, db)
                if success:
                    print(f"[EducationalAgent] Successfully posted creative content for user: {user_id}")
                else:
                    print(f"[EducationalAgent] Failed to post creative content for user: {user_id}")
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"[EducationalAgent] Error in educational trigger processing: {e}")


# Global instance for singleton pattern
_educational_agent_instance = None

def get_educational_agent() -> EducationalContentAgent:
    """Get or create the global educational agent instance"""
    global _educational_agent_instance
    if _educational_agent_instance is None:
        _educational_agent_instance = EducationalContentAgent()
    return _educational_agent_instance