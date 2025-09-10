#!/usr/bin/env python3
"""
Test Configuration for Unit Tests
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module provides test configuration and mock setup for unit testing.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set up mock imports before any other imports
def setup_test_environment():
    """Set up test environment with mocks."""
    # Mock BigQuery dependencies
    from tests.mocks.mock_bigquery_client import setup_mock_imports
    setup_mock_imports()

    # Set test environment variables
    os.environ['TESTING'] = 'true'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/test_credentials.json'

    return True

# Test configuration
TEST_CONFIG = {
    'bigquery': {
        'project_id': 'test-project',
        'location': 'US',
        'dataset_id': 'test_dataset',
        'tables': {
            'legal_documents': 'test_dataset.legal_documents',
            'embeddings': 'test_dataset.embeddings',
            'analysis_results': 'test_dataset.analysis_results'
        }
    },
    'ai_models': {
        'legal_extractor': {
            'model_name': 'test_legal_extractor',
            'version': '1.0.0'
        },
        'document_summarizer': {
            'model_name': 'test_document_summarizer',
            'version': '1.0.0'
        },
        'document_classifier': {
            'model_name': 'test_document_classifier',
            'version': '1.0.0'
        }
    },
    'vector_search': {
        'embedding_model': 'test_embedding_model',
        'similarity_threshold': 0.7,
        'max_results': 10
    },
    'predictive_analytics': {
        'outcome_model': 'test_outcome_model',
        'risk_model': 'test_risk_model',
        'strategy_model': 'test_strategy_model'
    },
    'processing': {
        'max_document_size': 1000000,
        'min_document_size': 10,
        'supported_formats': ['txt', 'pdf', 'docx'],
        'timeout_seconds': 300
    }
}

# Mock data for testing
MOCK_DOCUMENT_DATA = {
    'case_001': {
        'content': 'This is a constitutional law case involving free speech rights. The plaintiff argues that their First Amendment rights were violated.',
        'document_type': 'case_law',
        'metadata': {
            'jurisdiction': 'federal',
            'court': 'Supreme Court',
            'date': '2023-01-15',
            'case_number': '23-001'
        }
    },
    'case_002': {
        'content': 'This is a contract dispute case involving breach of contract claims. The defendant failed to deliver goods as specified in the agreement.',
        'document_type': 'case_law',
        'metadata': {
            'jurisdiction': 'state',
            'court': 'Superior Court',
            'date': '2023-02-20',
            'case_number': '23-002'
        }
    },
    'contract_001': {
        'content': 'This is a software licensing agreement between Company A and Company B. The agreement specifies terms for software usage and licensing fees.',
        'document_type': 'contract',
        'metadata': {
            'parties': ['Company A', 'Company B'],
            'date': '2023-03-10',
            'contract_type': 'software_license'
        }
    }
}

MOCK_AI_RESULTS = {
    'legal_extraction': {
        'parties': ['Plaintiff', 'Defendant'],
        'issues': ['Constitutional rights violation', 'Free speech'],
        'outcome': 'Pending',
        'legal_domains': ['constitutional_law', 'first_amendment']
    },
    'document_summary': {
        'summary': 'Case involving First Amendment free speech rights violation claims.',
        'key_points': [
            'Plaintiff alleges First Amendment violation',
            'Defendant argues legitimate government interest',
            'Court must balance competing interests'
        ]
    },
    'document_classification': {
        'classification': {
            'legal_domain': 'constitutional_law',
            'document_type': 'case_law',
            'jurisdiction': 'federal'
        },
        'confidence': 0.95
    }
}

MOCK_SIMILARITY_RESULTS = [
    {
        'document_id': 'similar_001',
        'similarity_score': 0.85,
        'document_type': 'case_law',
        'summary': 'Similar constitutional law case involving free speech',
        'legal_domain': 'constitutional_law',
        'jurisdiction': 'federal',
        'case_outcome': 'favorable',
        'quality_score': 0.9
    },
    {
        'document_id': 'similar_002',
        'similarity_score': 0.78,
        'document_type': 'case_law',
        'summary': 'Another constitutional law case with similar issues',
        'legal_domain': 'constitutional_law',
        'jurisdiction': 'federal',
        'case_outcome': 'unfavorable',
        'quality_score': 0.8
    }
]

MOCK_PREDICTIVE_RESULTS = {
    'outcome_prediction': {
        'prediction': 'Favorable',
        'confidence_score': 0.8,
        'reasoning': 'Strong constitutional arguments and precedent support'
    },
    'risk_assessment': {
        'risk_level': 'low',
        'confidence_score': 0.7,
        'risk_factors': ['Strong precedent', 'Clear constitutional basis'],
        'mitigation_strategies': ['Focus on precedent research', 'Emphasize constitutional arguments']
    },
    'strategy_recommendations': [
        {
            'strategy_type': 'outcome_based',
            'title': 'Constitutional Strategy',
            'description': 'Focus on constitutional arguments and precedent',
            'confidence': 0.8,
            'priority': 'high'
        },
        {
            'strategy_type': 'risk_mitigation',
            'title': 'Risk Mitigation Strategy',
            'description': 'Address identified risk factors',
            'confidence': 0.7,
            'priority': 'medium'
        }
    ],
    'compliance_check': {
        'compliant': True,
        'confidence_score': 0.9,
        'compliance_issues': [],
        'recommendations': ['Continue current approach']
    }
}

# Initialize test environment
setup_test_environment()
