#!/usr/bin/env python3
"""
Competition Test Suite - BigQuery AI Functions
Legal Document Intelligence Platform - BigQuery AI Hackathon

This script tests the core competition functions:
- Track 1: ML.GENERATE_TEXT, AI.GENERATE_TABLE, AI.GENERATE_BOOL, AI.FORECAST
- Track 2: ML.GENERATE_EMBEDDING, VECTOR_SEARCH

Author: Faizal
Date: September 2025
Competition: BigQuery AI Hackathon
"""

import sys
import os
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from bigquery_ai_functions import BigQueryAIFunctions


def test_track1_functions():
    """Test Track 1: Generative AI Functions"""
    logger.info("🧪 Testing Track 1: Generative AI Functions")
    logger.info("=" * 60)

    try:
        ai_functions = BigQueryAIFunctions()
        test_document_id = "caselaw_000001"

        # Test ML.GENERATE_TEXT
        logger.info("📝 Testing ML.GENERATE_TEXT...")
        start_time = time.time()
        result = ai_functions.ml_generate_text(test_document_id, 1)
        duration = time.time() - start_time
        logger.info(f"✅ ML.GENERATE_TEXT: {result['total_documents']} summaries in {duration:.2f}s")

        # Test AI.GENERATE_TABLE
        logger.info("📊 Testing AI.GENERATE_TABLE...")
        start_time = time.time()
        result = ai_functions.ai_generate_table(test_document_id, 1)
        duration = time.time() - start_time
        logger.info(f"✅ AI.GENERATE_TABLE: {result['total_documents']} extractions in {duration:.2f}s")

        # Test AI.GENERATE_BOOL
        logger.info("⚠️ Testing AI.GENERATE_BOOL...")
        start_time = time.time()
        result = ai_functions.ai_generate_bool(test_document_id, 1)
        duration = time.time() - start_time
        logger.info(f"✅ AI.GENERATE_BOOL: {result['total_documents']} analyses in {duration:.2f}s")

        # Test AI.FORECAST
        logger.info("🔮 Testing AI.FORECAST...")
        start_time = time.time()
        result = ai_functions.ai_forecast("case_law", 1)
        duration = time.time() - start_time
        logger.info(f"✅ AI.FORECAST: {result['total_forecasts']} forecasts in {duration:.2f}s")

        logger.info("🎉 Track 1 tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Track 1 tests failed: {e}")
        return False


def test_track2_functions():
    """Test Track 2: Vector Search Functions"""
    logger.info("🧪 Testing Track 2: Vector Search Functions")
    logger.info("=" * 60)

    try:
        ai_functions = BigQueryAIFunctions()
        test_document_id = "caselaw_000001"
        test_query = "legal case about marriage"

        # Test ML.GENERATE_EMBEDDING
        logger.info("🔗 Testing ML.GENERATE_EMBEDDING...")
        start_time = time.time()
        result = ai_functions.ml_generate_embedding(test_document_id, 1)
        duration = time.time() - start_time
        logger.info(f"✅ ML.GENERATE_EMBEDDING: {result['total_documents']} embeddings in {duration:.2f}s")

        # Test VECTOR_SEARCH
        logger.info("🔍 Testing VECTOR_SEARCH...")
        start_time = time.time()
        result = ai_functions.vector_search(test_query, 3)
        duration = time.time() - start_time
        logger.info(f"✅ VECTOR_SEARCH: {result['total_results']} results in {duration:.2f}s")

        logger.info("🎉 Track 2 tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Track 2 tests failed: {e}")
        return False


def test_integration_workflow():
    """Test complete integration workflow"""
    logger.info("🔄 Testing Integration Workflow")
    logger.info("=" * 60)

    try:
        ai_functions = BigQueryAIFunctions()
        test_document_id = "caselaw_000001"

        # Run all functions in sequence
        logger.info("Running complete workflow...")
        start_time = time.time()

        # Track 1 functions
        summary = ai_functions.ml_generate_text(test_document_id, 1)
        extraction = ai_functions.ai_generate_table(test_document_id, 1)
        urgency = ai_functions.ai_generate_bool(test_document_id, 1)
        forecast = ai_functions.ai_forecast("case_law", 1)

        duration = time.time() - start_time

        logger.info(f"✅ Integration workflow completed in {duration:.2f}s")
        logger.info(f"   📝 Summaries: {summary['total_documents']}")
        logger.info(f"   📊 Extractions: {extraction['total_documents']}")
        logger.info(f"   ⚠️ Urgency analyses: {urgency['total_documents']}")
        logger.info(f"   🔮 Forecasts: {forecast['total_forecasts']}")

        logger.info("🎉 Integration tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Integration tests failed: {e}")
        return False


def main():
    """Run all competition tests"""
    logger.info("🏆 BigQuery AI Competition Test Suite")
    logger.info("=" * 60)

    results = {
        'track1': False,
        'track2': False,
        'integration': False
    }

    # Test Track 1
    results['track1'] = test_track1_functions()

    # Test Track 2
    results['track2'] = test_track2_functions()

    # Test Integration
    results['integration'] = test_integration_workflow()

    # Summary
    logger.info("📊 Test Results Summary")
    logger.info("=" * 60)
    logger.info(f"Track 1 (Generative AI): {'✅ PASS' if results['track1'] else '❌ FAIL'}")
    logger.info(f"Track 2 (Vector Search): {'✅ PASS' if results['track2'] else '❌ FAIL'}")
    logger.info(f"Integration Workflow: {'✅ PASS' if results['integration'] else '❌ FAIL'}")

    success_rate = sum(results.values()) / len(results) * 100
    logger.info(f"Overall Success Rate: {success_rate:.1f}%")

    if all(results.values()):
        logger.info("🎉 All tests passed! Competition submission ready!")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs.")
        return 1


if __name__ == "__main__":
    exit(main())
