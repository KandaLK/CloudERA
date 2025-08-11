"""
Pydantic models for the multi-agent intent system
"""

from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IntentExtractionResult(BaseModel):
    intent: Optional[str] = Field(None, description="Extracted user intent")
    confidence: ConfidenceLevel = Field(..., description="Confidence in extraction")
    domain_relevance: str = Field(..., description="Domain relevance: 'domain', 'general', or 'followup'")
    clarification_needed: bool = Field(False, description="Whether clarification is needed")
    clarification_question: Optional[str] = Field(None, description="Question to ask user")
    reasoning: str = Field(..., description="Explanation of decision")


class QuestionEnhancement(BaseModel):
    enhanced_question: str = Field(..., description="Simplified, unambiguous question")
    reasoning: str = Field(..., description="Enhancement reasoning")


class QuestionDecomposition(BaseModel):
    sub_questions: List[str] = Field(..., description="2-4 essential sub-questions that directly serve the enhanced question")
    sub_question_reasoning: List[str] = Field(..., description="Explanation for why each sub-question is needed")
    web_queries: List[str] = Field(..., description="2-3 web search queries targeting the specific enhanced question")
    reasoning: str = Field(..., description="Overall decomposition strategy and approach")


class ValidationResult(BaseModel):
    approved: bool = Field(..., description="Whether output is approved")
    feedback: str = Field(..., description="General feedback for improvement")
    improvement_instructions: str = Field(..., description="Specific step-by-step instructions for improvement")
    technical_suggestions: str = Field(..., description="Domain-specific technical terminology and concepts to include")
    revision_prompts: str = Field(..., description="Ready-to-use prompt additions for agent improvement")
    next_action: str = Field(..., description="Next step: proceed, revise_intent, revise_enhancement, or revise_decomposition")


class LTMEntity(BaseModel):
    entity_type: str = Field(..., description="Type: preference, expertise, service, or fact")
    content: str = Field(..., description="The extracted information")
    confidence: float = Field(..., description="Confidence score 0-1")
    source_context: str = Field(..., description="Context it was extracted from")


class LTMEntityList(BaseModel):
    entities: List[LTMEntity] = Field(..., description="List of extracted entities")


class URLRelevanceEvaluation(BaseModel):
    relevant_urls: List[str] = Field(..., description="Top 5 most relevant URLs to scrape")
    url_confidence_scores: Dict[str, float] = Field(..., description="Confidence scores (0.0-1.0) for each URL's relevance to the search query")
    fallback_urls: List[str] = Field(default_factory=list, description="Additional URLs ranked by relevance for fallback use")
    url_ranking_details: Dict[str, str] = Field(default_factory=dict, description="Detailed reasoning for each URL's relevance score")
    reasoning: str = Field(..., description="Overall evaluation reasoning for URL selection")


class WebSearchResultEvaluation(BaseModel):
    relevant_urls: List[str] = Field(..., description="Top 5 most relevant URLs to scrape") 
    url_scores: Dict[str, float] = Field(..., description="Relevance scores for each URL")
    reasoning: str = Field(..., description="Evaluation reasoning")


class ResponseGeneration(BaseModel):
    response: str = Field(..., description="Generated response to user question")
    response_type: str = Field(..., description="Type: 'domain_response', 'not_allowed', or 'clarification'")
    sources_used: List[str] = Field(default_factory=list, description="Web sources referenced in response")
    confidence: float = Field(..., description="Confidence in response quality (0.0-1.0)")
    reasoning: str = Field(..., description="Explanation of response generation approach")