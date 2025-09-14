#!/usr/bin/env python3
"""
Track 1 Test Runner
Generative AI Functions Test Suite

This script runs all Track 1 tests:
- ML.GENERATE_TEXT: Document summarization
- AI.GENERATE_TABLE: Legal data extraction
- AI.GENERATE_BOOL: Urgency detection
- ML.FORECAST: Case outcome prediction

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
    """Run Track 1 tests."""
    logger.info("🧪 Track 1: Generative AI Functions Test Suite")
    logger.info("=" * 60)

    try:
        # Import and run Track 1 tests
        from track1.test_ml_generate_text import run_track1_ml_generate_text_tests
        from track1.test_ai_generate_table import run_track1_ai_generate_table_tests
        from track1.test_ai_generate_bool import run_track1_ai_generate_bool_tests
        from track1.test_ml_forecast import run_track1_ml_forecast_tests

        # Run individual test suites
        results = {}
        results['ml_generate_text'] = run_track1_ml_generate_text_tests()
        results['ai_generate_table'] = run_track1_ai_generate_table_tests()
        results['ai_generate_bool'] = run_track1_ai_generate_bool_tests()
        results['ml_forecast'] = run_track1_ml_forecast_tests()

        # Calculate success rate
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100

        logger.info("=" * 60)
        logger.info(f"📊 Track 1 Results Summary:")
        logger.info(f"   ML.GENERATE_TEXT: {'✅ PASS' if results['ml_generate_text'] else '❌ FAIL'}")
        logger.info(f"   AI.GENERATE_TABLE: {'✅ PASS' if results['ai_generate_table'] else '❌ FAIL'}")
        logger.info(f"   AI.GENERATE_BOOL: {'✅ PASS' if results['ai_generate_bool'] else '❌ FAIL'}")
        logger.info(f"   ML.FORECAST: {'✅ PASS' if results['ml_forecast'] else '❌ FAIL'}")
        logger.info(f"   Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")

        if success_rate == 100.0:
            logger.info("🎉 All Track 1 tests passed!")
            return True
        else:
            logger.error("❌ Some Track 1 tests failed.")
            return False

    except Exception as e:
        logger.error(f"❌ Track 1 test suite failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
