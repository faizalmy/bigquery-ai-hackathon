#!/usr/bin/env python3
"""
Phase 3 Components Testing Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests all Phase 3 core platform components to ensure they work
together correctly and meet the performance requirements.
"""

import sys
import os
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from core.document_processor import LegalDocumentProcessor
from core.similarity_engine import SimilarityEngine
from core.predictive_engine import PredictiveEngine
from core.comprehensive_analyzer import ComprehensiveAnalyzer
from core.status_tracker import StatusTracker
from core.error_handler import ErrorHandler
from utils.bigquery_client import BigQueryClient
from config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase3Tester:
    """Comprehensive tester for Phase 3 components."""

    def __init__(self, project_id: str):
        """Initialize the Phase 3 tester."""
        self.project_id = project_id
        self.test_results = {}
        self.start_time = datetime.now()

    def test_document_processor(self, bq_client: BigQueryClient) -> Dict[str, Any]:
        """Test the document processor component."""
        logger.info("🔄 Testing Document Processor...")

        try:
            # Initialize processor
            processor = LegalDocumentProcessor(self.project_id, bq_client)

            # Test document
            test_document = {
                'document_id': 'test_doc_001',
                'content': 'This is a Supreme Court case involving constitutional law and First Amendment rights of public employees. The case involves a dispute over freedom of speech in the workplace.',
                'document_type': 'case_law',
                'metadata': {'source': 'test', 'jurisdiction': 'federal'}
            }

            # Test processing
            start_time = time.time()
            result = processor.process_document(test_document)
            processing_time = time.time() - start_time

            # Validate results
            success = (
                result.status == 'completed' and
                'ai_analysis' in result.results and
                'vector_analysis' in result.results and
                'predictive_analysis' in result.results and
                processing_time < 60  # Performance requirement
            )

            return {
                'component': 'document_processor',
                'status': 'passed' if success else 'failed',
                'processing_time': processing_time,
                'result_status': result.status,
                'has_ai_analysis': 'ai_analysis' in result.results,
                'has_vector_analysis': 'vector_analysis' in result.results,
                'has_predictive_analysis': 'predictive_analysis' in result.results,
                'errors': result.errors,
                'performance_requirement_met': processing_time < 60
            }

        except Exception as e:
            logger.error(f"❌ Document processor test failed: {e}")
            return {
                'component': 'document_processor',
                'status': 'failed',
                'error': str(e)
            }

    def test_similarity_engine(self, bq_client: BigQueryClient) -> Dict[str, Any]:
        """Test the similarity engine component."""
        logger.info("🔍 Testing Similarity Engine...")

        try:
            # Initialize engine
            engine = SimilarityEngine(self.project_id, bq_client)

            # Test content search
            test_query = "constitutional law and First Amendment rights"

            start_time = time.time()
            results = engine.search_by_content(test_query, top_k=5, similarity_threshold=0.6)
            search_time = time.time() - start_time

            # Validate results
            success = (
                isinstance(results, list) and
                search_time < 5  # Performance requirement
            )

            return {
                'component': 'similarity_engine',
                'status': 'passed' if success else 'failed',
                'search_time': search_time,
                'results_count': len(results),
                'performance_requirement_met': search_time < 5,
                'has_results': len(results) > 0
            }

        except Exception as e:
            logger.error(f"❌ Similarity engine test failed: {e}")
            return {
                'component': 'similarity_engine',
                'status': 'failed',
                'error': str(e)
            }

    def test_predictive_engine(self, bq_client: BigQueryClient) -> Dict[str, Any]:
        """Test the predictive engine component."""
        logger.info("🔮 Testing Predictive Engine...")

        try:
            # Initialize engine
            engine = PredictiveEngine(self.project_id, bq_client)

            # Test case data
            test_case = {
                'case_id': 'test_case_001',
                'content': 'This is a constitutional law case involving First Amendment rights and requires comprehensive analysis.',
                'type': 'constitutional_law',
                'metadata': {'jurisdiction': 'federal'}
            }

            # Test comprehensive analysis
            start_time = time.time()
            analysis = engine.analyze_case(test_case)
            analysis_time = time.time() - start_time

            # Validate results
            success = (
                analysis.case_id == 'test_case_001' and
                analysis.confidence_score > 0 and
                analysis_time < 20  # Performance requirement
            )

            return {
                'component': 'predictive_engine',
                'status': 'passed' if success else 'failed',
                'analysis_time': analysis_time,
                'confidence_score': analysis.confidence_score,
                'has_outcome_prediction': 'prediction' in analysis.outcome_prediction,
                'has_risk_assessment': 'risk_level' in analysis.risk_assessment,
                'strategy_count': len(analysis.strategy_recommendations),
                'performance_requirement_met': analysis_time < 20
            }

        except Exception as e:
            logger.error(f"❌ Predictive engine test failed: {e}")
            return {
                'component': 'predictive_engine',
                'status': 'failed',
                'error': str(e)
            }

    def test_comprehensive_analyzer(self, bq_client: BigQueryClient) -> Dict[str, Any]:
        """Test the comprehensive analyzer component."""
        logger.info("🔍 Testing Comprehensive Analyzer...")

        try:
            # Initialize analyzer
            analyzer = ComprehensiveAnalyzer(self.project_id, bq_client)

            # Test case data
            test_case = {
                'case_id': 'test_comprehensive_001',
                'content': 'This is a Supreme Court case involving constitutional law and First Amendment rights of public employees. The case involves a dispute over freedom of speech in the workplace and requires comprehensive legal analysis.',
                'document_type': 'case_law',
                'metadata': {'source': 'test', 'jurisdiction': 'federal'}
            }

            # Test comprehensive analysis
            start_time = time.time()
            report = analyzer.analyze_legal_case(test_case, generate_brief=False)
            analysis_time = time.time() - start_time

            # Validate results
            success = (
                report.case_id == 'test_comprehensive_001' and
                report.confidence_score > 0 and
                len(report.recommendations) > 0 and
                analysis_time < 60  # Performance requirement
            )

            return {
                'component': 'comprehensive_analyzer',
                'status': 'passed' if success else 'failed',
                'analysis_time': analysis_time,
                'confidence_score': report.confidence_score,
                'recommendations_count': len(report.recommendations),
                'has_similarity_analysis': len(report.similarity_analysis) > 0,
                'has_predictive_analysis': report.predictive_analysis is not None,
                'performance_requirement_met': analysis_time < 60
            }

        except Exception as e:
            logger.error(f"❌ Comprehensive analyzer test failed: {e}")
            return {
                'component': 'comprehensive_analyzer',
                'status': 'failed',
                'error': str(e)
            }

    def test_status_tracker(self) -> Dict[str, Any]:
        """Test the status tracker component."""
        logger.info("📊 Testing Status Tracker...")

        try:
            # Initialize tracker
            tracker = StatusTracker()

            # Test document tracking
            test_doc_id = 'test_status_001'
            metadata = {'test': True}

            # Start tracking
            metrics = tracker.start_processing(test_doc_id, metadata)

            # Update stages
            tracker.update_stage(test_doc_id, 'processing', 50)
            tracker.record_error(test_doc_id, 'Test error', 'test')
            tracker.record_retry(test_doc_id, 'Test retry')

            # Complete tracking
            tracker.complete_processing(test_doc_id, True, {'test_result': 'success'})

            # Get status
            status = tracker.get_document_status(test_doc_id)
            system_metrics = tracker.get_system_metrics()

            # Validate results
            success = (
                status is not None and
                status['status'] == 'completed' and
                system_metrics['total_documents_processed'] > 0
            )

            return {
                'component': 'status_tracker',
                'status': 'passed' if success else 'failed',
                'document_status': status['status'] if status else 'unknown',
                'total_processed': system_metrics['total_documents_processed'],
                'successful_documents': system_metrics['successful_documents']
            }

        except Exception as e:
            logger.error(f"❌ Status tracker test failed: {e}")
            return {
                'component': 'status_tracker',
                'status': 'failed',
                'error': str(e)
            }

    def test_error_handler(self) -> Dict[str, Any]:
        """Test the error handler component."""
        logger.info("⚠️ Testing Error Handler...")

        try:
            # Initialize handler
            handler = ErrorHandler()

            # Test error handling
            test_error = ValueError("Test error for validation")
            context = {'test': True, 'component': 'test'}

            # Handle error
            processing_error = handler.handle_error(test_error, context)

            # Test retry logic
            def failing_function():
                raise ValueError("Test retry error")

            def success_function():
                return "success"

            # Test retry
            result, error = handler.execute_with_retry(failing_function)

            # Test fallback
            fallback_result, fallback_error = handler.execute_with_fallback(
                failing_function, success_function
            )

            # Get error summary
            error_summary = handler.get_error_summary()

            # Validate results
            success = (
                processing_error.category is not None and
                processing_error.severity is not None and
                result is None and  # Failing function should return None
                error is not None and  # Should have error
                fallback_result == "success" and  # Fallback should succeed
                fallback_error is None and  # No error from fallback
                error_summary['total_errors'] > 0
            )

            return {
                'component': 'error_handler',
                'status': 'passed' if success else 'failed',
                'error_category': processing_error.category.value if processing_error.category else 'unknown',
                'error_severity': processing_error.severity.value if processing_error.severity else 'unknown',
                'retry_handled': error is not None,
                'fallback_successful': fallback_result == "success",
                'total_errors_logged': error_summary['total_errors']
            }

        except Exception as e:
            logger.error(f"❌ Error handler test failed: {e}")
            return {
                'component': 'error_handler',
                'status': 'failed',
                'error': str(e)
            }

    def run_comprehensive_tests(self, bq_client: BigQueryClient) -> Dict[str, Any]:
        """Run all Phase 3 component tests."""
        logger.info("🚀 Starting Comprehensive Phase 3 Testing...")

        # Test all components
        self.test_results['document_processor'] = self.test_document_processor(bq_client)
        self.test_results['similarity_engine'] = self.test_similarity_engine(bq_client)
        self.test_results['predictive_engine'] = self.test_predictive_engine(bq_client)
        self.test_results['comprehensive_analyzer'] = self.test_comprehensive_analyzer(bq_client)
        self.test_results['status_tracker'] = self.test_status_tracker()
        self.test_results['error_handler'] = self.test_error_handler()

        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests

        # Performance analysis
        performance_requirements_met = sum(
            1 for result in self.test_results.values()
            if result.get('performance_requirement_met', False)
        )

        # Generate summary
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()

        summary = {
            'overall_status': 'passed' if failed_tests == 0 else 'failed',
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'performance_requirements_met': performance_requirements_met,
            'total_testing_time': total_time,
            'test_results': self.test_results,
            'testing_timestamp': end_time.isoformat()
        }

        return summary

def main():
    """Main testing function."""
    print("🧪 Phase 3 Components Testing")
    print("=" * 60)

    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Test connection
        if not bq_client.test_connection():
            logger.error("❌ BigQuery connection test failed")
            return 1

        # Initialize tester
        tester = Phase3Tester(project_id)

        # Run comprehensive tests
        test_summary = tester.run_comprehensive_tests(bq_client)

        # Print results
        print("\n📊 PHASE 3 TESTING RESULTS:")
        print("=" * 40)

        overall_status = test_summary['overall_status']
        success_rate = test_summary['success_rate']

        print(f"🎯 Overall Status: {overall_status.upper()}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Testing Time: {test_summary['total_testing_time']:.2f}s")
        print(f"✅ Tests Passed: {test_summary['passed_tests']}/{test_summary['total_tests']}")
        print(f"❌ Tests Failed: {test_summary['failed_tests']}")

        print("\n📋 Component Results:")
        for component, result in test_summary['test_results'].items():
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            print(f"   {status_icon} {component}: {result['status']}")

            if 'error' in result:
                print(f"      Error: {result['error']}")

            if 'performance_requirement_met' in result:
                perf_icon = "✅" if result['performance_requirement_met'] else "⚠️"
                print(f"      Performance: {perf_icon}")

        print(f"\n🚀 Performance Requirements Met: {test_summary['performance_requirements_met']}/{test_summary['total_tests']}")

        if overall_status == 'passed':
            print("\n🎉 PHASE 3 COMPONENTS TESTING PASSED!")
            print("✅ All components are working correctly")
            print("🚀 Ready for Phase 4: API Development")
        else:
            print(f"\n⚠️  Phase 3 testing partially passed ({success_rate:.1f}%)")
            print("🔧 Some components need attention")

        return 0 if overall_status == 'passed' else 1

    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())


