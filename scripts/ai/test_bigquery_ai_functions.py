#!/usr/bin/env python3
"""
BigQuery AI Functions Testing Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests the BigQuery AI functions implementation with sample legal documents.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from ai.models.bigquery_ai_functions import BigQueryAIFunctions
from data.ingestion import LegalDataIngestion
from data.preprocessing import LegalDocumentPreprocessor

def setup_logging():
    """Setup logging for the script."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'bigquery_ai_functions_test.log')
        ]
    )

def load_test_data() -> list:
    """
    Load test data for BigQuery AI functions testing.

    Returns:
        List of preprocessed legal documents
    """
    print("📥 Loading test data...")

    # Load raw data
    ingestion = LegalDataIngestion()
    datasets = ingestion.load_legal_datasets()
    raw_documents = datasets['sample_legal_docs']['documents']

    # Preprocess documents
    preprocessor = LegalDocumentPreprocessor()
    preprocessed_documents = preprocessor.preprocess_batch(raw_documents[:10])  # Test with 10 documents

    print(f"✅ Loaded {len(preprocessed_documents)} preprocessed documents for testing")
    return preprocessed_documents

def test_ml_generate_text(ai_functions: BigQueryAIFunctions, documents: list) -> dict:
    """
    Test ML.GENERATE_TEXT function for document summarization.

    Args:
        ai_functions: BigQuery AI functions instance
        documents: List of test documents

    Returns:
        Test results
    """
    print("\n🔍 Testing ML.GENERATE_TEXT (Document Summarization)")
    print("-" * 60)

    results = {
        'function': 'ML.GENERATE_TEXT',
        'test_timestamp': datetime.now().isoformat(),
        'documents_tested': len(documents),
        'successful_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    for i, doc in enumerate(documents):
        try:
            print(f"  📄 Testing document {i+1}: {doc['document_id']} ({doc['document_type']})")

            # Test summarization
            summary_result = ai_functions.generate_document_summary(doc)

            # Validate result
            if summary_result.get('document_id') and summary_result.get('sql_query'):
                results['successful_tests'] += 1
                test_result = {
                    'document_id': doc['document_id'],
                    'document_type': doc['document_type'],
                    'status': 'success',
                    'sql_query_length': len(summary_result['sql_query']),
                    'prompt_used': summary_result.get('prompt_used', '')
                }
                print(f"    ✅ Success: Generated SQL query ({len(summary_result['sql_query'])} chars)")
            else:
                results['failed_tests'] += 1
                test_result = {
                    'document_id': doc['document_id'],
                    'status': 'failed',
                    'error': 'Invalid result structure'
                }
                print(f"    ❌ Failed: Invalid result structure")

            results['test_results'].append(test_result)

        except Exception as e:
            results['failed_tests'] += 1
            test_result = {
                'document_id': doc.get('document_id', 'unknown'),
                'status': 'error',
                'error': str(e)
            }
            results['test_results'].append(test_result)
            print(f"    ❌ Error: {e}")

    success_rate = (results['successful_tests'] / results['documents_tested']) * 100
    print(f"\n  📊 ML.GENERATE_TEXT Test Results:")
    print(f"    Documents Tested: {results['documents_tested']}")
    print(f"    Successful: {results['successful_tests']}")
    print(f"    Failed: {results['failed_tests']}")
    print(f"    Success Rate: {success_rate:.1f}%")

    return results

def test_ai_generate_table(ai_functions: BigQueryAIFunctions, documents: list) -> dict:
    """
    Test AI.GENERATE_TABLE function for legal data extraction.

    Args:
        ai_functions: BigQuery AI functions instance
        documents: List of test documents

    Returns:
        Test results
    """
    print("\n📊 Testing AI.GENERATE_TABLE (Legal Data Extraction)")
    print("-" * 60)

    results = {
        'function': 'AI.GENERATE_TABLE',
        'test_timestamp': datetime.now().isoformat(),
        'documents_tested': len(documents),
        'successful_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    for i, doc in enumerate(documents):
        try:
            print(f"  📄 Testing document {i+1}: {doc['document_id']} ({doc['document_type']})")

            # Test extraction
            extraction_result = ai_functions.extract_legal_data(doc)

            # Validate result
            if extraction_result.get('document_id') and extraction_result.get('sql_query'):
                results['successful_tests'] += 1
                test_result = {
                    'document_id': doc['document_id'],
                    'document_type': doc['document_type'],
                    'status': 'success',
                    'sql_query_length': len(extraction_result['sql_query']),
                    'output_schema': extraction_result.get('output_schema', ''),
                    'prompt_used': extraction_result.get('prompt_used', '')
                }
                print(f"    ✅ Success: Generated SQL query with schema")
                print(f"       Schema: {extraction_result.get('output_schema', '')[:50]}...")
            else:
                results['failed_tests'] += 1
                test_result = {
                    'document_id': doc['document_id'],
                    'status': 'failed',
                    'error': 'Invalid result structure'
                }
                print(f"    ❌ Failed: Invalid result structure")

            results['test_results'].append(test_result)

        except Exception as e:
            results['failed_tests'] += 1
            test_result = {
                'document_id': doc.get('document_id', 'unknown'),
                'status': 'error',
                'error': str(e)
            }
            results['test_results'].append(test_result)
            print(f"    ❌ Error: {e}")

    success_rate = (results['successful_tests'] / results['documents_tested']) * 100
    print(f"\n  📊 AI.GENERATE_TABLE Test Results:")
    print(f"    Documents Tested: {results['documents_tested']}")
    print(f"    Successful: {results['successful_tests']}")
    print(f"    Failed: {results['failed_tests']}")
    print(f"    Success Rate: {success_rate:.1f}%")

    return results

def test_ai_generate_bool(ai_functions: BigQueryAIFunctions, documents: list) -> dict:
    """
    Test AI.GENERATE_BOOL function for urgency detection.

    Args:
        ai_functions: BigQuery AI functions instance
        documents: List of test documents

    Returns:
        Test results
    """
    print("\n⚡ Testing AI.GENERATE_BOOL (Urgency Detection)")
    print("-" * 60)

    results = {
        'function': 'AI.GENERATE_BOOL',
        'test_timestamp': datetime.now().isoformat(),
        'documents_tested': len(documents),
        'successful_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    for i, doc in enumerate(documents):
        try:
            print(f"  📄 Testing document {i+1}: {doc['document_id']} ({doc['document_type']})")

            # Test urgency detection
            urgency_result = ai_functions.detect_urgency(doc)

            # Validate result
            if urgency_result.get('document_id') and urgency_result.get('sql_query'):
                results['successful_tests'] += 1
                test_result = {
                    'document_id': doc['document_id'],
                    'document_type': doc['document_type'],
                    'status': 'success',
                    'sql_query_length': len(urgency_result['sql_query']),
                    'prompt_used': urgency_result.get('prompt_used', '')
                }
                print(f"    ✅ Success: Generated SQL query for urgency detection")
            else:
                results['failed_tests'] += 1
                test_result = {
                    'document_id': doc['document_id'],
                    'status': 'failed',
                    'error': 'Invalid result structure'
                }
                print(f"    ❌ Failed: Invalid result structure")

            results['test_results'].append(test_result)

        except Exception as e:
            results['failed_tests'] += 1
            test_result = {
                'document_id': doc.get('document_id', 'unknown'),
                'status': 'error',
                'error': str(e)
            }
            results['test_results'].append(test_result)
            print(f"    ❌ Error: {e}")

    success_rate = (results['successful_tests'] / results['documents_tested']) * 100
    print(f"\n  📊 AI.GENERATE_BOOL Test Results:")
    print(f"    Documents Tested: {results['documents_tested']}")
    print(f"    Successful: {results['successful_tests']}")
    print(f"    Failed: {results['failed_tests']}")
    print(f"    Success Rate: {success_rate:.1f}%")

    return results

def test_ai_forecast(ai_functions: BigQueryAIFunctions) -> dict:
    """
    Test AI.FORECAST function for case outcome prediction.

    Args:
        ai_functions: BigQuery AI functions instance

    Returns:
        Test results
    """
    print("\n📈 Testing AI.FORECAST (Case Outcome Prediction)")
    print("-" * 60)

    # Create sample case data with time series
    sample_case_data = {
        'case_id': 'case_001',
        'time_series_data': [
            {'period': 1, 'case_volume': 10},
            {'period': 2, 'case_volume': 15},
            {'period': 3, 'case_volume': 12},
            {'period': 4, 'case_volume': 18},
            {'period': 5, 'case_volume': 20}
        ]
    }

    results = {
        'function': 'AI.FORECAST',
        'test_timestamp': datetime.now().isoformat(),
        'cases_tested': 1,
        'successful_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    try:
        print(f"  📄 Testing case: {sample_case_data['case_id']}")

        # Test forecasting
        forecast_result = ai_functions.forecast_case_outcome(sample_case_data)

        # Validate result
        if forecast_result.get('case_id') and forecast_result.get('sql_query'):
            results['successful_tests'] += 1
            test_result = {
                'case_id': sample_case_data['case_id'],
                'status': 'success',
                'sql_query_length': len(forecast_result['sql_query']),
                'forecast_periods': forecast_result.get('forecast_periods', 0)
            }
            print(f"    ✅ Success: Generated SQL query for forecasting")
            print(f"       Forecast Periods: {forecast_result.get('forecast_periods', 0)}")
        else:
            results['failed_tests'] += 1
            test_result = {
                'case_id': sample_case_data['case_id'],
                'status': 'failed',
                'error': 'Invalid result structure'
            }
            print(f"    ❌ Failed: Invalid result structure")

        results['test_results'].append(test_result)

    except Exception as e:
        results['failed_tests'] += 1
        test_result = {
            'case_id': sample_case_data['case_id'],
            'status': 'error',
            'error': str(e)
        }
        results['test_results'].append(test_result)
        print(f"    ❌ Error: {e}")

    success_rate = (results['successful_tests'] / results['cases_tested']) * 100
    print(f"\n  📊 AI.FORECAST Test Results:")
    print(f"    Cases Tested: {results['cases_tested']}")
    print(f"    Successful: {results['successful_tests']}")
    print(f"    Failed: {results['failed_tests']}")
    print(f"    Success Rate: {success_rate:.1f}%")

    return results

def test_batch_processing(ai_functions: BigQueryAIFunctions, documents: list) -> dict:
    """
    Test batch processing of documents with all AI functions.

    Args:
        ai_functions: BigQuery AI functions instance
        documents: List of test documents

    Returns:
        Test results
    """
    print("\n🔄 Testing Batch Processing")
    print("-" * 60)

    results = {
        'function': 'BATCH_PROCESSING',
        'test_timestamp': datetime.now().isoformat(),
        'documents_tested': len(documents),
        'successful_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    try:
        print(f"  📄 Processing {len(documents)} documents with all AI functions...")

        # Test batch processing
        batch_results = ai_functions.batch_process_documents(documents)

        # Analyze results
        for result in batch_results:
            if result.get('success', False):
                results['successful_tests'] += 1
                test_result = {
                    'document_id': result.get('document_id'),
                    'status': 'success',
                    'ai_functions_used': len(result.get('ai_results', {}))
                }
            else:
                results['failed_tests'] += 1
                test_result = {
                    'document_id': result.get('document_id'),
                    'status': 'failed',
                    'error': result.get('error', 'Unknown error')
                }

            results['test_results'].append(test_result)

        print(f"    ✅ Batch processing completed")
        print(f"    📊 Results: {results['successful_tests']} successful, {results['failed_tests']} failed")

    except Exception as e:
        results['failed_tests'] = len(documents)
        test_result = {
            'status': 'error',
            'error': str(e)
        }
        results['test_results'].append(test_result)
        print(f"    ❌ Error: {e}")

    success_rate = (results['successful_tests'] / results['documents_tested']) * 100
    print(f"\n  📊 Batch Processing Test Results:")
    print(f"    Documents Tested: {results['documents_tested']}")
    print(f"    Successful: {results['successful_tests']}")
    print(f"    Failed: {results['failed_tests']}")
    print(f"    Success Rate: {success_rate:.1f}%")

    return results

def save_test_results(all_results: dict):
    """
    Save test results to file.

    Args:
        all_results: Dictionary containing all test results
    """
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"bigquery_ai_functions_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n💾 Test results saved to: {output_file}")

def main():
    """Main function to run BigQuery AI functions tests."""
    print("🤖 BigQuery AI Functions Testing - Phase 2.3")
    print("=" * 70)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize AI functions
        print("🔧 Initializing BigQuery AI functions...")
        ai_functions = BigQueryAIFunctions("faizal-hackathon")
        print("✅ BigQuery AI functions initialized")

        # Load test data
        test_documents = load_test_data()

        # Run tests
        all_results = {
            'test_suite': 'BigQuery AI Functions',
            'test_timestamp': datetime.now().isoformat(),
            'test_results': {}
        }

        # Test ML.GENERATE_TEXT
        ml_generate_text_results = test_ml_generate_text(ai_functions, test_documents)
        all_results['test_results']['ml_generate_text'] = ml_generate_text_results

        # Test AI.GENERATE_TABLE
        ai_generate_table_results = test_ai_generate_table(ai_functions, test_documents)
        all_results['test_results']['ai_generate_table'] = ai_generate_table_results

        # Test AI.GENERATE_BOOL
        ai_generate_bool_results = test_ai_generate_bool(ai_functions, test_documents)
        all_results['test_results']['ai_generate_bool'] = ai_generate_bool_results

        # Test AI.FORECAST
        ai_forecast_results = test_ai_forecast(ai_functions)
        all_results['test_results']['ai_forecast'] = ai_forecast_results

        # Test batch processing
        batch_processing_results = test_batch_processing(ai_functions, test_documents)
        all_results['test_results']['batch_processing'] = batch_processing_results

        # Calculate overall success rate
        total_tests = sum(len(result.get('test_results', [])) for result in all_results['test_results'].values())
        total_successful = sum(result.get('successful_tests', 0) for result in all_results['test_results'].values())
        overall_success_rate = (total_successful / total_tests) * 100 if total_tests > 0 else 0

        # Print final summary
        print(f"\n📋 Final Test Summary")
        print("=" * 70)
        print(f"  Total Tests: {total_tests}")
        print(f"  Successful: {total_successful}")
        print(f"  Failed: {total_tests - total_successful}")
        print(f"  Overall Success Rate: {overall_success_rate:.1f}%")

        # Save results
        save_test_results(all_results)

        if overall_success_rate >= 80:
            print(f"\n✅ BigQuery AI functions testing completed successfully!")
            print(f"🎯 Ready for Phase 2.4: Data Loading and Integration")
        else:
            print(f"\n⚠️  BigQuery AI functions testing completed with issues")
            print(f"   Success rate below 80% - review and fix issues")

    except Exception as e:
        logger.error(f"Error in BigQuery AI functions testing: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
