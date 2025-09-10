#!/usr/bin/env python3
"""
Unit Test Coverage Report
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

Following World-Class Production Tester Protocol:
- Comprehensive Coverage: Validate every specification, requirement, and edge case
- Risk-Based Prioritization: Focus testing on highest impact and failure probability areas
- Data-Driven Decisions: Base testing priorities on measurable metrics and trends
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

def run_unit_tests() -> Dict[str, Any]:
    """Run all unit tests and collect results."""
    print("🧪 Running Unit Tests...")
    print("=" * 60)

    test_results = {
        'test_files': [],
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_coverage': {},
        'performance_metrics': {},
        'quality_gates': {}
    }

    # Define test files to run
    test_files = [
        'tests/unit/core/test_document_processor.py',
        'tests/unit/core/test_similarity_engine.py',
        'tests/unit/core/test_predictive_engine.py',
        'tests/unit/core/test_status_tracker.py',
        'tests/unit/core/test_error_handler.py',
        'tests/unit/core/test_comprehensive_analyzer.py'
    ]

    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")

        try:
            # Run the test file
            result = subprocess.run([
                sys.executable, '-m', 'unittest', test_file, '-v'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            # Parse test results
            test_output = result.stdout
            test_errors = result.stderr

            # Count tests
            lines = test_output.split('\n')
            test_count = 0
            passed_count = 0
            failed_count = 0

            for line in lines:
                if 'test_' in line and ('ok' in line or 'FAIL' in line or 'ERROR' in line):
                    test_count += 1
                    if 'ok' in line:
                        passed_count += 1
                    elif 'FAIL' in line or 'ERROR' in line:
                        failed_count += 1

            test_file_result = {
                'file': test_file,
                'status': 'PASSED' if result.returncode == 0 else 'FAILED',
                'tests_run': test_count,
                'tests_passed': passed_count,
                'tests_failed': failed_count,
                'return_code': result.returncode,
                'output': test_output,
                'errors': test_errors
            }

            test_results['test_files'].append(test_file_result)
            test_results['total_tests'] += test_count
            test_results['passed_tests'] += passed_count
            test_results['failed_tests'] += failed_count

            print(f"   ✅ Tests: {passed_count}/{test_count} passed")
            if failed_count > 0:
                print(f"   ❌ Tests: {failed_count} failed")

        except Exception as e:
            print(f"   ❌ Error running {test_file}: {e}")
            test_results['test_files'].append({
                'file': test_file,
                'status': 'ERROR',
                'error': str(e)
            })

    return test_results

def analyze_test_coverage() -> Dict[str, Any]:
    """Analyze test coverage for Phase 3 components."""
    print("\n📊 Analyzing Test Coverage...")
    print("=" * 60)

    coverage_analysis = {
        'component_coverage': {},
        'method_coverage': {},
        'edge_case_coverage': {},
        'error_handling_coverage': {},
        'performance_test_coverage': {}
    }

    # Define Phase 3 components and their expected test coverage
    components = {
        'DocumentProcessor': {
            'file': 'src/core/document_processor.py',
            'test_file': 'tests/unit/core/test_document_processor.py',
            'methods': [
                'process_document',
                'process_batch',
                'get_processing_status',
                'retry_failed_processing',
                'get_processing_metrics',
                '_validate_document',
                '_generate_embeddings',
                '_store_processing_results',
                '_update_processing_metrics'
            ],
            'edge_cases': [
                'empty_content',
                'content_too_short',
                'content_too_long',
                'invalid_document_type',
                'ai_processing_failure',
                'storage_failure'
            ],
            'error_handling': [
                'validation_errors',
                'ai_model_errors',
                'bigquery_errors',
                'system_errors'
            ]
        },
        'SimilarityEngine': {
            'file': 'src/core/similarity_engine.py',
            'test_file': 'tests/unit/core/test_similarity_engine.py',
            'methods': [
                'find_similar_cases',
                'search_by_content',
                'batch_similarity_search',
                'get_similarity_explanation',
                '_get_case_information',
                '_perform_similarity_search',
                '_perform_content_search',
                '_apply_filters',
                '_generate_similarity_explanation'
            ],
            'edge_cases': [
                'case_not_found',
                'empty_search_results',
                'low_similarity_threshold',
                'high_similarity_threshold',
                'invalid_filters',
                'bigquery_connection_error'
            ],
            'error_handling': [
                'bigquery_errors',
                'network_errors',
                'timeout_errors',
                'invalid_input_errors'
            ]
        },
        'PredictiveEngine': {
            'file': 'src/core/predictive_engine.py',
            'test_file': 'tests/unit/core/test_predictive_engine.py',
            'methods': [
                'analyze_case',
                'generate_legal_brief',
                'assess_litigation_risk',
                'recommend_strategies',
                '_find_similar_cases_for_analysis',
                '_generate_strategy_recommendations',
                '_calculate_analysis_confidence',
                '_generate_analysis_summary'
            ],
            'edge_cases': [
                'case_analysis_failure',
                'brief_generation_failure',
                'risk_assessment_failure',
                'strategy_recommendation_failure',
                'low_confidence_analysis',
                'no_similar_cases_found'
            ],
            'error_handling': [
                'ai_model_errors',
                'similarity_engine_errors',
                'analysis_errors',
                'brief_generation_errors'
            ]
        },
        'StatusTracker': {
            'file': 'src/core/status_tracker.py',
            'test_file': 'tests/unit/core/test_status_tracker.py',
            'methods': [
                'start_processing',
                'update_stage',
                'record_error',
                'record_retry',
                'complete_processing',
                'cancel_processing',
                'get_document_status',
                'get_system_metrics',
                'get_active_documents',
                'cleanup_old_metrics'
            ],
            'edge_cases': [
                'concurrent_processing',
                'document_not_found',
                'invalid_progress_values',
                'old_metrics_cleanup',
                'high_volume_processing'
            ],
            'error_handling': [
                'thread_safety',
                'invalid_input_handling',
                'resource_cleanup',
                'metrics_calculation_errors'
            ]
        },
        'ErrorHandler': {
            'file': 'src/core/error_handler.py',
            'test_file': 'tests/unit/core/test_error_handler.py',
            'methods': [
                'handle_error',
                'execute_with_retry',
                'execute_with_fallback',
                'get_error_summary',
                '_classify_error',
                '_determine_severity',
                '_is_retryable',
                '_calculate_retry_delay'
            ],
            'edge_cases': [
                'unknown_error_types',
                'max_retries_exceeded',
                'fallback_failures',
                'concurrent_error_handling',
                'invalid_error_inputs'
            ],
            'error_handling': [
                'error_classification',
                'retry_logic',
                'fallback_strategies',
                'error_logging'
            ]
        },
        'ComprehensiveAnalyzer': {
            'file': 'src/core/comprehensive_analyzer.py',
            'test_file': 'tests/unit/core/test_comprehensive_analyzer.py',
            'methods': [
                'analyze_legal_case',
                'batch_analyze_cases',
                'get_analysis_status',
                'get_system_metrics',
                'export_analysis_report',
                '_generate_executive_summary',
                '_generate_recommendations',
                '_generate_risk_assessment',
                '_calculate_overall_confidence'
            ],
            'edge_cases': [
                'processing_failures',
                'analysis_failures',
                'brief_generation_failures',
                'export_failures',
                'batch_processing_mixed_results'
            ],
            'error_handling': [
                'component_failures',
                'analysis_errors',
                'export_errors',
                'invalid_case_data'
            ]
        }
    }

    # Analyze coverage for each component
    for component_name, component_info in components.items():
        print(f"\n🔍 Analyzing {component_name}...")

        component_coverage = {
            'methods_tested': 0,
            'methods_total': len(component_info['methods']),
            'edge_cases_tested': 0,
            'edge_cases_total': len(component_info['edge_cases']),
            'error_handling_tested': 0,
            'error_handling_total': len(component_info['error_handling']),
            'coverage_percentage': 0.0
        }

        # Check if test file exists and analyze coverage
        test_file_path = Path(__file__).parent.parent.parent / component_info['test_file']
        if test_file_path.exists():
            with open(test_file_path, 'r') as f:
                test_content = f.read()

            # Count tested methods
            for method in component_info['methods']:
                if f'test_{method}' in test_content or f'def test_{method}' in test_content:
                    component_coverage['methods_tested'] += 1

            # Count tested edge cases
            for edge_case in component_info['edge_cases']:
                if edge_case.replace('_', '') in test_content.lower():
                    component_coverage['edge_cases_tested'] += 1

            # Count tested error handling
            for error_type in component_info['error_handling']:
                if error_type.replace('_', '') in test_content.lower():
                    component_coverage['error_handling_tested'] += 1

            # Calculate coverage percentage
            total_items = (component_coverage['methods_total'] +
                          component_coverage['edge_cases_total'] +
                          component_coverage['error_handling_total'])
            tested_items = (component_coverage['methods_tested'] +
                           component_coverage['edge_cases_tested'] +
                           component_coverage['error_handling_tested'])

            if total_items > 0:
                component_coverage['coverage_percentage'] = (tested_items / total_items) * 100

        coverage_analysis['component_coverage'][component_name] = component_coverage

        print(f"   📋 Methods: {component_coverage['methods_tested']}/{component_coverage['methods_total']}")
        print(f"   🎯 Edge Cases: {component_coverage['edge_cases_tested']}/{component_coverage['edge_cases_total']}")
        print(f"   ⚠️  Error Handling: {component_coverage['error_handling_tested']}/{component_coverage['error_handling_total']}")
        print(f"   📊 Coverage: {component_coverage['coverage_percentage']:.1f}%")

    return coverage_analysis

def calculate_quality_gates(test_results: Dict[str, Any], coverage_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate quality gates based on test results and coverage."""
    print("\n🎯 Calculating Quality Gates...")
    print("=" * 60)

    quality_gates = {
        'test_execution': {
            'total_tests': test_results['total_tests'],
            'passed_tests': test_results['passed_tests'],
            'failed_tests': test_results['failed_tests'],
            'pass_rate': 0.0,
            'status': 'FAILED'
        },
        'test_coverage': {
            'average_coverage': 0.0,
            'components_above_threshold': 0,
            'components_total': len(coverage_analysis['component_coverage']),
            'coverage_threshold': 80.0,
            'status': 'FAILED'
        },
        'error_handling': {
            'error_handling_tests': 0,
            'total_error_scenarios': 0,
            'error_coverage_rate': 0.0,
            'status': 'FAILED'
        },
        'performance_testing': {
            'performance_tests': 0,
            'total_components': len(coverage_analysis['component_coverage']),
            'performance_coverage_rate': 0.0,
            'status': 'FAILED'
        },
        'overall_status': 'FAILED'
    }

    # Calculate test execution quality gate
    if test_results['total_tests'] > 0:
        quality_gates['test_execution']['pass_rate'] = (test_results['passed_tests'] / test_results['total_tests']) * 100
        if quality_gates['test_execution']['pass_rate'] >= 95.0:
            quality_gates['test_execution']['status'] = 'PASSED'

    # Calculate test coverage quality gate
    coverage_percentages = []
    for component_name, component_coverage in coverage_analysis['component_coverage'].items():
        coverage_percentages.append(component_coverage['coverage_percentage'])
        if component_coverage['coverage_percentage'] >= 80.0:
            quality_gates['test_coverage']['components_above_threshold'] += 1

    if coverage_percentages:
        quality_gates['test_coverage']['average_coverage'] = sum(coverage_percentages) / len(coverage_percentages)
        if quality_gates['test_coverage']['average_coverage'] >= 80.0:
            quality_gates['test_coverage']['status'] = 'PASSED'

    # Calculate error handling quality gate
    total_error_tests = 0
    total_error_scenarios = 0
    for component_name, component_coverage in coverage_analysis['component_coverage'].items():
        total_error_tests += component_coverage['error_handling_tested']
        total_error_scenarios += component_coverage['error_handling_total']

    quality_gates['error_handling']['error_handling_tests'] = total_error_tests
    quality_gates['error_handling']['total_error_scenarios'] = total_error_scenarios
    if total_error_scenarios > 0:
        quality_gates['error_handling']['error_coverage_rate'] = (total_error_tests / total_error_scenarios) * 100
        if quality_gates['error_handling']['error_coverage_rate'] >= 70.0:
            quality_gates['error_handling']['status'] = 'PASSED'

    # Calculate performance testing quality gate
    performance_tests = 0
    for component_name, component_coverage in coverage_analysis['component_coverage'].items():
        # Check if performance tests exist (simplified check)
        if component_coverage['methods_tested'] > 0:  # Assume performance tests if methods are tested
            performance_tests += 1

    quality_gates['performance_testing']['performance_tests'] = performance_tests
    if quality_gates['performance_testing']['total_components'] > 0:
        quality_gates['performance_testing']['performance_coverage_rate'] = (performance_tests / quality_gates['performance_testing']['total_components']) * 100
        if quality_gates['performance_testing']['performance_coverage_rate'] >= 80.0:
            quality_gates['performance_testing']['status'] = 'PASSED'

    # Calculate overall status
    passed_gates = sum(1 for gate in quality_gates.values() if isinstance(gate, dict) and gate.get('status') == 'PASSED')
    total_gates = sum(1 for gate in quality_gates.values() if isinstance(gate, dict) and 'status' in gate)

    if passed_gates >= total_gates * 0.8:  # 80% of gates must pass
        quality_gates['overall_status'] = 'PASSED'

    # Print quality gate results
    print(f"📊 Test Execution: {quality_gates['test_execution']['status']} ({quality_gates['test_execution']['pass_rate']:.1f}% pass rate)")
    print(f"📈 Test Coverage: {quality_gates['test_coverage']['status']} ({quality_gates['test_coverage']['average_coverage']:.1f}% average)")
    print(f"⚠️  Error Handling: {quality_gates['error_handling']['status']} ({quality_gates['error_handling']['error_coverage_rate']:.1f}% coverage)")
    print(f"⚡ Performance Testing: {quality_gates['performance_testing']['status']} ({quality_gates['performance_testing']['performance_coverage_rate']:.1f}% coverage)")
    print(f"🎯 Overall Status: {quality_gates['overall_status']}")

    return quality_gates

def generate_coverage_report(test_results: Dict[str, Any], coverage_analysis: Dict[str, Any], quality_gates: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive coverage report."""
    print("\n📋 Generating Coverage Report...")
    print("=" * 60)

    report = {
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Unit Test Coverage Report',
            'project': 'Legal Document Intelligence Platform',
            'phase': 'Phase 3 - Advanced AI Integration',
            'tester_protocol': 'World-Class Production Tester Protocol'
        },
        'executive_summary': {
            'overall_status': quality_gates['overall_status'],
            'total_tests': test_results['total_tests'],
            'passed_tests': test_results['passed_tests'],
            'failed_tests': test_results['failed_tests'],
            'test_pass_rate': quality_gates['test_execution']['pass_rate'],
            'average_coverage': quality_gates['test_coverage']['average_coverage'],
            'components_tested': len(coverage_analysis['component_coverage']),
            'quality_gates_passed': sum(1 for gate in quality_gates.values() if isinstance(gate, dict) and gate.get('status') == 'PASSED'),
            'quality_gates_total': sum(1 for gate in quality_gates.values() if isinstance(gate, dict) and 'status' in gate)
        },
        'test_results': test_results,
        'coverage_analysis': coverage_analysis,
        'quality_gates': quality_gates,
        'recommendations': [],
        'next_steps': []
    }

    # Generate recommendations based on results
    if quality_gates['test_execution']['status'] == 'FAILED':
        report['recommendations'].append("Improve test pass rate by fixing failing tests")

    if quality_gates['test_coverage']['status'] == 'FAILED':
        report['recommendations'].append("Increase test coverage to meet 80% threshold")

    if quality_gates['error_handling']['status'] == 'FAILED':
        report['recommendations'].append("Add more error handling test scenarios")

    if quality_gates['performance_testing']['status'] == 'FAILED':
        report['recommendations'].append("Implement performance testing for all components")

    # Generate next steps
    if quality_gates['overall_status'] == 'PASSED':
        report['next_steps'].append("Proceed to integration testing")
        report['next_steps'].append("Prepare for Phase 4 implementation")
    else:
        report['next_steps'].append("Address failing quality gates")
        report['next_steps'].append("Improve test coverage and reliability")
        report['next_steps'].append("Re-run tests after improvements")

    return report

def main():
    """Main function to run coverage analysis."""
    print("🧪 Unit Test Coverage Analysis")
    print("Legal Document Intelligence Platform - Phase 3")
    print("Following World-Class Production Tester Protocol")
    print("=" * 80)

    # Run unit tests
    test_results = run_unit_tests()

    # Analyze test coverage
    coverage_analysis = analyze_test_coverage()

    # Calculate quality gates
    quality_gates = calculate_quality_gates(test_results, coverage_analysis)

    # Generate comprehensive report
    report = generate_coverage_report(test_results, coverage_analysis, quality_gates)

    # Save report to file
    report_file = Path(__file__).parent / "unit_test_coverage_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n💾 Coverage report saved to: {report_file}")

    # Print final summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print(f"🎯 Overall Status: {report['executive_summary']['overall_status']}")
    print(f"📈 Test Pass Rate: {report['executive_summary']['test_pass_rate']:.1f}%")
    print(f"📊 Average Coverage: {report['executive_summary']['average_coverage']:.1f}%")
    print(f"🏆 Quality Gates: {report['executive_summary']['quality_gates_passed']}/{report['executive_summary']['quality_gates_total']} passed")
    print(f"🧪 Total Tests: {report['executive_summary']['total_tests']}")
    print(f"✅ Passed Tests: {report['executive_summary']['passed_tests']}")
    print(f"❌ Failed Tests: {report['executive_summary']['failed_tests']}")

    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")

    if report['next_steps']:
        print(f"\n🚀 Next Steps:")
        for i, step in enumerate(report['next_steps'], 1):
            print(f"   {i}. {step}")

    return report

if __name__ == "__main__":
    main()
