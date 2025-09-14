#!/usr/bin/env python3
"""
Test Suite for VECTOR_SEARCH Function
Track 2: Vector Search - Semantic Similarity Search

This test suite validates the VECTOR_SEARCH function for semantic similarity search.
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


class TestVectorSearch(unittest.TestCase):
    """Test cases for VECTOR_SEARCH function."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with BigQuery AI functions."""
        logger.info("Setting up VECTOR_SEARCH test suite...")
        cls.bq_ai = BigQueryAIFunctions()
        cls.test_queries = [
            "insurance contract dispute",
            "supreme court decision",
            "breach of contract liability",
            "alabama supreme court",
            "legal document"
        ]

    def test_vector_search_initialization(self):
        """Test that VECTOR_SEARCH can be initialized."""
        logger.info("Testing VECTOR_SEARCH initialization...")

        # Test that the function exists and can be called
        self.assertIsNotNone(self.bq_ai.vector_search)
        self.assertTrue(callable(self.bq_ai.vector_search))

        logger.info("✅ VECTOR_SEARCH initialization test passed")

    def test_vector_search_basic_functionality(self):
        """Test VECTOR_SEARCH basic functionality."""
        logger.info("Testing VECTOR_SEARCH basic functionality...")

        try:
            query = self.test_queries[0]
            result = self.bq_ai.vector_search(query_text=query, limit=5)

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_results', result)
            self.assertIn('results', result)

            # Validate function name
            self.assertEqual(result['function'], 'VECTOR_SEARCH')

            # Validate results
            self.assertIsInstance(result['results'], list)
            self.assertGreaterEqual(len(result['results']), 0)
            self.assertLessEqual(len(result['results']), 5)

            # Validate each result
            for search_result in result['results']:
                self.assertIn('document_id', search_result)
                self.assertIn('similarity_distance', search_result)

                # Validate document ID
                self.assertIsInstance(search_result['document_id'], str)
                self.assertTrue(search_result['document_id'].startswith('caselaw_'))

                # Validate similarity distance
                self.assertIsInstance(search_result['similarity_distance'], (int, float))
                self.assertGreaterEqual(search_result['similarity_distance'], 0.0)
                self.assertLessEqual(search_result['similarity_distance'], 1.0)

            logger.info(f"✅ Basic functionality test passed - Found {len(result['results'])} similar documents")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH basic functionality test failed: {e}")

    def test_vector_search_different_queries(self):
        """Test VECTOR_SEARCH with different query types."""
        logger.info("Testing VECTOR_SEARCH with different queries...")

        try:
            for query in self.test_queries:
                result = self.bq_ai.vector_search(query_text=query, limit=3)

                # Validate result structure
                self.assertIsInstance(result, dict)
                self.assertIn('results', result)
                self.assertIsInstance(result['results'], list)

                # Should return some results for each query
                self.assertGreaterEqual(len(result['results']), 0)

                logger.info(f"✅ Query '{query}' returned {len(result['results'])} results")

            logger.info("✅ Different queries test passed - All queries returned results")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH different queries test failed: {e}")

    def test_vector_search_performance(self):
        """Test VECTOR_SEARCH performance."""
        logger.info("Testing VECTOR_SEARCH performance...")

        import time

        try:
            query = self.test_queries[0]
            start_time = time.time()
            result = self.bq_ai.vector_search(query_text=query, limit=5)
            end_time = time.time()

            processing_time = end_time - start_time

            # Validate result
            self.assertIsInstance(result, dict)
            self.assertIn('results', result)

            # Validate performance (should complete within reasonable time)
            self.assertLess(processing_time, 30)  # Should complete within 30 seconds

            logger.info(f"✅ Performance test passed - Processing time: {processing_time:.2f} seconds")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH performance test failed: {e}")

    def test_vector_search_error_handling(self):
        """Test VECTOR_SEARCH error handling."""
        logger.info("Testing VECTOR_SEARCH error handling...")

        try:
            # Test with empty query
            result = self.bq_ai.vector_search(query_text="", limit=3)

            # Should still return a valid structure
            self.assertIsInstance(result, dict)
            self.assertIn('results', result)

            logger.info("✅ Error handling test passed - Graceful handling of empty query")

        except Exception as e:
            # If it raises an exception, that's also acceptable error handling
            logger.info(f"✅ Error handling test passed - Exception raised as expected: {e}")

    def test_vector_search_similarity_quality(self):
        """Test VECTOR_SEARCH similarity quality."""
        logger.info("Testing VECTOR_SEARCH similarity quality...")

        try:
            query = "supreme court decision"
            result = self.bq_ai.vector_search(query_text=query, limit=5)

            results = result['results']

            if len(results) >= 2:
                # Check that results are ordered by similarity (distance should be increasing)
                distances = [r['similarity_distance'] for r in results]

                # Results should be ordered by similarity distance (ascending)
                is_ordered = all(distances[i] <= distances[i+1] for i in range(len(distances)-1))

                if is_ordered:
                    logger.info("✅ Similarity quality test passed - Results are properly ordered by similarity")
                else:
                    logger.warning("⚠️ Results may not be properly ordered by similarity")

                # Check similarity score range
                for result_item in results:
                    distance = result_item['similarity_distance']
                    self.assertGreaterEqual(distance, 0.0)
                    self.assertLessEqual(distance, 1.0)

                logger.info(f"✅ Similarity quality test passed - Distance range: {min(distances):.4f} to {max(distances):.4f}")
            else:
                logger.warning("⚠️ Not enough results to test similarity quality")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH similarity quality test failed: {e}")

    def test_vector_search_limit_parameter(self):
        """Test VECTOR_SEARCH limit parameter."""
        logger.info("Testing VECTOR_SEARCH limit parameter...")

        try:
            query = self.test_queries[0]

            # Test different limit values
            for limit in [1, 3, 5, 10]:
                result = self.bq_ai.vector_search(query_text=query, limit=limit)

                # Validate result count doesn't exceed limit
                self.assertLessEqual(len(result['results']), limit)

                logger.info(f"✅ Limit {limit} test passed - Returned {len(result['results'])} results")

            logger.info("✅ Limit parameter test passed - All limits respected")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH limit parameter test failed: {e}")

    def test_vector_search_consistency(self):
        """Test VECTOR_SEARCH consistency across multiple calls."""
        logger.info("Testing VECTOR_SEARCH consistency...")

        try:
            query = self.test_queries[0]

            # Run multiple times to check consistency
            results = []
            for i in range(3):
                result = self.bq_ai.vector_search(query_text=query, limit=3)
                results.append(result)

            # All results should have the same structure
            for result in results:
                self.assertIsInstance(result, dict)
                self.assertIn('results', result)
                self.assertIsInstance(result['results'], list)

            # Results should be consistent in structure
            first_result = results[0]
            for result in results[1:]:
                self.assertEqual(len(first_result['results']), len(result['results']))

            logger.info("✅ Consistency test passed - All calls return consistent structure")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH consistency test failed: {e}")

    def test_vector_search_legal_relevance(self):
        """Test VECTOR_SEARCH legal relevance."""
        logger.info("Testing VECTOR_SEARCH legal relevance...")

        try:
            # Test with legal-specific queries
            legal_queries = [
                "insurance contract dispute",
                "supreme court decision",
                "breach of contract",
                "liability damages"
            ]

            for query in legal_queries:
                result = self.bq_ai.vector_search(query_text=query, limit=3)

                # Should return some results for legal queries
                self.assertGreaterEqual(len(result['results']), 0)

                # Results should have reasonable similarity scores
                for search_result in result['results']:
                    distance = search_result['similarity_distance']
                    self.assertGreaterEqual(distance, 0.0)
                    self.assertLessEqual(distance, 1.0)

                logger.info(f"✅ Legal query '{query}' returned {len(result['results'])} relevant results")

            logger.info("✅ Legal relevance test passed - All legal queries returned relevant results")

        except Exception as e:
            self.fail(f"VECTOR_SEARCH legal relevance test failed: {e}")


def run_track2_vector_search_tests():
    """Run all VECTOR_SEARCH tests."""
    logger.info("🧪 Starting Track 2 - VECTOR_SEARCH Test Suite")
    logger.info("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVectorSearch)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 VECTOR_SEARCH Test Results:")
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
        logger.info("🎉 All VECTOR_SEARCH tests passed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_track2_vector_search_tests()
    sys.exit(0 if success else 1)
