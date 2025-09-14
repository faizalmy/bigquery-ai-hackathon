#!/usr/bin/env python3
"""
Track 2 Test Runner
Vector Search Functions Test Suite

This script runs all Track 2 tests:
- ML.GENERATE_EMBEDDING: Document embeddings
- VECTOR_SEARCH: Semantic similarity search

Author: Faizal
Date: September 2025
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Run Track 2 tests."""
    logger.info("🧪 Track 2: Vector Search Functions Test Suite")
    logger.info("=" * 60)

    try:
        # Import and run Track 2 tests
        from track2.test_ml_generate_embedding import run_track2_ml_generate_embedding_tests
        from track2.test_vector_search import run_track2_vector_search_tests

        # Run individual test suites
        results = {}
        results['ml_generate_embedding'] = run_track2_ml_generate_embedding_tests()
        results['vector_search'] = run_track2_vector_search_tests()

        # Calculate success rate
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100

        logger.info("=" * 60)
        logger.info(f"📊 Track 2 Results Summary:")
        logger.info(f"   ML.GENERATE_EMBEDDING: {'✅ PASS' if results['ml_generate_embedding'] else '❌ FAIL'}")
        logger.info(f"   VECTOR_SEARCH: {'✅ PASS' if results['vector_search'] else '❌ FAIL'}")
        logger.info(f"   Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")

        if success_rate == 100.0:
            logger.info("🎉 All Track 2 tests passed!")
            return True
        else:
            logger.error("❌ Some Track 2 tests failed.")
            return False

    except Exception as e:
        logger.error(f"❌ Track 2 test suite failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
