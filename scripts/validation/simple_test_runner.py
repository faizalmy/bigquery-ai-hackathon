#!/usr/bin/env python3
"""
Simple Test Runner for Unit Tests
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script runs unit tests without requiring full BigQuery setup.
"""

import sys
import os
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up test environment
from tests.test_config import setup_test_environment
setup_test_environment()

def run_simple_tests():
    """Run simple unit tests that don't require BigQuery."""
    print("🧪 Running Simple Unit Tests")
    print("=" * 60)

    # Test cases that should work without BigQuery
    test_cases = [
        # Test data structures and basic functionality
        ('tests.unit.core.test_document_processor.TestProcessingResult', 'test_processing_result_creation'),
        ('tests.unit.core.test_document_processor.TestProcessingResult', 'test_processing_result_with_errors'),

        # Test error handling
        ('tests.unit.core.test_error_handler.TestErrorCategory', 'test_error_category_values'),
        ('tests.unit.core.test_error_handler.TestErrorSeverity', 'test_error_severity_values'),
        ('tests.unit.core.test_error_handler.TestRetryConfig', 'test_retry_config_creation'),

        # Test status tracker data structures
        ('tests.unit.core.test_status_tracker.TestProcessingStatus', 'test_processing_status_values'),
        ('tests.unit.core.test_status_tracker.TestSystemMetrics', 'test_system_metrics_creation'),

        # Test similarity engine data structures
        ('tests.unit.core.test_similarity_engine.TestSimilarityResult', 'test_similarity_result_creation'),
        ('tests.unit.core.test_similarity_engine.TestSearchQuery', 'test_search_query_creation'),

        # Test predictive engine data structures
        ('tests.unit.core.test_predictive_engine.TestComprehensiveAnalysis', 'test_comprehensive_analysis_creation'),
        ('tests.unit.core.test_predictive_engine.TestLegalBrief', 'test_legal_brief_creation'),

        # Test comprehensive analyzer data structures
        ('tests.unit.core.test_comprehensive_analyzer.TestLegalIntelligenceReport', 'test_legal_intelligence_report_creation'),
    ]

    results = {
        'total_tests': len(test_cases),
        'passed_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    for test_class, test_method in test_cases:
        print(f"\n📋 Running {test_class}.{test_method}...")

        try:
            # Import the test class
            module_name, class_name = test_class.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            test_class_obj = getattr(module, class_name)

            # Create test instance
            test_instance = test_class_obj()
            test_instance.setUp()

            # Run the specific test method
            test_method_obj = getattr(test_instance, test_method)
            test_method_obj()

            print(f"   ✅ PASSED")
            results['passed_tests'] += 1
            results['test_results'].append({
                'test': f"{test_class}.{test_method}",
                'status': 'PASSED',
                'error': None
            })

        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            results['failed_tests'] += 1
            results['test_results'].append({
                'test': f"{test_class}.{test_method}",
                'status': 'FAILED',
                'error': str(e)
            })

    return results

def run_mock_tests():
    """Run tests with mocked dependencies."""
    print("\n🎭 Running Mock Tests")
    print("=" * 60)

    # Test cases that use mocks
    mock_test_cases = [
        ('tests.unit.core.test_document_processor.TestLegalDocumentProcessor', 'test_initialization_success'),
        ('tests.unit.core.test_document_processor.TestLegalDocumentProcessor', 'test_document_validation_success'),
        ('tests.unit.core.test_document_processor.TestLegalDocumentProcessor', 'test_document_validation_missing_content'),
        ('tests.unit.core.test_document_processor.TestLegalDocumentProcessor', 'test_document_validation_empty_content'),
        ('tests.unit.core.test_document_processor.TestLegalDocumentProcessor', 'test_document_validation_content_too_short'),
        ('tests.unit.core.test_document_processor.TestLegalDocumentProcessor', 'test_document_validation_content_too_long'),
    ]

    results = {
        'total_tests': len(mock_test_cases),
        'passed_tests': 0,
        'failed_tests': 0,
        'test_results': []
    }

    for test_class, test_method in mock_test_cases:
        print(f"\n📋 Running {test_class}.{test_method}...")

        try:
            # Import the test class
            module_name, class_name = test_class.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            test_class_obj = getattr(module, class_name)

            # Create test instance
            test_instance = test_class_obj()
            test_instance.setUp()

            # Run the specific test method
            test_method_obj = getattr(test_instance, test_method)
            test_method_obj()

            print(f"   ✅ PASSED")
            results['passed_tests'] += 1
            results['test_results'].append({
                'test': f"{test_class}.{test_method}",
                'status': 'PASSED',
                'error': None
            })

        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            results['failed_tests'] += 1
            results['test_results'].append({
                'test': f"{test_class}.{test_method}",
                'status': 'FAILED',
                'error': str(e)
            })

    return results

def generate_test_report(simple_results, mock_results):
    """Generate test report."""
    print("\n📊 Test Report")
    print("=" * 60)

    total_tests = simple_results['total_tests'] + mock_results['total_tests']
    total_passed = simple_results['passed_tests'] + mock_results['passed_tests']
    total_failed = simple_results['failed_tests'] + mock_results['failed_tests']

    print(f"📈 Simple Tests: {simple_results['passed_tests']}/{simple_results['total_tests']} passed")
    print(f"🎭 Mock Tests: {mock_results['passed_tests']}/{mock_results['total_tests']} passed")
    print(f"🎯 Total Tests: {total_passed}/{total_tests} passed")
    print(f"📊 Pass Rate: {(total_passed/total_tests)*100:.1f}%")

    if total_failed > 0:
        print(f"\n❌ Failed Tests:")
        for result in simple_results['test_results'] + mock_results['test_results']:
            if result['status'] == 'FAILED':
                print(f"   - {result['test']}: {result['error']}")

    return {
        'total_tests': total_tests,
        'passed_tests': total_passed,
        'failed_tests': total_failed,
        'pass_rate': (total_passed/total_tests)*100 if total_tests > 0 else 0,
        'simple_results': simple_results,
        'mock_results': mock_results
    }

def main():
    """Main function."""
    print("🧪 Simple Unit Test Runner")
    print("Legal Document Intelligence Platform - Phase 3")
    print("=" * 80)

    # Run simple tests
    simple_results = run_simple_tests()

    # Run mock tests
    mock_results = run_mock_tests()

    # Generate report
    report = generate_test_report(simple_results, mock_results)

    print(f"\n🎯 Final Status: {'PASSED' if report['pass_rate'] >= 80 else 'NEEDS IMPROVEMENT'}")

    return report

if __name__ == "__main__":
    main()
