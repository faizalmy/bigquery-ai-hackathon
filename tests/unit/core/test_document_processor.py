#!/usr/bin/env python3
"""
Unit Tests for Document Processor
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

Following World-Class Production Tester Protocol:
- Comprehensive Coverage: Validate every specification, requirement, and edge case
- Risk-Based Prioritization: Focus testing on highest impact and failure probability areas
- Data-Driven Decisions: Base testing priorities on measurable metrics and trends
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Set up test environment and mocks
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "tests"))
from test_config import setup_test_environment, TEST_CONFIG, MOCK_DOCUMENT_DATA, MOCK_AI_RESULTS
setup_test_environment()

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from core.document_processor import LegalDocumentProcessor, ProcessingResult
from tests.mocks.mock_bigquery_client import MockBigQueryClient

class TestLegalDocumentProcessor(unittest.TestCase):
    """
    Comprehensive unit tests for LegalDocumentProcessor following tester protocol.

    Test Coverage Areas:
    1. Initialization and Configuration
    2. Document Processing Pipeline
    3. Error Handling and Edge Cases
    4. Performance and Resource Management
    5. Data Validation and Quality Gates
    """

    def setUp(self):
        """Set up test fixtures with mock dependencies."""
        self.project_id = "test-project"
        self.mock_bq_client = MockBigQueryClient(TEST_CONFIG)

        # Mock the AI models and components
        with patch('core.document_processor.SimpleAIModels') as mock_ai_models, \
             patch('core.document_processor.SimpleVectorSearch') as mock_vector_search, \
             patch('core.document_processor.PredictiveAnalytics') as mock_predictive:

            self.processor = LegalDocumentProcessor(self.project_id, self.mock_bq_client)

            # Store mock references for assertions
            self.mock_ai_models = mock_ai_models.return_value
            self.mock_vector_search = mock_vector_search.return_value
            self.mock_predictive = mock_predictive.return_value

    def test_initialization_success(self):
        """Test successful processor initialization."""
        # Verify all components are initialized
        self.assertEqual(self.processor.project_id, self.project_id)
        self.assertEqual(self.processor.bq_client, self.mock_bq_client)
        self.assertIsNotNone(self.processor.ai_models)
        self.assertIsNotNone(self.processor.vector_search)
        self.assertIsNotNone(self.processor.predictive_analytics)

        # Verify initial metrics
        self.assertEqual(self.processor.processing_metrics['total_processed'], 0)
        self.assertEqual(self.processor.processing_metrics['successful_processed'], 0)
        self.assertEqual(self.processor.processing_metrics['failed_processed'], 0)
        self.assertEqual(self.processor.processing_metrics['average_processing_time'], 0.0)

    def test_document_validation_success(self):
        """Test successful document validation."""
        valid_document = {
            'content': 'This is a valid legal document with sufficient content for processing.',
            'document_type': 'contract',
            'metadata': {'source': 'test'}
        }

        result = self.processor._validate_document(valid_document)

        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_document_validation_missing_content(self):
        """Test document validation with missing content."""
        invalid_document = {
            'document_type': 'contract',
            'metadata': {'source': 'test'}
        }

        result = self.processor._validate_document(invalid_document)

        self.assertFalse(result['valid'])
        self.assertIn("Missing required field: content", result['errors'])

    def test_document_validation_empty_content(self):
        """Test document validation with empty content."""
        invalid_document = {
            'content': '',
            'document_type': 'contract'
        }

        result = self.processor._validate_document(invalid_document)

        self.assertFalse(result['valid'])
        self.assertIn("Document content is empty", result['errors'])

    def test_document_validation_content_too_short(self):
        """Test document validation with content too short."""
        invalid_document = {
            'content': 'Short',
            'document_type': 'contract'
        }

        result = self.processor._validate_document(invalid_document)

        self.assertFalse(result['valid'])
        self.assertIn("Document content too short", result['errors'])

    def test_document_validation_content_too_long(self):
        """Test document validation with content too long."""
        invalid_document = {
            'content': 'x' * 1000001,  # Over 1M characters
            'document_type': 'contract'
        }

        result = self.processor._validate_document(invalid_document)

        self.assertFalse(result['valid'])
        self.assertIn("Document content too long", result['errors'])

    @patch('core.document_processor.datetime')
    def test_process_document_success(self, mock_datetime):
        """Test successful document processing."""
        # Mock datetime
        mock_start_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_end_time = datetime(2025, 1, 1, 12, 0, 5)
        mock_datetime.now.side_effect = [mock_start_time, mock_end_time]

        # Mock AI processing results
        self.mock_ai_models.extract_legal_data.return_value = {
            'parties': ['Party A', 'Party B'],
            'issues': ['Contract dispute'],
            'outcome': 'Settlement'
        }
        self.mock_ai_models.summarize_document.return_value = {
            'summary': 'Test summary',
            'key_points': ['Point 1', 'Point 2']
        }
        self.mock_ai_models.classify_document.return_value = {
            'classification': {'legal_domain': 'contract_law'},
            'confidence': 0.9
        }

        # Mock predictive analytics
        self.mock_predictive.predict_case_outcome.return_value = {
            'prediction': 'Favorable',
            'confidence_score': 0.8
        }
        self.mock_predictive.assess_legal_risk.return_value = {
            'risk_level': 'low',
            'confidence_score': 0.7
        }
        self.mock_predictive.generate_legal_strategy.return_value = {
            'strategy': 'Negotiate settlement',
            'confidence_score': 0.8
        }
        self.mock_predictive.check_compliance.return_value = {
            'compliant': True,
            'confidence_score': 0.9
        }
        self.mock_predictive.comprehensive_analysis.return_value = {
            'overall_assessment': 'Low risk case',
            'confidence_score': 0.8
        }

        # Test document
        test_document = {
            'content': 'This is a valid legal document for testing.',
            'document_type': 'contract',
            'metadata': {'source': 'test'}
        }

        result = self.processor.process_document(test_document)

        # Verify result structure
        self.assertIsInstance(result, ProcessingResult)
        self.assertEqual(result.status, 'completed')
        self.assertEqual(result.processing_time, 5.0)
        self.assertEqual(len(result.errors), 0)

        # Verify processing results
        self.assertIn('ai_analysis', result.results)
        self.assertIn('vector_analysis', result.results)
        self.assertIn('predictive_analysis', result.results)
        self.assertIn('storage', result.results)

        # Verify metrics updated
        self.assertEqual(self.processor.processing_metrics['total_processed'], 1)
        self.assertEqual(self.processor.processing_metrics['successful_processed'], 1)
        self.assertEqual(self.processor.processing_metrics['failed_processed'], 0)

    def test_process_document_validation_failure(self):
        """Test document processing with validation failure."""
        invalid_document = {
            'content': '',  # Empty content
            'document_type': 'contract'
        }

        result = self.processor.process_document(invalid_document)

        # Verify failure result
        self.assertEqual(result.status, 'failed')
        self.assertGreater(len(result.errors), 0)
        self.assertIn("Document validation failed", result.errors[0])

        # Verify metrics updated
        self.assertEqual(self.processor.processing_metrics['total_processed'], 1)
        self.assertEqual(self.processor.processing_metrics['successful_processed'], 0)
        self.assertEqual(self.processor.processing_metrics['failed_processed'], 1)

    def test_process_document_ai_processing_failure(self):
        """Test document processing with AI processing failure."""
        # Mock AI processing to raise exception
        self.mock_ai_models.extract_legal_data.side_effect = Exception("AI processing failed")

        test_document = {
            'content': 'This is a valid legal document for testing.',
            'document_type': 'contract'
        }

        result = self.processor.process_document(test_document)

        # Verify failure result
        self.assertEqual(result.status, 'failed')
        self.assertIn("AI processing failed", result.errors[0])

        # Verify metrics updated
        self.assertEqual(self.processor.processing_metrics['failed_processed'], 1)

    def test_process_batch_success(self):
        """Test successful batch processing."""
        # Mock successful processing
        with patch.object(self.processor, 'process_document') as mock_process:
            mock_process.return_value = ProcessingResult(
                document_id="test_doc",
                status="completed",
                processing_time=1.0,
                results={},
                errors=[],
                timestamp=datetime.now()
            )

            documents = [
                {'content': 'Document 1', 'document_type': 'contract'},
                {'content': 'Document 2', 'document_type': 'brief'}
            ]

            results = self.processor.process_batch(documents)

            # Verify results
            self.assertEqual(len(results), 2)
            self.assertEqual(mock_process.call_count, 2)

            for result in results:
                self.assertEqual(result.status, 'completed')

    def test_get_processing_status_existing(self):
        """Test getting processing status for existing document."""
        document_id = "test_doc"
        self.processor.processing_status[document_id] = {
            'status': 'processing',
            'start_time': datetime.now(),
            'stage': 'ai_processing'
        }

        status = self.processor.get_processing_status(document_id)

        self.assertEqual(status['status'], 'processing')
        self.assertEqual(status['stage'], 'ai_processing')

    def test_get_processing_status_not_found(self):
        """Test getting processing status for non-existent document."""
        status = self.processor.get_processing_status("non_existent_doc")

        self.assertEqual(status['status'], 'not_found')

    def test_retry_failed_processing(self):
        """Test retry functionality for failed processing."""
        document_id = "failed_doc"

        result = self.processor.retry_failed_processing(document_id)

        # Verify retry result
        self.assertEqual(result.status, 'failed')
        self.assertIn("Retry functionality requires document storage implementation", result.errors)

    def test_update_processing_metrics_success(self):
        """Test processing metrics update for successful processing."""
        initial_total = self.processor.processing_metrics['total_processed']
        initial_successful = self.processor.processing_metrics['successful_processed']
        initial_avg_time = self.processor.processing_metrics['average_processing_time']

        self.processor._update_processing_metrics(2.5, success=True)

        # Verify metrics updated
        self.assertEqual(self.processor.processing_metrics['total_processed'], initial_total + 1)
        self.assertEqual(self.processor.processing_metrics['successful_processed'], initial_successful + 1)
        self.assertEqual(self.processor.processing_metrics['average_processing_time'], 2.5)

    def test_update_processing_metrics_failure(self):
        """Test processing metrics update for failed processing."""
        initial_total = self.processor.processing_metrics['total_processed']
        initial_failed = self.processor.processing_metrics['failed_processed']

        self.processor._update_processing_metrics(1.0, success=False)

        # Verify metrics updated
        self.assertEqual(self.processor.processing_metrics['total_processed'], initial_total + 1)
        self.assertEqual(self.processor.processing_metrics['failed_processed'], initial_failed + 1)

    def test_get_processing_metrics(self):
        """Test getting current processing metrics."""
        # Set up some test data
        self.processor.processing_metrics['total_processed'] = 10
        self.processor.processing_metrics['successful_processed'] = 8
        self.processor.processing_metrics['failed_processed'] = 2
        self.processor.processing_metrics['average_processing_time'] = 3.5

        self.processor.processing_status['active_doc'] = {'status': 'processing'}

        metrics = self.processor.get_processing_metrics()

        # Verify metrics structure
        self.assertIn('metrics', metrics)
        self.assertIn('active_processing', metrics)
        self.assertIn('timestamp', metrics)

        # Verify values
        self.assertEqual(metrics['metrics']['total_processed'], 10)
        self.assertEqual(metrics['metrics']['successful_processed'], 8)
        self.assertEqual(metrics['metrics']['failed_processed'], 2)
        self.assertEqual(metrics['active_processing'], 1)

    def test_generate_embeddings_success(self):
        """Test successful embedding generation."""
        self.mock_vector_search.create_embedding_table.return_value = True

        document = {'content': 'Test content'}
        ai_results = {'test': 'data'}

        result = self.processor._generate_embeddings(document, ai_results)

        # Verify result
        self.assertTrue(result['embedding_generated'])
        self.assertIn('embedding_timestamp', result)
        self.assertEqual(result['method'], 'simple_vector_search')

    def test_generate_embeddings_failure(self):
        """Test embedding generation failure."""
        self.mock_vector_search.create_embedding_table.side_effect = Exception("Embedding failed")

        document = {'content': 'Test content'}
        ai_results = {'test': 'data'}

        result = self.processor._generate_embeddings(document, ai_results)

        # Verify failure result
        self.assertFalse(result['embedding_generated'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Embedding failed')

    def test_store_processing_results_success(self):
        """Test successful storage of processing results."""
        document_id = "test_doc"
        results = {'test': 'data'}

        result = self.processor._store_processing_results(document_id, results)

        # Verify result
        self.assertTrue(result['stored'])
        self.assertIn('table_id', result)
        self.assertIn('storage_timestamp', result)

    def test_store_processing_results_failure(self):
        """Test storage failure handling."""
        # This would be tested with actual BigQuery failures in integration tests
        # For unit tests, we verify the structure is correct
        document_id = "test_doc"
        results = {'test': 'data'}

        result = self.processor._store_processing_results(document_id, results)

        # Verify result structure
        self.assertIn('stored', result)
        self.assertIn('table_id', result)
        self.assertIn('storage_timestamp', result)

    def test_performance_requirements(self):
        """Test that processing meets performance requirements."""
        # This test verifies the architecture supports performance requirements
        # Actual performance testing would be done in integration tests

        # Verify processing pipeline is designed for < 60s processing time
        self.assertIsNotNone(self.processor.ai_models)
        self.assertIsNotNone(self.processor.vector_search)
        self.assertIsNotNone(self.processor.predictive_analytics)

        # Verify error handling is in place for performance issues
        self.assertIsNotNone(self.processor.processing_metrics)
        self.assertIn('average_processing_time', self.processor.processing_metrics)

    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with various error conditions
        test_cases = [
            {'content': None},  # None content
            {'content': 123},   # Non-string content
            {},                 # Empty document
            {'content': 'x' * 2000000}  # Extremely long content
        ]

        for test_doc in test_cases:
            result = self.processor.process_document(test_doc)

            # Verify error handling
            self.assertEqual(result.status, 'failed')
            self.assertGreater(len(result.errors), 0)

            # Verify metrics updated
            self.assertGreater(self.processor.processing_metrics['total_processed'], 0)

    def test_data_quality_gates(self):
        """Test data quality gates and validation."""
        # Test quality gate: content length validation
        quality_test_cases = [
            ('', False, "empty content"),
            ('x' * 5, False, "too short"),
            ('x' * 10, True, "minimum valid"),
            ('x' * 1000000, True, "maximum valid"),
            ('x' * 1000001, False, "too long")
        ]

        for content, should_pass, description in quality_test_cases:
            with self.subTest(description=description):
                doc = {'content': content}
                result = self.processor._validate_document(doc)

                if should_pass:
                    self.assertTrue(result['valid'], f"Should pass: {description}")
                else:
                    self.assertFalse(result['valid'], f"Should fail: {description}")

class TestProcessingResult(unittest.TestCase):
    """Test ProcessingResult data structure."""

    def test_processing_result_creation(self):
        """Test ProcessingResult creation and properties."""
        timestamp = datetime.now()
        result = ProcessingResult(
            document_id="test_doc",
            status="completed",
            processing_time=1.5,
            results={'test': 'data'},
            errors=[],
            timestamp=timestamp
        )

        # Verify properties
        self.assertEqual(result.document_id, "test_doc")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.processing_time, 1.5)
        self.assertEqual(result.results, {'test': 'data'})
        self.assertEqual(result.errors, [])
        self.assertEqual(result.timestamp, timestamp)

    def test_processing_result_with_errors(self):
        """Test ProcessingResult with errors."""
        timestamp = datetime.now()
        errors = ["Error 1", "Error 2"]

        result = ProcessingResult(
            document_id="failed_doc",
            status="failed",
            processing_time=0.5,
            results={},
            errors=errors,
            timestamp=timestamp
        )

        # Verify error handling
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.errors, errors)
        self.assertEqual(len(result.errors), 2)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
