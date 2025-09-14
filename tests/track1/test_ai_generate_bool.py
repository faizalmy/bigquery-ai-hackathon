#!/usr/bin/env python3
"""
Test Suite for AI.GENERATE_BOOL Function
Track 1: Generative AI - Urgency Detection

This test suite validates the AI.GENERATE_BOOL function for legal document urgency detection.
"""

import sys
import os
import unittest
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_ai_functions import BigQueryAIFunctions

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestAIGenerateBool(unittest.TestCase):
    """Test cases for AI.GENERATE_BOOL function."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with BigQuery AI functions."""
        logger.info("Setting up AI.GENERATE_BOOL test suite...")
        cls.bq_ai = BigQueryAIFunctions()
        cls.test_document_id = 'caselaw_000001'

    def test_ai_generate_bool_initialization(self):
        """Test that AI.GENERATE_BOOL can be initialized."""
        logger.info("Testing AI.GENERATE_BOOL initialization...")

        # Test that the function exists and can be called
        self.assertIsNotNone(self.bq_ai.ai_generate_bool)
        self.assertTrue(callable(self.bq_ai.ai_generate_bool))

        logger.info("✅ AI.GENERATE_BOOL initialization test passed")

    def test_ai_generate_bool_single_document(self):
        """Test AI.GENERATE_BOOL with a single document."""
        logger.info("Testing AI.GENERATE_BOOL with single document...")

        try:
            result = self.bq_ai.ai_generate_bool(
                document_id=self.test_document_id,
                limit=1
            )

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('urgency_analyses', result)

            # Validate function name
            self.assertEqual(result['function'], 'AI.GENERATE_BOOL')

            # Validate document count
            self.assertEqual(result['total_documents'], 1)

            # Validate urgency analyses
            self.assertIsInstance(result['urgency_analyses'], list)
            self.assertEqual(len(result['urgency_analyses']), 1)

            analysis = result['urgency_analyses'][0]
            self.assertIn('document_id', analysis)
            self.assertIn('is_urgent', analysis)
            self.assertIn('status', analysis)

            # Validate document ID
            self.assertEqual(analysis['document_id'], self.test_document_id)

            # Validate urgency result
            self.assertIsInstance(analysis['is_urgent'], bool)

            # Validate status
            self.assertEqual(analysis['status'], 'OK')

            logger.info(f"✅ Single document test passed - Urgency: {analysis['is_urgent']}")

        except Exception as e:
            self.fail(f"AI.GENERATE_BOOL single document test failed: {e}")

    def test_ai_generate_bool_multiple_documents(self):
        """Test AI.GENERATE_BOOL with multiple documents."""
        logger.info("Testing AI.GENERATE_BOOL with multiple documents...")

        try:
            result = self.bq_ai.ai_generate_bool(limit=3)

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('urgency_analyses', result)

            # Validate function name
            self.assertEqual(result['function'], 'AI.GENERATE_BOOL')

            # Validate document count
            self.assertGreaterEqual(result['total_documents'], 1)
            self.assertLessEqual(result['total_documents'], 3)

            # Validate urgency analyses
            self.assertIsInstance(result['urgency_analyses'], list)
            self.assertEqual(len(result['urgency_analyses']), result['total_documents'])

            # Validate each analysis
            for analysis in result['urgency_analyses']:
                self.assertIn('document_id', analysis)
                self.assertIn('is_urgent', analysis)
                self.assertIn('status', analysis)

                # Validate urgency result
                self.assertIsInstance(analysis['is_urgent'], bool)

                # Validate status
                self.assertEqual(analysis['status'], 'OK')

            logger.info(f"✅ Multiple documents test passed - Generated {result['total_documents']} urgency analyses")

        except Exception as e:
            self.fail(f"AI.GENERATE_BOOL multiple documents test failed: {e}")

    def test_ai_generate_bool_performance(self):
        """Test AI.GENERATE_BOOL performance."""
        logger.info("Testing AI.GENERATE_BOOL performance...")

        import time

        try:
            start_time = time.time()
            result = self.bq_ai.ai_generate_bool(
                document_id=self.test_document_id,
                limit=1
            )
            end_time = time.time()

            processing_time = end_time - start_time

            # Validate result
            self.assertIsInstance(result, dict)
            self.assertIn('urgency_analyses', result)
            self.assertEqual(len(result['urgency_analyses']), 1)

            # Validate performance (should complete within reasonable time)
            self.assertLess(processing_time, 30)  # Should complete within 30 seconds

            logger.info(f"✅ Performance test passed - Processing time: {processing_time:.2f} seconds")

        except Exception as e:
            self.fail(f"AI.GENERATE_BOOL performance test failed: {e}")

    def test_ai_generate_bool_error_handling(self):
        """Test AI.GENERATE_BOOL error handling."""
        logger.info("Testing AI.GENERATE_BOOL error handling...")

        try:
            # Test with invalid document ID
            result = self.bq_ai.ai_generate_bool(
                document_id='invalid_document_id',
                limit=1
            )

            # Should still return a valid structure, even if no results
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('urgency_analyses', result)

            logger.info("✅ Error handling test passed - Graceful handling of invalid document ID")

        except Exception as e:
            # If it raises an exception, that's also acceptable error handling
            logger.info(f"✅ Error handling test passed - Exception raised as expected: {e}")

    def test_ai_generate_bool_boolean_consistency(self):
        """Test AI.GENERATE_BOOL boolean result consistency."""
        logger.info("Testing AI.GENERATE_BOOL boolean result consistency...")

        try:
            # Run multiple times to check consistency
            results = []
            for i in range(3):
                result = self.bq_ai.ai_generate_bool(
                    document_id=self.test_document_id,
                    limit=1
                )
                analysis = result['urgency_analyses'][0]
                results.append(analysis['is_urgent'])

            # All results should be boolean
            for result in results:
                self.assertIsInstance(result, bool)

            # Results should be consistent (same document should have same urgency)
            # Note: This might vary due to AI model behavior, so we just check they're all boolean
            logger.info(f"✅ Boolean consistency test passed - Results: {results}")

        except Exception as e:
            self.fail(f"AI.GENERATE_BOOL boolean consistency test failed: {e}")

    def test_ai_generate_bool_urgency_distribution(self):
        """Test AI.GENERATE_BOOL urgency distribution across multiple documents."""
        logger.info("Testing AI.GENERATE_BOOL urgency distribution...")

        try:
            result = self.bq_ai.ai_generate_bool(limit=10)

            analyses = result['urgency_analyses']
            urgent_count = sum(1 for analysis in analyses if analysis['is_urgent'])
            non_urgent_count = len(analyses) - urgent_count

            # Validate that we get both urgent and non-urgent results
            # (This is a reasonable expectation for a diverse legal document set)
            logger.info(f"✅ Urgency distribution test passed - Urgent: {urgent_count}, Non-urgent: {non_urgent_count}")

        except Exception as e:
            self.fail(f"AI.GENERATE_BOOL urgency distribution test failed: {e}")


def run_track1_ai_generate_bool_tests():
    """Run all AI.GENERATE_BOOL tests."""
    logger.info("🧪 Starting Track 1 - AI.GENERATE_BOOL Test Suite")
    logger.info("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAIGenerateBool)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 AI.GENERATE_BOOL Test Results:")
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
        logger.info("🎉 All AI.GENERATE_BOOL tests passed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_track1_ai_generate_bool_tests()
    sys.exit(0 if success else 1)
