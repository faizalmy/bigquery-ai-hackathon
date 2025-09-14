#!/usr/bin/env python3
"""
Comprehensive Test Runner for BigQuery AI Legal Document Intelligence Platform

This script runs all test suites:
- Track 1: Generative AI Functions
- Track 2: Vector Search Functions
- Integration: End-to-End Workflows

Author: Faizal
Date: September 2025
Competition: BigQuery AI Hackathon
"""

import sys
import os
import logging
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_track1_tests():
    """Run all Track 1 (Generative AI) tests."""
    logger.info("🚀 Starting Track 1: Generative AI Functions Test Suite")
    logger.info("=" * 80)

    track1_results = {}

    try:
        # Import and run Track 1 tests
        from track1.test_ml_generate_text import run_track1_ml_generate_text_tests
        from track1.test_ai_generate_table import run_track1_ai_generate_table_tests
        from track1.test_ai_generate_bool import run_track1_ai_generate_bool_tests
        from track1.test_ml_forecast import run_track1_ml_forecast_tests

        # Run individual test suites
        track1_results['ml_generate_text'] = run_track1_ml_generate_text_tests()
        track1_results['ai_generate_table'] = run_track1_ai_generate_table_tests()
        track1_results['ai_generate_bool'] = run_track1_ai_generate_bool_tests()
        track1_results['ml_forecast'] = run_track1_ml_forecast_tests()

        # Calculate Track 1 success rate
        track1_success_count = sum(1 for success in track1_results.values() if success)
        track1_total_count = len(track1_results)
        track1_success_rate = (track1_success_count / track1_total_count) * 100

        logger.info("=" * 80)
        logger.info(f"📊 Track 1 Results Summary:")
        logger.info(f"   ML.GENERATE_TEXT: {'✅ PASS' if track1_results['ml_generate_text'] else '❌ FAIL'}")
        logger.info(f"   AI.GENERATE_TABLE: {'✅ PASS' if track1_results['ai_generate_table'] else '❌ FAIL'}")
        logger.info(f"   AI.GENERATE_BOOL: {'✅ PASS' if track1_results['ai_generate_bool'] else '❌ FAIL'}")
        logger.info(f"   ML.FORECAST: {'✅ PASS' if track1_results['ml_forecast'] else '❌ FAIL'}")
        logger.info(f"   Success Rate: {track1_success_rate:.1f}% ({track1_success_count}/{track1_total_count})")

        return track1_success_rate == 100.0

    except Exception as e:
        logger.error(f"❌ Track 1 test suite failed: {e}")
        return False


def run_track2_tests():
    """Run all Track 2 (Vector Search) tests."""
    logger.info("🚀 Starting Track 2: Vector Search Functions Test Suite")
    logger.info("=" * 80)

    track2_results = {}

    try:
        # Import and run Track 2 tests
        from track2.test_ml_generate_embedding import run_track2_ml_generate_embedding_tests
        from track2.test_vector_search import run_track2_vector_search_tests

        # Run individual test suites
        track2_results['ml_generate_embedding'] = run_track2_ml_generate_embedding_tests()
        track2_results['vector_search'] = run_track2_vector_search_tests()

        # Calculate Track 2 success rate
        track2_success_count = sum(1 for success in track2_results.values() if success)
        track2_total_count = len(track2_results)
        track2_success_rate = (track2_success_count / track2_total_count) * 100

        logger.info("=" * 80)
        logger.info(f"📊 Track 2 Results Summary:")
        logger.info(f"   ML.GENERATE_EMBEDDING: {'✅ PASS' if track2_results['ml_generate_embedding'] else '❌ FAIL'}")
        logger.info(f"   VECTOR_SEARCH: {'✅ PASS' if track2_results['vector_search'] else '❌ FAIL'}")
        logger.info(f"   Success Rate: {track2_success_rate:.1f}% ({track2_success_count}/{track2_total_count})")

        return track2_success_rate == 100.0

    except Exception as e:
        logger.error(f"❌ Track 2 test suite failed: {e}")
        return False


def run_integration_tests():
    """Run all integration tests."""
    logger.info("🚀 Starting Integration Test Suite")
    logger.info("=" * 80)

    try:
        # Import and run integration tests
        from integration.test_end_to_end_workflow import run_integration_tests

        # Run integration test suite
        integration_success = run_integration_tests()

        logger.info("=" * 80)
        logger.info(f"📊 Integration Results Summary:")
        logger.info(f"   End-to-End Workflow: {'✅ PASS' if integration_success else '❌ FAIL'}")

        return integration_success

    except Exception as e:
        logger.error(f"❌ Integration test suite failed: {e}")
        return False


def main():
    """Run all test suites and provide comprehensive summary."""
    logger.info("🧪 BigQuery AI Legal Document Intelligence Platform - Comprehensive Test Suite")
    logger.info("=" * 100)
    logger.info("Competition: BigQuery AI Hackathon")
    logger.info("Author: Faizal")
    logger.info("Date: September 2025")
    logger.info("=" * 100)

    start_time = time.time()

    # Run all test suites
    track1_success = run_track1_tests()
    track2_success = run_track2_tests()
    integration_success = run_integration_tests()

    end_time = time.time()
    total_time = end_time - start_time

    # Calculate overall results
    total_suites = 3
    successful_suites = sum([track1_success, track2_success, integration_success])
    overall_success_rate = (successful_suites / total_suites) * 100

    # Print final summary
    logger.info("=" * 100)
    logger.info("🏆 FINAL TEST RESULTS SUMMARY")
    logger.info("=" * 100)
    logger.info(f"📊 Overall Results:")
    logger.info(f"   Track 1 (Generative AI): {'✅ PASS' if track1_success else '❌ FAIL'}")
    logger.info(f"   Track 2 (Vector Search): {'✅ PASS' if track2_success else '❌ FAIL'}")
    logger.info(f"   Integration Tests: {'✅ PASS' if integration_success else '❌ FAIL'}")
    logger.info(f"   Overall Success Rate: {overall_success_rate:.1f}% ({successful_suites}/{total_suites})")
    logger.info(f"   Total Test Time: {total_time:.2f} seconds")

    if overall_success_rate == 100.0:
        logger.info("🎉 ALL TESTS PASSED! System is ready for competition submission.")
        return True
    else:
        logger.error("❌ Some tests failed. Please review and fix issues before submission.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
