"""
AI Models Package
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This package contains all AI model implementations for legal document analysis.
"""

from .legal_extractor import LegalExtractor
from .document_summarizer import DocumentSummarizer
from .urgency_detector import UrgencyDetector
from .outcome_predictor import OutcomePredictor
from .risk_assessor import RiskAssessor
from .strategy_generator import StrategyGenerator

__all__ = [
    'LegalExtractor',
    'DocumentSummarizer',
    'UrgencyDetector',
    'OutcomePredictor',
    'RiskAssessor',
    'StrategyGenerator'
]
