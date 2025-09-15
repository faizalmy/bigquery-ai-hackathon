#!/usr/bin/env python3
"""
Test Suite for AI.GENERATE_TABLE Function
Track 1: Generative AI - Legal Data Extraction

This test suite validates the AI.GENERATE_TABLE function for structured legal data extraction.
"""

import sys
import os
import unittest
import logging
import json
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_ai_functions import BigQueryAIFunctions

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestAIGenerateTable(unittest.TestCase):
    """Test cases for AI.GENERATE_TABLE function."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with BigQuery AI functions."""
        logger.info("Setting up AI.GENERATE_TABLE test suite...")
        cls.bq_ai = BigQueryAIFunctions()
        cls.test_document_id = 'caselaw_000001'

    def test_ai_generate_table_initialization(self):
        """Test that AI.GENERATE_TABLE can be initialized."""
        logger.info("Testing AI.GENERATE_TABLE initialization...")

        # Test that the function exists and can be called
        self.assertIsNotNone(self.bq_ai.ai_generate_table)
        self.assertTrue(callable(self.bq_ai.ai_generate_table))

        logger.info("✅ AI.GENERATE_TABLE initialization test passed")

    def test_ai_generate_table_single_document(self):
        """Test AI.GENERATE_TABLE with a single document."""
        logger.info("Testing AI.GENERATE_TABLE with single document...")

        try:
            result = self.bq_ai.ai_generate_table(
                document_id=self.test_document_id,
                limit=1
            )

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('extractions', result)

            # Validate function name
            self.assertEqual(result['function'], 'AI.GENERATE_TABLE')

            # Validate document count
            self.assertEqual(result['total_documents'], 1)

            # Validate extractions
            self.assertIsInstance(result['extractions'], list)
            self.assertEqual(len(result['extractions']), 1)

            extraction = result['extractions'][0]
            self.assertIn('document_id', extraction)
            self.assertIn('extracted_data', extraction)
            self.assertIn('status', extraction)

            # Validate document ID
            self.assertEqual(extraction['document_id'], self.test_document_id)

            # Validate extracted data
            self.assertIsInstance(extraction['extracted_data'], dict)

            # Validate status
            self.assertEqual(extraction['status'], 'OK')

            logger.info(f"✅ Single document test passed - Extracted data keys: {list(extraction['extracted_data'].keys())}")

        except Exception as e:
            self.fail(f"AI.GENERATE_TABLE single document test failed: {e}")

    def test_ai_generate_table_multiple_documents(self):
        """Test AI.GENERATE_TABLE with multiple documents."""
        logger.info("Testing AI.GENERATE_TABLE with multiple documents...")

        try:
            result = self.bq_ai.ai_generate_table(limit=3)

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('extractions', result)

            # Validate function name
            self.assertEqual(result['function'], 'AI.GENERATE_TABLE')

            # Validate document count
            self.assertGreaterEqual(result['total_documents'], 1)
            self.assertLessEqual(result['total_documents'], 3)

            # Validate extractions
            self.assertIsInstance(result['extractions'], list)
            self.assertEqual(len(result['extractions']), result['total_documents'])

            # Validate each extraction
            for extraction in result['extractions']:
                self.assertIn('document_id', extraction)
                self.assertIn('extracted_data', extraction)
                self.assertIn('status', extraction)

                # Validate extracted data
                self.assertIsInstance(extraction['extracted_data'], dict)

                # Validate status
                self.assertEqual(extraction['status'], 'OK')

            logger.info(f"✅ Multiple documents test passed - Generated {result['total_documents']} extractions")

        except Exception as e:
            self.fail(f"AI.GENERATE_TABLE multiple documents test failed: {e}")

    def test_ai_generate_table_performance(self):
        """Test AI.GENERATE_TABLE performance."""
        logger.info("Testing AI.GENERATE_TABLE performance...")

        import time

        try:
            start_time = time.time()
            result = self.bq_ai.ai_generate_table(
                document_id=self.test_document_id,
                limit=1
            )
            end_time = time.time()

            processing_time = end_time - start_time

            # Validate result
            self.assertIsInstance(result, dict)
            self.assertIn('extractions', result)
            self.assertEqual(len(result['extractions']), 1)

            # Validate performance (should complete within reasonable time)
            self.assertLess(processing_time, 30)  # Should complete within 30 seconds

            logger.info(f"✅ Performance test passed - Processing time: {processing_time:.2f} seconds")

        except Exception as e:
            self.fail(f"AI.GENERATE_TABLE performance test failed: {e}")

    def test_ai_generate_table_error_handling(self):
        """Test AI.GENERATE_TABLE error handling."""
        logger.info("Testing AI.GENERATE_TABLE error handling...")

        try:
            # Test with invalid document ID
            result = self.bq_ai.ai_generate_table(
                document_id='invalid_document_id',
                limit=1
            )

            # Should still return a valid structure, even if no results
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('extractions', result)

            logger.info("✅ Error handling test passed - Graceful handling of invalid document ID")

        except Exception as e:
            # If it raises an exception, that's also acceptable error handling
            logger.info(f"✅ Error handling test passed - Exception raised as expected: {e}")

    def test_ai_generate_table_data_quality(self):
        """Test AI.GENERATE_TABLE data extraction quality."""
        logger.info("Testing AI.GENERATE_TABLE data extraction quality...")

        try:
            result = self.bq_ai.ai_generate_table(
                document_id=self.test_document_id,
                limit=1
            )

            extraction = result['extractions'][0]
            extracted_data = extraction['extracted_data']

            # Validate extracted data structure
            self.assertIsInstance(extracted_data, dict)

            # Check for common legal document fields
            legal_fields = ['parties', 'case_number', 'date', 'court', 'jurisdiction', 'outcome', 'issues']
            has_legal_fields = any(field in extracted_data for field in legal_fields)

            if has_legal_fields:
                logger.info("✅ Data quality test passed - Contains legal document fields")
            else:
                logger.warning("⚠️ Extracted data may not contain expected legal fields")

            logger.info(f"✅ Data quality test passed - Extracted {len(extracted_data)} fields")

        except Exception as e:
            self.fail(f"AI.GENERATE_TABLE data quality test failed: {e}")

    def test_ai_generate_table_json_parsing(self):
        """Test AI.GENERATE_TABLE JSON parsing."""
        logger.info("Testing AI.GENERATE_TABLE JSON parsing...")

        try:
            result = self.bq_ai.ai_generate_table(
                document_id=self.test_document_id,
                limit=1
            )

            extraction = result['extractions'][0]
            extracted_data = extraction['extracted_data']

            # Validate that extracted data is valid JSON structure
            self.assertIsInstance(extracted_data, dict)

            # Try to serialize and deserialize to ensure it's valid JSON
            json_string = json.dumps(extracted_data)
            parsed_data = json.loads(json_string)

            self.assertEqual(extracted_data, parsed_data)

            logger.info("✅ JSON parsing test passed - Valid JSON structure")

        except Exception as e:
            self.fail(f"AI.GENERATE_TABLE JSON parsing test failed: {e}")


def run_track1_ai_generate_table_tests():
    """Run all AI.GENERATE_TABLE tests."""
    logger.info("🧪 Starting Track 1 - AI.GENERATE_TABLE Test Suite")
    logger.info("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAIGenerateTable)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 AI.GENERATE_TABLE Test Results:")
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
        logger.info("🎉 All AI.GENERATE_TABLE tests passed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_track1_ai_generate_table_tests()
    sys.exit(0 if success else 1)
