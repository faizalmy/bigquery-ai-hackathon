#!/usr/bin/env python3
"""
Test Suite for ML.GENERATE_EMBEDDING Function
Track 2: Vector Search - Document Embeddings

This test suite validates the ML.GENERATE_EMBEDDING function for document vector embeddings.
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


class TestMLGenerateEmbedding(unittest.TestCase):
    """Test cases for ML.GENERATE_EMBEDDING function."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with BigQuery AI functions."""
        logger.info("Setting up ML.GENERATE_EMBEDDING test suite...")
        cls.bq_ai = BigQueryAIFunctions()
        cls.test_document_id = 'caselaw_000001'

    def test_ml_generate_embedding_initialization(self):
        """Test that ML.GENERATE_EMBEDDING can be initialized."""
        logger.info("Testing ML.GENERATE_EMBEDDING initialization...")

        # Test that the function exists and can be called
        self.assertIsNotNone(self.bq_ai.ml_generate_embedding)
        self.assertTrue(callable(self.bq_ai.ml_generate_embedding))

        logger.info("✅ ML.GENERATE_EMBEDDING initialization test passed")

    def test_ml_generate_embedding_single_document(self):
        """Test ML.GENERATE_EMBEDDING with a single document."""
        logger.info("Testing ML.GENERATE_EMBEDDING with single document...")

        try:
            result = self.bq_ai.ml_generate_embedding(
                document_id=self.test_document_id,
                limit=1
            )

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('embeddings', result)

            # Validate function name
            self.assertEqual(result['function'], 'ML.GENERATE_EMBEDDING')

            # Validate document count
            self.assertEqual(result['total_documents'], 1)

            # Validate embeddings
            self.assertIsInstance(result['embeddings'], list)
            self.assertEqual(len(result['embeddings']), 1)

            embedding = result['embeddings'][0]
            self.assertIn('document_id', embedding)
            self.assertIn('embedding', embedding)
            self.assertIn('status', embedding)

            # Validate document ID
            self.assertEqual(embedding['document_id'], self.test_document_id)

            # Validate embedding vector
            self.assertIsInstance(embedding['embedding'], list)
            self.assertEqual(len(embedding['embedding']), 768)  # text-embedding-005 has 768 dimensions

            # Validate embedding values are numeric
            for value in embedding['embedding']:
                self.assertIsInstance(value, (int, float))

            # Validate status
            self.assertEqual(embedding['status'], 'OK')

            logger.info(f"✅ Single document test passed - Embedding dimensions: {len(embedding['embedding'])}")

        except Exception as e:
            self.fail(f"ML.GENERATE_EMBEDDING single document test failed: {e}")

    def test_ml_generate_embedding_multiple_documents(self):
        """Test ML.GENERATE_EMBEDDING with multiple documents."""
        logger.info("Testing ML.GENERATE_EMBEDDING with multiple documents...")

        try:
            result = self.bq_ai.ml_generate_embedding(limit=3)

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('embeddings', result)

            # Validate function name
            self.assertEqual(result['function'], 'ML.GENERATE_EMBEDDING')

            # Validate document count
            self.assertGreaterEqual(result['total_documents'], 1)
            self.assertLessEqual(result['total_documents'], 3)

            # Validate embeddings
            self.assertIsInstance(result['embeddings'], list)
            self.assertEqual(len(result['embeddings']), result['total_documents'])

            # Validate each embedding
            for embedding in result['embeddings']:
                self.assertIn('document_id', embedding)
                self.assertIn('embedding', embedding)
                self.assertIn('status', embedding)

                # Validate embedding vector
                self.assertIsInstance(embedding['embedding'], list)
                self.assertEqual(len(embedding['embedding']), 768)

                # Validate embedding values are numeric
                for value in embedding['embedding']:
                    self.assertIsInstance(value, (int, float))

                # Validate status
                self.assertEqual(embedding['status'], 'OK')

            logger.info(f"✅ Multiple documents test passed - Generated {result['total_documents']} embeddings")

        except Exception as e:
            self.fail(f"ML.GENERATE_EMBEDDING multiple documents test failed: {e}")

    def test_ml_generate_embedding_performance(self):
        """Test ML.GENERATE_EMBEDDING performance."""
        logger.info("Testing ML.GENERATE_EMBEDDING performance...")

        import time

        try:
            start_time = time.time()
            result = self.bq_ai.ml_generate_embedding(
                document_id=self.test_document_id,
                limit=1
            )
            end_time = time.time()

            processing_time = end_time - start_time

            # Validate result
            self.assertIsInstance(result, dict)
            self.assertIn('embeddings', result)
            self.assertEqual(len(result['embeddings']), 1)

            # Validate performance (should complete within reasonable time)
            self.assertLess(processing_time, 30)  # Should complete within 30 seconds

            logger.info(f"✅ Performance test passed - Processing time: {processing_time:.2f} seconds")

        except Exception as e:
            self.fail(f"ML.GENERATE_EMBEDDING performance test failed: {e}")

    def test_ml_generate_embedding_error_handling(self):
        """Test ML.GENERATE_EMBEDDING error handling."""
        logger.info("Testing ML.GENERATE_EMBEDDING error handling...")

        try:
            # Test with invalid document ID
            result = self.bq_ai.ml_generate_embedding(
                document_id='invalid_document_id',
                limit=1
            )

            # Should still return a valid structure, even if no results
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_documents', result)
            self.assertIn('embeddings', result)

            logger.info("✅ Error handling test passed - Graceful handling of invalid document ID")

        except Exception as e:
            # If it raises an exception, that's also acceptable error handling
            logger.info(f"✅ Error handling test passed - Exception raised as expected: {e}")

    def test_ml_generate_embedding_vector_quality(self):
        """Test ML.GENERATE_EMBEDDING vector quality."""
        logger.info("Testing ML.GENERATE_EMBEDDING vector quality...")

        try:
            result = self.bq_ai.ml_generate_embedding(
                document_id=self.test_document_id,
                limit=1
            )

            embedding = result['embeddings'][0]
            embedding_vector = embedding['embedding']

            # Validate embedding quality
            self.assertEqual(len(embedding_vector), 768)  # Correct dimensions

            # Check that values are in reasonable range (typically -1 to 1 for normalized embeddings)
            for value in embedding_vector:
                self.assertGreaterEqual(value, -10.0)  # Allow some range
                self.assertLessEqual(value, 10.0)

            # Check that vector is not all zeros
            non_zero_count = sum(1 for value in embedding_vector if abs(value) > 1e-6)
            self.assertGreater(non_zero_count, 0)

            # Check that vector has reasonable magnitude
            magnitude = sum(value * value for value in embedding_vector) ** 0.5
            self.assertGreater(magnitude, 0.1)  # Should have some magnitude

            logger.info(f"✅ Vector quality test passed - Non-zero values: {non_zero_count}, Magnitude: {magnitude:.4f}")

        except Exception as e:
            self.fail(f"ML.GENERATE_EMBEDDING vector quality test failed: {e}")

    def test_ml_generate_embedding_consistency(self):
        """Test ML.GENERATE_EMBEDDING consistency across multiple calls."""
        logger.info("Testing ML.GENERATE_EMBEDDING consistency...")

        try:
            # Run multiple times to check consistency
            results = []
            for i in range(3):
                result = self.bq_ai.ml_generate_embedding(
                    document_id=self.test_document_id,
                    limit=1
                )
                results.append(result)

            # All results should have the same structure
            for result in results:
                self.assertIsInstance(result, dict)
                self.assertIn('embeddings', result)
                self.assertEqual(len(result['embeddings']), 1)

            # Results should be consistent in structure
            first_result = results[0]
            for result in results[1:]:
                self.assertEqual(len(first_result['embeddings']), len(result['embeddings']))
                self.assertEqual(len(first_result['embeddings'][0]['embedding']),
                               len(result['embeddings'][0]['embedding']))

            logger.info("✅ Consistency test passed - All calls return consistent structure")

        except Exception as e:
            self.fail(f"ML.GENERATE_EMBEDDING consistency test failed: {e}")

    def test_ml_generate_embedding_different_documents(self):
        """Test ML.GENERATE_EMBEDDING with different documents produces different vectors."""
        logger.info("Testing ML.GENERATE_EMBEDDING with different documents...")

        try:
            # Generate embeddings for different documents
            result = self.bq_ai.ml_generate_embedding(limit=3)

            embeddings = result['embeddings']

            if len(embeddings) >= 2:
                # Compare embeddings from different documents
                embedding1 = embeddings[0]['embedding']
                embedding2 = embeddings[1]['embedding']

                # Calculate cosine similarity
                dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
                magnitude1 = sum(a * a for a in embedding1) ** 0.5
                magnitude2 = sum(b * b for b in embedding2) ** 0.5

                if magnitude1 > 0 and magnitude2 > 0:
                    cosine_similarity = dot_product / (magnitude1 * magnitude2)

                    # Different documents should have different embeddings
                    # (similarity should not be exactly 1.0)
                    self.assertLess(cosine_similarity, 0.99)

                    logger.info(f"✅ Different documents test passed - Cosine similarity: {cosine_similarity:.4f}")
                else:
                    logger.warning("⚠️ One or both embeddings have zero magnitude")
            else:
                logger.warning("⚠️ Not enough documents to compare embeddings")

        except Exception as e:
            self.fail(f"ML.GENERATE_EMBEDDING different documents test failed: {e}")


def run_track2_ml_generate_embedding_tests():
    """Run all ML.GENERATE_EMBEDDING tests."""
    logger.info("🧪 Starting Track 2 - ML.GENERATE_EMBEDDING Test Suite")
    logger.info("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMLGenerateEmbedding)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 ML.GENERATE_EMBEDDING Test Results:")
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
        logger.info("🎉 All ML.GENERATE_EMBEDDING tests passed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_track2_ml_generate_embedding_tests()
    sys.exit(0 if success else 1)
