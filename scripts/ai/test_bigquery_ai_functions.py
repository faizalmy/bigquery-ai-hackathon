#!/usr/bin/env python3
"""
BigQuery AI Functions Test Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests all Track 1 BigQuery AI functions with real legal data.
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_ai_functions import BigQueryAIFunctions

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ml_generate_text():
    """Test ML.GENERATE_TEXT function."""
    try:
        print("🧪 Testing ML.GENERATE_TEXT (Document Summarization)")
        print("-" * 50)

        ai_functions = BigQueryAIFunctions()
        results = ai_functions.ml_generate_text_summarization(limit=3)

        print(f"✅ Function: {results['function']}")
        print(f"✅ Purpose: {results['purpose']}")
        print(f"✅ Documents Processed: {results['total_documents']}")

        # Show sample results
        for i, summary in enumerate(results['summaries'][:2]):
            print(f"\n📄 Document {i+1}: {summary['document_id']}")
            print(f"   Type: {summary['document_type']}")
            print(f"   Length: {summary['content_length']} characters")
            if summary['summary']:
                print(f"   Summary: {summary['summary'][:200]}...")
            else:
                print("   Summary: [No summary generated]")

        return True

    except Exception as e:
        print(f"❌ ML.GENERATE_TEXT test failed: {e}")
        return False

def test_ai_generate_table():
    """Test AI.GENERATE_TABLE function."""
    try:
        print("\n🧪 Testing AI.GENERATE_TABLE (Legal Data Extraction)")
        print("-" * 50)

        ai_functions = BigQueryAIFunctions()
        results = ai_functions.ai_generate_table_extraction(limit=3)

        print(f"✅ Function: {results['function']}")
        print(f"✅ Purpose: {results['purpose']}")
        print(f"✅ Documents Processed: {results['total_documents']}")

        # Show sample results
        for i, extraction in enumerate(results['extractions'][:2]):
            print(f"\n📊 Document {i+1}: {extraction['document_id']}")
            print(f"   Type: {extraction['document_type']}")
            print(f"   Length: {extraction['content_length']} characters")
            if extraction['extracted_data']:
                print(f"   Extracted Data: {str(extraction['extracted_data'])[:200]}...")
            else:
                print("   Extracted Data: [No data extracted]")

        return True

    except Exception as e:
        print(f"❌ AI.GENERATE_TABLE test failed: {e}")
        return False

def test_ai_generate_bool():
    """Test AI.GENERATE_BOOL function."""
    try:
        print("\n🧪 Testing AI.GENERATE_BOOL (Urgency Detection)")
        print("-" * 50)

        ai_functions = BigQueryAIFunctions()
        results = ai_functions.ai_generate_bool_urgency(limit=3)

        print(f"✅ Function: {results['function']}")
        print(f"✅ Purpose: {results['purpose']}")
        print(f"✅ Documents Processed: {results['total_documents']}")

        # Show sample results
        for i, urgency in enumerate(results['urgency_analyses'][:2]):
            print(f"\n⚡ Document {i+1}: {urgency['document_id']}")
            print(f"   Type: {urgency['document_type']}")
            print(f"   Length: {urgency['content_length']} characters")
            print(f"   Is Urgent: {urgency['is_urgent']}")

        return True

    except Exception as e:
        print(f"❌ AI.GENERATE_BOOL test failed: {e}")
        return False

def test_ai_forecast():
    """Test AI.FORECAST function."""
    try:
        print("\n🧪 Testing AI.FORECAST (Case Outcome Prediction)")
        print("-" * 50)

        ai_functions = BigQueryAIFunctions()
        results = ai_functions.ai_forecast_outcome(limit=3)

        print(f"✅ Function: {results['function']}")
        print(f"✅ Purpose: {results['purpose']}")
        print(f"✅ Documents Processed: {results['total_documents']}")

        # Show sample results
        for i, forecast in enumerate(results['forecasts'][:2]):
            print(f"\n📈 Document {i+1}: {forecast['document_id']}")
            print(f"   Type: {forecast['document_type']}")
            print(f"   Length: {forecast['content_length']} characters")
            print(f"   Current Score: {forecast['current_outcome_score']}")
            if forecast['forecast']:
                print(f"   Forecast: {str(forecast['forecast'])[:200]}...")
            else:
                print("   Forecast: [No forecast generated]")

        return True

    except Exception as e:
        print(f"❌ AI.FORECAST test failed: {e}")
        return False

def test_all_functions():
    """Test all Track 1 functions together."""
    try:
        print("\n🧪 Testing All Track 1 Functions")
        print("=" * 50)

        ai_functions = BigQueryAIFunctions()
        results = ai_functions.run_all_track1_functions(limit=2)

        print(f"✅ Functions Executed: {len(results['functions_executed'])}")
        print(f"✅ Total Documents Processed: {results['total_documents_processed']}")
        print(f"✅ Functions: {', '.join(results['functions_executed'])}")

        return True

    except Exception as e:
        print(f"❌ All functions test failed: {e}")
        return False

def main():
    """Main test execution."""
    try:
        print("🚀 BigQuery AI Functions Test Suite")
        print("=" * 60)
        print("Testing Track 1 BigQuery AI functions with real legal data...")
        print(f"Started at: {datetime.now().isoformat()}")
        print()

        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'PENDING'
        }

        # Run individual tests
        test_results['tests']['ml_generate_text'] = test_ml_generate_text()
        test_results['tests']['ai_generate_table'] = test_ai_generate_table()
        test_results['tests']['ai_generate_bool'] = test_ai_generate_bool()
        test_results['tests']['ai_forecast'] = test_ai_forecast()
        test_results['tests']['all_functions'] = test_all_functions()

        # Calculate overall status
        passed_tests = sum(1 for result in test_results['tests'].values() if result)
        total_tests = len(test_results['tests'])

        if passed_tests == total_tests:
            test_results['overall_status'] = 'PASSED'
            print(f"\n🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
        else:
            test_results['overall_status'] = 'FAILED'
            print(f"\n⚠️ SOME TESTS FAILED ({passed_tests}/{total_tests})")

        # Save test results
        results_file = Path("data/processed/bigquery_ai_functions_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Test Results Summary:")
        for test_name, result in test_results['tests'].items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")

        print(f"\n📁 Results saved to: {results_file}")
        print(f"Completed at: {datetime.now().isoformat()}")

        return 0 if test_results['overall_status'] == 'PASSED' else 1

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
