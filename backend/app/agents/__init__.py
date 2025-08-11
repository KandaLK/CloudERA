"""
Multi-Agent Intent System

This module implements a sophisticated multi-agent framework for intent extraction,
question enhancement, decomposition, and validation with dual-layer memory management.
"""

from .memory import ShortTermMemory, LongTermMemory, MemoryManager
from .agents import IntentionExtractor, QuestionEnhancer, QuestionDecomposer, ReEvaluator
from .workflow import IntentExtractionWorkflow, AgentState
from .models import (
    ConfidenceLevel, 
    IntentExtractionResult, 
    QuestionEnhancement, 
    QuestionDecomposition,
    ValidationResult,
    LTMEntity
)

__all__ = [
    'ShortTermMemory',
    'LongTermMemory', 
    'MemoryManager',
    'IntentionExtractor',
    'QuestionEnhancer',
    'QuestionDecomposer', 
    'ReEvaluator',
    'IntentExtractionWorkflow',
    'AgentState',
    'ConfidenceLevel',
    'IntentExtractionResult',
    'QuestionEnhancement',
    'QuestionDecomposition',
    'ValidationResult',
    'LTMEntity'
]