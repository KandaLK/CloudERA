"""
Translation Service using DeepSeek API

Provides efficient parallel translation for Sinhala to English translation
with optimized prompts for message and history processing.
"""

import asyncio
import openai
from typing import Dict, List, Any
from app.core.config import settings


class TranslationService:
    """DeepSeek-based translation service for Sinhala to English"""
    
    def __init__(self):
        if not settings.deepseek_api_key or not settings.translation_enabled:
            print("[Translation] Warning: Translation service disabled or no DeepSeek API key configured")
            self.client = None
        else:
            self.client = openai.OpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
            print("[Translation] DeepSeek translation service initialized")
    
    def _clean_response(self, response_text: str) -> str:
        """
        Clean and extract the core content from AI response, removing any explanatory text
        """
        if not response_text:
            return ""
            
        # Remove common AI explanation patterns
        cleaned = response_text.strip()
        
        # Remove explanation prefixes like "Here is the translation:", "Translation:", etc.
        prefixes_to_remove = [
            "Here is the translation:",
            "Translation:",
            "The translation is:",
            "Summary:",
            "Here is the summary:",
            "The summary is:",
            "English translation:",
            "Translated text:"
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove quotes if the entire response is wrapped in quotes
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1].strip()
        elif cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1].strip()
        
        # Remove any remaining explanation suffixes
        suffixes_to_remove = [
            "\n\nNote:",
            "\n\nThis translation",
            "\n\nThe above",
        ]
        
        for suffix in suffixes_to_remove:
            if suffix.lower() in cleaned.lower():
                idx = cleaned.lower().find(suffix.lower())
                cleaned = cleaned[:idx].strip()
        
        return cleaned

    async def translate_message_and_history_parallel(self, current_message: str, messages: List[Any]) -> Dict[str, Any]:
        """
        Parallel translation of current message and conversation history for Sinhala threads
        Returns both translated message and translated history summary
        """
        if not self.client:
            print("[Translation] No DeepSeek client available, returning original content")
            return {
                "translated_message": current_message,
                "translated_history": "No conversation history available.",
                "success": False
            }

        print(f"[Translation] Starting parallel translation: message + {len(messages)} history messages")

        try:
            # Create two parallel API call tasks
            tasks = [
                self._translate_message(current_message),
                self._translate_history(messages)
            ]

            # Execute both API calls simultaneously
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            translated_message = current_message  # fallback
            translated_history = "No conversation history available."  # fallback
            success = True

            if not isinstance(results[0], Exception):
                translated_message = results[0]
            else:
                print(f"[Translation] Message translation error: {results[0]}")
                success = False

            if not isinstance(results[1], Exception):
                translated_history = results[1]
            else:
                print(f"[Translation] History translation error: {results[1]}")
                success = False

            print(f"[Translation] Parallel translation completed - Success: {success}")
            return {
                "translated_message": translated_message,
                "translated_history": translated_history,
                "success": success
            }

        except Exception as e:
            print(f"[Translation] Parallel translation error: {e}")
            return {
                "translated_message": current_message,
                "translated_history": "Error processing conversation history.",
                "success": False
            }

    async def _translate_message(self, message: str) -> str:
        """Direct API call to translate user message"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional Sinhala to English translator. Your task is to:

1. Translate the given Sinhala text to clear, natural English
2. Preserve the original meaning and context
3. Handle technical terms related to cloud computing, AWS, Azure, GCP appropriately
4. For mixed Sinhala-English text, translate only the Sinhala parts
5. Output ONLY the English translation, no explanations or additional text
6. If the input is already in English, return it unchanged
7. Maintain the same tone and formality level

Focus on accuracy and natural English expression."""
                    },
                    {
                        "role": "user",
                        "content": f"Translate this to English: {message}"
                    }
                ],
                temperature=0.1,
                max_tokens=800
            )
            raw_response = response.choices[0].message.content.strip()
            return self._clean_response(raw_response)
        except Exception as e:
            print(f"[Translation] Message translation error: {e}")
            return message

    async def _translate_history(self, messages: List[Any]) -> str:
        """Direct API call to translate and summarize conversation history"""
        if not messages:
            return "No conversation history available."

        try:
            # Format last 6 messages
            conversation_lines = []
            for msg in messages[-5:]:
                if isinstance(msg, dict):
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                else:
                    # Handle Message objects
                    role = "user" if msg.author.value == "user" else "assistant"
                    content = msg.content

                conversation_lines.append(f"{role.upper()}: {content}")

            conversation = "\n".join(conversation_lines)
            
            # Apply 2000 character limit
            

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a professional conversation summarizer and translator. Your task is to:

1. Summarize the conversation in clear, concise English
2. Translate any Sinhala content to English while preserving ALL key technical points
3. Keep important context about cloud services, technical questions, and user preferences
4. Maintain chronological order and preserve question-answer relationships
5. Keep the summary comprehensive but under 1500 words
6. Focus on technical details, described topics and content
7. Output ONLY the English summary with all important details preserved

The summary will be used as memory context for AI agents."""
                    },
                    {
                        "role": "user",
                        "content": f"Translate and summarize:\n\n{conversation}"
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            raw_summary = response.choices[0].message.content.strip()
            summary = self._clean_response(raw_summary)
            print(f"[Translation] History translation completed: {len(summary)} characters")
            return summary

        except Exception as e:
            print(f"[Translation] History translation error: {e}")
            return "Error processing conversation history."


# Global translation service instance
_translation_service = None

def get_translation_service() -> TranslationService:
    """Get or create the global translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service