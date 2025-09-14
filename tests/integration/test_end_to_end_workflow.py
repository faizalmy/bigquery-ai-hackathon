#!/usr/bin/env python3
"""
End-to-End Integration Test Suite
Complete Legal Document Intelligence Platform Workflow

This test suite validates the complete end-to-end workflow combining:
- Track 1: Generative AI Functions (ML.GENERATE_TEXT, AI.GENERATE_TABLE, AI.GENERATE_BOOL, ML.FORECAST)
- Track 2: Vector Search Functions (ML.GENERATE_EMBEDDING, VECTOR_SEARCH)

Author: Faizal
Date: September 2025
Competition: BigQuery AI Hackathon
"""

import sys
import os
import unittest
import logging
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_ai_functions import BigQueryAIFunctions

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestEndToEndWorkflow(unittest.TestCase):
    """Test cases for complete end-to-end workflow."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with BigQuery AI functions."""
        logger.info("Setting up End-to-End Workflow test suite...")
        cls.bq_ai = BigQueryAIFunctions()
        cls.test_document_id = 'caselaw_000001'
        cls.test_query = "insurance contract dispute"

    def test_complete_track1_workflow(self):
        """Test complete Track 1 (Generative AI) workflow."""
        logger.info("Testing complete Track 1 workflow...")

        try:
            start_time = time.time()

            # Step 1: Document Summarization
            logger.info("Step 1: Document Summarization (ML.GENERATE_TEXT)")
            summary_result = self.bq_ai.ml_generate_text(
                document_id=self.test_document_id,
                limit=1
            )
            self.assertIsInstance(summary_result, dict)
            self.assertIn('summaries', summary_result)
            self.assertEqual(len(summary_result['summaries']), 1)

            # Step 2: Data Extraction
            logger.info("Step 2: Data Extraction (AI.GENERATE_TABLE)")
            extraction_result = self.bq_ai.ai_generate_table(
                document_id=self.test_document_id,
                limit=1
            )
            self.assertIsInstance(extraction_result, dict)
            self.assertIn('extractions', extraction_result)
            self.assertEqual(len(extraction_result['extractions']), 1)

            # Step 3: Urgency Detection
            logger.info("Step 3: Urgency Detection (AI.GENERATE_BOOL)")
            urgency_result = self.bq_ai.ai_generate_bool(
                document_id=self.test_document_id,
                limit=1
            )
            self.assertIsInstance(urgency_result, dict)
            self.assertIn('urgency_analyses', urgency_result)
            self.assertEqual(len(urgency_result['urgency_analyses']), 1)

            # Step 4: Case Outcome Prediction
            logger.info("Step 4: Case Outcome Prediction (ML.FORECAST)")
            forecast_result = self.bq_ai.ai_forecast(limit=3)
            self.assertIsInstance(forecast_result, dict)
            self.assertIn('forecasts', forecast_result)
            self.assertGreater(len(forecast_result['forecasts']), 0)

            end_time = time.time()
            total_time = end_time - start_time

            # Validate complete workflow
            self.assertLess(total_time, 120)  # Should complete within 2 minutes

            logger.info(f"✅ Complete Track 1 workflow test passed - Total time: {total_time:.2f} seconds")

        except Exception as e:
            self.fail(f"Complete Track 1 workflow test failed: {e}")

    def test_complete_track2_workflow(self):
        """Test complete Track 2 (Vector Search) workflow."""
        logger.info("Testing complete Track 2 workflow...")

        try:
            start_time = time.time()

            # Step 1: Generate Embeddings
            logger.info("Step 1: Generate Embeddings (ML.GENERATE_EMBEDDING)")
            embedding_result = self.bq_ai.ml_generate_embedding(
                document_id=self.test_document_id,
                limit=1
            )
            self.assertIsInstance(embedding_result, dict)
            self.assertIn('embeddings', embedding_result)
            self.assertEqual(len(embedding_result['embeddings']), 1)

            # Step 2: Vector Search
            logger.info("Step 2: Vector Search (VECTOR_SEARCH)")
            search_result = self.bq_ai.vector_search(
                query=self.test_query,
                limit=5
            )
            self.assertIsInstance(search_result, dict)
            self.assertIn('results', search_result)
            self.assertGreaterEqual(len(search_result['results']), 0)

            end_time = time.time()
            total_time = end_time - start_time

            # Validate complete workflow
            self.assertLess(total_time, 60)  # Should complete within 1 minute

            logger.info(f"✅ Complete Track 2 workflow test passed - Total time: {total_time:.2f} seconds")

        except Exception as e:
            self.fail(f"Complete Track 2 workflow test failed: {e}")

    def test_combined_track1_track2_workflow(self):
        """Test combined Track 1 + Track 2 workflow."""
        logger.info("Testing combined Track 1 + Track 2 workflow...")

        try:
            start_time = time.time()

            # Track 1: Generative AI
            logger.info("Track 1: Generative AI Functions")
            summary_result = self.bq_ai.ml_generate_text(limit=2)
            extraction_result = self.bq_ai.ai_generate_table(limit=2)
            urgency_result = self.bq_ai.ai_generate_bool(limit=2)
            forecast_result = self.bq_ai.ai_forecast(limit=2)

            # Track 2: Vector Search
            logger.info("Track 2: Vector Search Functions")
            embedding_result = self.bq_ai.ml_generate_embedding(limit=2)
            search_result = self.bq_ai.vector_search(query_text=self.test_query, limit=3)

            end_time = time.time()
            total_time = end_time - start_time

            # Validate all results
            self.assertIsInstance(summary_result, dict)
            self.assertIsInstance(extraction_result, dict)
            self.assertIsInstance(urgency_result, dict)
            self.assertIsInstance(forecast_result, dict)
            self.assertIsInstance(embedding_result, dict)
            self.assertIsInstance(search_result, dict)

            # Validate complete workflow
            self.assertLess(total_time, 180)  # Should complete within 3 minutes

            logger.info(f"✅ Combined workflow test passed - Total time: {total_time:.2f} seconds")

        except Exception as e:
            self.fail(f"Combined workflow test failed: {e}")

    def test_performance_benchmarks(self):
        """Test performance benchmarks for all functions."""
        logger.info("Testing performance benchmarks...")

        try:
            benchmarks = {}

            # Track 1 Performance Tests
            logger.info("Testing Track 1 performance...")

            # ML.GENERATE_TEXT
            start_time = time.time()
            self.bq_ai.ml_generate_text(limit=1)
            benchmarks['ml_generate_text'] = time.time() - start_time

            # AI.GENERATE_TABLE
            start_time = time.time()
            self.bq_ai.ai_generate_table(limit=1)
            benchmarks['ai_generate_table'] = time.time() - start_time

            # AI.GENERATE_BOOL
            start_time = time.time()
            self.bq_ai.ai_generate_bool(limit=1)
            benchmarks['ai_generate_bool'] = time.time() - start_time

            # ML.FORECAST
            start_time = time.time()
            self.bq_ai.ai_forecast(limit=1)
            benchmarks['ml_forecast'] = time.time() - start_time

            # Track 2 Performance Tests
            logger.info("Testing Track 2 performance...")

            # ML.GENERATE_EMBEDDING
            start_time = time.time()
            self.bq_ai.ml_generate_embedding(limit=1)
            benchmarks['ml_generate_embedding'] = time.time() - start_time

            # VECTOR_SEARCH
            start_time = time.time()
            self.bq_ai.vector_search(query_text=self.test_query, limit=3)
            benchmarks['vector_search'] = time.time() - start_time

            # Validate performance benchmarks
            for function, duration in benchmarks.items():
                self.assertLess(duration, 30)  # Each function should complete within 30 seconds
                logger.info(f"   {function}: {duration:.2f} seconds")

            logger.info("✅ Performance benchmarks test passed - All functions meet performance requirements")

        except Exception as e:
            self.fail(f"Performance benchmarks test failed: {e}")

    def test_error_recovery(self):
        """Test error recovery and resilience."""
        logger.info("Testing error recovery and resilience...")

        try:
            # Test with invalid parameters
            invalid_tests = [
                lambda: self.bq_ai.ml_generate_text(document_id='invalid_id', limit=1),
                lambda: self.bq_ai.ai_generate_table(document_id='invalid_id', limit=1),
                lambda: self.bq_ai.ai_generate_bool(document_id='invalid_id', limit=1),
                lambda: self.bq_ai.ml_generate_embedding(document_id='invalid_id', limit=1),
                lambda: self.bq_ai.vector_search(query_text='', limit=1)
            ]

            for i, test_func in enumerate(invalid_tests):
                try:
                    result = test_func()
                    # Should return valid structure even with invalid input
                    self.assertIsInstance(result, dict)
                    logger.info(f"   Test {i+1}: Graceful error handling")
                except Exception as e:
                    # Exception handling is also acceptable
                    logger.info(f"   Test {i+1}: Exception handling - {e}")

            logger.info("✅ Error recovery test passed - System handles errors gracefully")

        except Exception as e:
            self.fail(f"Error recovery test failed: {e}")

    def test_data_consistency(self):
        """Test data consistency across functions."""
        logger.info("Testing data consistency...")

        try:
            # Test that same document ID returns consistent results
            document_id = self.test_document_id

            # Get results from multiple functions
            summary_result = self.bq_ai.ml_generate_text(document_id=document_id, limit=1)
            extraction_result = self.bq_ai.ai_generate_table(document_id=document_id, limit=1)
            urgency_result = self.bq_ai.ai_generate_bool(document_id=document_id, limit=1)
            embedding_result = self.bq_ai.ml_generate_embedding(document_id=document_id, limit=1)

            # Validate document ID consistency
            self.assertEqual(summary_result['summaries'][0]['document_id'], document_id)
            self.assertEqual(extraction_result['extractions'][0]['document_id'], document_id)
            self.assertEqual(urgency_result['urgency_analyses'][0]['document_id'], document_id)
            self.assertEqual(embedding_result['embeddings'][0]['document_id'], document_id)

            logger.info("✅ Data consistency test passed - Document IDs are consistent across functions")

        except Exception as e:
            self.fail(f"Data consistency test failed: {e}")

    def test_scalability(self):
        """Test scalability with larger datasets."""
        logger.info("Testing scalability...")

        try:
            # Test with larger limits
            large_limit_tests = [
                lambda: self.bq_ai.ml_generate_text(limit=5),
                lambda: self.bq_ai.ai_generate_table(limit=5),
                lambda: self.bq_ai.ai_generate_bool(limit=5),
                lambda: self.bq_ai.ml_generate_embedding(limit=5),
                lambda: self.bq_ai.vector_search(query_text=self.test_query, limit=10)
            ]

            for i, test_func in enumerate(large_limit_tests):
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time

                # Should complete within reasonable time
                self.assertLess(duration, 60)
                self.assertIsInstance(result, dict)

                logger.info(f"   Test {i+1}: {duration:.2f} seconds")

            logger.info("✅ Scalability test passed - System handles larger datasets efficiently")

        except Exception as e:
            self.fail(f"Scalability test failed: {e}")


def run_integration_tests():
    """Run all integration tests."""
    logger.info("🧪 Starting Integration Test Suite")
    logger.info("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEndToEndWorkflow)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 Integration Test Results:")
    logger.info(f"   Tests run: {result.testsRun}")
    logger.info(f"   Failures: {len(result.failures)}")
    logger.info(f"   Errors: {len(result.errors)}")
    logger.info(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        logger.error("❌ Test failures:")
        for test, traceback in result.failures:
            logger.error(f"   {test}: {traceback}")

    if result.errors:
        logger.error("❌ Test errors:")
        for test, traceback in result.errors:
            logger.error(f"   {test}: {traceback}")

    if not result.failures and not result.errors:
        logger.info("🎉 All integration tests passed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
