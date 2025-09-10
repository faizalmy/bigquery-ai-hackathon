"""
AI Module
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module contains all AI-related functionality for legal document analysis.
"""

from .models import (
    LegalExtractor,
    DocumentSummarizer,
    UrgencyDetector,
    OutcomePredictor,
    RiskAssessor,
    StrategyGenerator
)
from .embeddings import DocumentEmbeddingGenerator
from .vector_search import VectorSearchEngine
from .model_manager import ModelManager

__all__ = [
    'LegalExtractor',
    'DocumentSummarizer',
    'UrgencyDetector',
    'OutcomePredictor',
    'RiskAssessor',
    'StrategyGenerator',
    'DocumentEmbeddingGenerator',
    'VectorSearchEngine',
    'ModelManager'
]
