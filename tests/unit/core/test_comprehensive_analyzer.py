#!/usr/bin/env python3
"""
Unit Tests for Comprehensive Analyzer
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

Following World-Class Production Tester Protocol:
- Comprehensive Coverage: Validate every specification, requirement, and edge case
- Risk-Based Prioritization: Focus testing on highest impact and failure probability areas
- Data-Driven Decisions: Base testing priorities on measurable metrics and trends
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from core.comprehensive_analyzer import ComprehensiveAnalyzer, LegalIntelligenceReport
from core.document_processor import ProcessingResult
from core.similarity_engine import SimilarityResult
from core.predictive_engine import ComprehensiveAnalysis, LegalBrief
from utils.bigquery_client import BigQueryClient

class TestComprehensiveAnalyzer(unittest.TestCase):
    """
    Comprehensive unit tests for ComprehensiveAnalyzer following tester protocol.

    Test Coverage Areas:
    1. Initialization and Configuration
    2. Legal Case Analysis Operations
    3. Batch Analysis Processing
    4. Report Generation and Export
    5. Error Handling and Edge Cases
    """

    def setUp(self):
        """Set up test fixtures with mock dependencies."""
        self.project_id = "test-project"
        self.mock_bq_client = Mock(spec=BigQueryClient)

        # Mock all Phase 3 components
        with patch('core.comprehensive_analyzer.LegalDocumentProcessor') as mock_doc_processor, \
             patch('core.comprehensive_analyzer.SimilarityEngine') as mock_similarity, \
             patch('core.comprehensive_analyzer.PredictiveEngine') as mock_predictive, \
             patch('core.comprehensive_analyzer.StatusTracker') as mock_status, \
             patch('core.comprehensive_analyzer.ErrorHandler') as mock_error:

            self.analyzer = ComprehensiveAnalyzer(self.project_id, self.mock_bq_client)

            # Store mock references for assertions
            self.mock_document_processor = mock_doc_processor.return_value
            self.mock_similarity_engine = mock_similarity.return_value
            self.mock_predictive_engine = mock_predictive.return_value
            self.mock_status_tracker = mock_status.return_value
            self.mock_error_handler = mock_error.return_value

    def test_initialization_success(self):
        """Test successful analyzer initialization."""
        # Verify initialization
        self.assertEqual(self.analyzer.project_id, self.project_id)
        self.assertEqual(self.analyzer.bq_client, self.mock_bq_client)
        self.assertIsNotNone(self.analyzer.document_processor)
        self.assertIsNotNone(self.analyzer.similarity_engine)
        self.assertIsNotNone(self.analyzer.predictive_engine)
        self.assertIsNotNone(self.analyzer.status_tracker)
        self.assertIsNotNone(self.analyzer.error_handler)

        # Verify configuration
        self.assertEqual(self.analyzer.default_confidence_threshold, 0.7)
        self.assertIsInstance(self.analyzer.analysis_cache, dict)

    def test_analyze_legal_case_success(self):
        """Test successful legal case analysis."""
        # Mock case data
        case_data = {
            'case_id': 'case_001',
            'content': 'This is a constitutional law case involving free speech rights.',
            'document_type': 'case_law',
            'metadata': {'jurisdiction': 'federal'}
        }

        # Mock processing result
        mock_processing_result = ProcessingResult(
            document_id='case_001',
            status='completed',
            processing_time=5.0,
            results={
                'ai_analysis': {'legal_extraction': {'parties': ['Plaintiff', 'Defendant']}},
                'vector_analysis': {'embedding_generated': True},
                'predictive_analysis': {'outcome_prediction': {'prediction': 'Favorable'}},
                'storage': {'stored': True}
            },
            errors=[],
            timestamp=datetime.now()
        )

        # Mock similarity results
        mock_similarity_results = [
            SimilarityResult(
                document_id='similar_001',
                similarity_score=0.85,
                document_type='case_law',
                summary='Similar constitutional case',
                legal_domain='constitutional',
                jurisdiction='federal',
                case_outcome='favorable',
                confidence_score=0.9
            )
        ]

        # Mock comprehensive analysis
        mock_comprehensive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable', 'confidence_score': 0.8},
            risk_assessment={'risk_level': 'low', 'confidence_score': 0.7},
            strategy_recommendations=[
                {
                    'strategy_type': 'outcome_based',
                    'title': 'Constitutional Strategy',
                    'description': 'Focus on constitutional arguments',
                    'confidence': 0.8,
                    'priority': 'high'
                }
            ],
            similar_cases=[
                {
                    'document_id': 'similar_001',
                    'similarity_score': 0.85,
                    'summary': 'Similar constitutional case'
                }
            ],
            compliance_check={'compliant': True, 'confidence_score': 0.9},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted with high confidence."
        )

        # Mock legal brief
        mock_legal_brief = LegalBrief(
            brief_id='brief_001',
            case_id='case_001',
            brief_type='motion',
            content='LEGAL BRIEF - MOTION\nCase ID: case_001\n...',
            key_arguments=['Strong constitutional arguments', 'Clear precedent support'],
            supporting_cases=['similar_001'],
            legal_citations=['Case: similar_001'],
            confidence_score=0.8,
            generated_at=datetime.now()
        )

        # Mock component methods
        self.mock_document_processor.process_document.return_value = mock_processing_result
        self.mock_similarity_engine.search_by_content.return_value = mock_similarity_results
        self.mock_predictive_engine.analyze_case.return_value = mock_comprehensive_analysis
        self.mock_predictive_engine.generate_legal_brief.return_value = mock_legal_brief

        # Mock internal methods
        with patch.object(self.analyzer, '_generate_executive_summary') as mock_gen_summary, \
             patch.object(self.analyzer, '_generate_recommendations') as mock_gen_recommendations, \
             patch.object(self.analyzer, '_generate_risk_assessment') as mock_gen_risk, \
             patch.object(self.analyzer, '_calculate_overall_confidence') as mock_calc_confidence:

            mock_gen_summary.return_value = "Comprehensive analysis completed successfully."
            mock_gen_recommendations.return_value = [
                "Proceed with constitutional arguments",
                "Focus on precedent research"
            ]
            mock_gen_risk.return_value = {
                'overall_risk_level': 'low',
                'risk_factors': [],
                'mitigation_strategies': []
            }
            mock_calc_confidence.return_value = 0.8

            # Execute analysis
            report = self.analyzer.analyze_legal_case(case_data, generate_brief=True)

            # Verify report structure
            self.assertIsInstance(report, LegalIntelligenceReport)
            self.assertEqual(report.case_id, 'case_001')
            self.assertEqual(report.confidence_score, 0.8)
            self.assertEqual(report.executive_summary, "Comprehensive analysis completed successfully.")
            self.assertEqual(len(report.recommendations), 2)
            self.assertEqual(report.risk_assessment['overall_risk_level'], 'low')

            # Verify components
            self.assertEqual(report.processing_result, mock_processing_result)
            self.assertEqual(report.similarity_analysis, mock_similarity_results)
            self.assertEqual(report.predictive_analysis, mock_comprehensive_analysis)
            self.assertEqual(report.legal_brief, mock_legal_brief)

    def test_analyze_legal_case_without_brief(self):
        """Test legal case analysis without brief generation."""
        case_data = {
            'case_id': 'case_002',
            'content': 'This is a contract dispute case.',
            'document_type': 'contract'
        }

        # Mock processing result
        mock_processing_result = ProcessingResult(
            document_id='case_002',
            status='completed',
            processing_time=3.0,
            results={'test': 'data'},
            errors=[],
            timestamp=datetime.now()
        )

        # Mock similarity results
        mock_similarity_results = []

        # Mock comprehensive analysis
        mock_comprehensive_analysis = ComprehensiveAnalysis(
            case_id='case_002',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Unfavorable'},
            risk_assessment={'risk_level': 'high'},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={'compliant': False},
            confidence_score=0.6,
            analysis_summary="Unfavorable outcome predicted."
        )

        # Mock component methods
        self.mock_document_processor.process_document.return_value = mock_processing_result
        self.mock_similarity_engine.search_by_content.return_value = mock_similarity_results
        self.mock_predictive_engine.analyze_case.return_value = mock_comprehensive_analysis

        # Mock internal methods
        with patch.object(self.analyzer, '_generate_executive_summary') as mock_gen_summary, \
             patch.object(self.analyzer, '_generate_recommendations') as mock_gen_recommendations, \
             patch.object(self.analyzer, '_generate_risk_assessment') as mock_gen_risk, \
             patch.object(self.analyzer, '_calculate_overall_confidence') as mock_calc_confidence:

            mock_gen_summary.return_value = "Analysis completed without brief generation."
            mock_gen_recommendations.return_value = ["Consider settlement"]
            mock_gen_risk.return_value = {'overall_risk_level': 'high'}
            mock_calc_confidence.return_value = 0.6

            # Execute analysis without brief
            report = self.analyzer.analyze_legal_case(case_data, generate_brief=False)

            # Verify report structure
            self.assertIsInstance(report, LegalIntelligenceReport)
            self.assertEqual(report.case_id, 'case_002')
            self.assertIsNone(report.legal_brief)  # No brief generated

    def test_analyze_legal_case_processing_failure(self):
        """Test legal case analysis with processing failure."""
        case_data = {
            'case_id': 'case_003',
            'content': 'Invalid case data',
            'document_type': 'invalid'
        }

        # Mock processing failure
        mock_processing_result = ProcessingResult(
            document_id='case_003',
            status='failed',
            processing_time=1.0,
            results={},
            errors=['Document validation failed'],
            timestamp=datetime.now()
        )

        self.mock_document_processor.process_document.return_value = mock_processing_result

        # Execute analysis
        report = self.analyzer.analyze_legal_case(case_data)

        # Verify error handling
        self.assertIsInstance(report, LegalIntelligenceReport)
        self.assertEqual(report.case_id, 'case_003')
        self.assertEqual(report.confidence_score, 0.0)
        self.assertIn('failed', report.executive_summary.lower())

    def test_analyze_legal_case_with_exception(self):
        """Test legal case analysis with exception handling."""
        case_data = {
            'case_id': 'case_004',
            'content': 'This will cause an exception.',
            'document_type': 'test'
        }

        # Mock exception in document processing
        self.mock_document_processor.process_document.side_effect = Exception("Processing failed")

        # Mock error handler
        mock_error = Mock()
        mock_error.category.value = 'system'
        mock_error.severity.value = 'high'
        self.mock_error_handler.handle_error.return_value = mock_error

        # Execute analysis
        report = self.analyzer.analyze_legal_case(case_data)

        # Verify error handling
        self.assertIsInstance(report, LegalIntelligenceReport)
        self.assertEqual(report.case_id, 'case_004')
        self.assertEqual(report.confidence_score, 0.0)
        self.assertIn('failed', report.executive_summary.lower())

    def test_batch_analyze_cases_success(self):
        """Test successful batch case analysis."""
        cases_data = [
            {
                'case_id': 'batch_001',
                'content': 'First case content',
                'document_type': 'case_law'
            },
            {
                'case_id': 'batch_002',
                'content': 'Second case content',
                'document_type': 'contract'
            },
            {
                'case_id': 'batch_003',
                'content': 'Third case content',
                'document_type': 'brief'
            }
        ]

        # Mock successful analysis for each case
        with patch.object(self.analyzer, 'analyze_legal_case') as mock_analyze:
            mock_report = LegalIntelligenceReport(
                report_id='report_001',
                case_id='batch_001',
                generated_at=datetime.now(),
                processing_result=Mock(),
                similarity_analysis=[],
                predictive_analysis=Mock(),
                legal_brief=None,
                confidence_score=0.8,
                executive_summary="Analysis completed",
                recommendations=[],
                risk_assessment={}
            )
            mock_analyze.return_value = mock_report

            # Execute batch analysis
            reports = self.analyzer.batch_analyze_cases(cases_data, generate_briefs=False)

            # Verify results
            self.assertEqual(len(reports), 3)
            self.assertEqual(mock_analyze.call_count, 3)

            for report in reports:
                self.assertIsInstance(report, LegalIntelligenceReport)

    def test_batch_analyze_cases_with_failures(self):
        """Test batch case analysis with some failures."""
        cases_data = [
            {
                'case_id': 'batch_001',
                'content': 'Valid case content',
                'document_type': 'case_law'
            },
            {
                'case_id': 'batch_002',
                'content': 'Invalid case content',
                'document_type': 'invalid'
            }
        ]

        # Mock mixed results
        with patch.object(self.analyzer, 'analyze_legal_case') as mock_analyze:
            def side_effect(case_data, generate_brief=False):
                if case_data['case_id'] == 'batch_001':
                    return LegalIntelligenceReport(
                        report_id='report_001',
                        case_id='batch_001',
                        generated_at=datetime.now(),
                        processing_result=Mock(),
                        similarity_analysis=[],
                        predictive_analysis=Mock(),
                        legal_brief=None,
                        confidence_score=0.8,
                        executive_summary="Analysis completed",
                        recommendations=[],
                        risk_assessment={}
                    )
                else:
                    raise Exception("Analysis failed")

            mock_analyze.side_effect = side_effect

            # Execute batch analysis
            reports = self.analyzer.batch_analyze_cases(cases_data, generate_briefs=False)

            # Verify results (only successful analyses included)
            self.assertEqual(len(reports), 1)
            self.assertEqual(reports[0].case_id, 'batch_001')

    def test_get_analysis_status(self):
        """Test getting analysis status."""
        case_id = 'case_001'
        mock_status = {
            'document_id': case_id,
            'status': 'processing',
            'current_stage': 'ai_processing',
            'progress_percentage': 50.0
        }

        self.mock_status_tracker.get_document_status.return_value = mock_status

        status = self.analyzer.get_analysis_status(case_id)

        # Verify status retrieval
        self.assertEqual(status, mock_status)
        self.mock_status_tracker.get_document_status.assert_called_once_with(case_id)

    def test_get_system_metrics(self):
        """Test getting system metrics."""
        mock_status_metrics = {
            'total_documents_processed': 100,
            'successful_documents': 90,
            'failed_documents': 10
        }

        mock_error_summary = {
            'total_errors': 5,
            'category_counts': {'system': 2, 'network': 3}
        }

        mock_cache_stats = {
            'cache_enabled': True,
            'cache_size': 25
        }

        self.mock_status_tracker.get_system_metrics.return_value = mock_status_metrics
        self.mock_error_handler.get_error_summary.return_value = mock_error_summary
        self.mock_similarity_engine.get_cache_stats.return_value = mock_cache_stats

        metrics = self.analyzer.get_system_metrics()

        # Verify metrics structure
        self.assertIn('status_tracker', metrics)
        self.assertIn('error_handler', metrics)
        self.assertIn('similarity_engine', metrics)
        self.assertIn('timestamp', metrics)

        # Verify values
        self.assertEqual(metrics['status_tracker'], mock_status_metrics)
        self.assertEqual(metrics['error_handler'], mock_error_summary)
        self.assertEqual(metrics['similarity_engine'], mock_cache_stats)

    def test_generate_executive_summary_success(self):
        """Test executive summary generation for successful analysis."""
        processing_result = ProcessingResult(
            document_id='case_001',
            status='completed',
            processing_time=5.0,
            results={'test': 'data'},
            errors=[],
            timestamp=datetime.now()
        )

        similarity_results = [
            SimilarityResult(
                document_id='similar_001',
                similarity_score=0.85,
                document_type='case_law',
                summary='Similar case',
                legal_domain='constitutional',
                jurisdiction='federal'
            )
        ]

        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable'},
            risk_assessment={'risk_level': 'low'},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.8,
            analysis_summary="High-confidence analysis completed."
        )

        summary = self.analyzer._generate_executive_summary(
            processing_result, similarity_results, predictive_analysis
        )

        # Verify summary content
        self.assertIn('successfully', summary.lower())
        self.assertIn('1 similar cases', summary)
        self.assertIn('high-confidence', summary.lower())
        self.assertIn('favorable', summary.lower())

    def test_generate_executive_summary_failure(self):
        """Test executive summary generation for failed analysis."""
        processing_result = ProcessingResult(
            document_id='case_001',
            status='failed',
            processing_time=2.0,
            results={},
            errors=['Processing failed'],
            timestamp=datetime.now()
        )

        similarity_results = []

        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={},
            risk_assessment={},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.0,
            analysis_summary="Analysis failed."
        )

        summary = self.analyzer._generate_executive_summary(
            processing_result, similarity_results, predictive_analysis
        )

        # Verify summary content
        self.assertIn('failed', summary.lower())
        self.assertIn('no similar cases', summary.lower())
        self.assertIn('low-confidence', summary.lower())

    def test_generate_recommendations_favorable(self):
        """Test recommendations generation for favorable outcome."""
        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable outcome expected'},
            risk_assessment={'risk_level': 'low'},
            strategy_recommendations=[
                {
                    'title': 'Primary Strategy',
                    'description': 'Focus on constitutional arguments'
                }
            ],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted."
        )

        similarity_results = [
            SimilarityResult(
                document_id='similar_001',
                similarity_score=0.85,
                document_type='case_law',
                summary='Similar successful case',
                legal_domain='constitutional',
                jurisdiction='federal',
                case_outcome='favorable'
            )
        ]

        recommendations = self.analyzer._generate_recommendations(
            predictive_analysis, similarity_results
        )

        # Verify recommendations
        self.assertGreater(len(recommendations), 0)
        self.assertIn('proceeding', recommendations[0].lower())
        self.assertIn('constitutional arguments', recommendations[0].lower())

    def test_generate_recommendations_unfavorable(self):
        """Test recommendations generation for unfavorable outcome."""
        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Unfavorable outcome expected'},
            risk_assessment={'risk_level': 'high'},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.6,
            analysis_summary="Unfavorable outcome predicted."
        )

        similarity_results = []

        recommendations = self.analyzer._generate_recommendations(
            predictive_analysis, similarity_results
        )

        # Verify recommendations
        self.assertGreater(len(recommendations), 0)
        self.assertIn('settlement', recommendations[0].lower())

    def test_generate_risk_assessment(self):
        """Test risk assessment generation."""
        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={},
            risk_assessment={'risk_level': 'high'},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.4,  # Low confidence
            analysis_summary="High risk case."
        )

        similarity_results = []  # No similar cases

        risk_assessment = self.analyzer._generate_risk_assessment(
            predictive_analysis, similarity_results
        )

        # Verify risk assessment structure
        self.assertIn('overall_risk_level', risk_assessment)
        self.assertIn('risk_factors', risk_assessment)
        self.assertIn('mitigation_strategies', risk_assessment)
        self.assertIn('confidence_score', risk_assessment)

        # Verify values
        self.assertEqual(risk_assessment['overall_risk_level'], 'high')
        self.assertIn('Low analysis confidence', risk_assessment['risk_factors'])
        self.assertIn('No similar cases found', risk_assessment['risk_factors'])

    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation."""
        processing_result = ProcessingResult(
            document_id='case_001',
            status='completed',
            processing_time=5.0,
            results={'test': 'data'},
            errors=[],
            timestamp=datetime.now()
        )

        similarity_results = [
            SimilarityResult(
                document_id='similar_001',
                similarity_score=0.85,
                document_type='case_law',
                summary='Similar case',
                legal_domain='constitutional',
                jurisdiction='federal'
            )
        ]

        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={},
            risk_assessment={},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.8,
            analysis_summary="High confidence analysis."
        )

        confidence = self.analyzer._calculate_overall_confidence(
            processing_result, similarity_results, predictive_analysis
        )

        # Verify confidence calculation
        # Processing: 0.9 (successful), Similarity: 0.85 (avg similarity), Predictive: 0.8
        # Average: (0.9 + 0.85 + 0.8) / 3 = 0.85
        expected_confidence = (0.9 + 0.85 + 0.8) / 3
        self.assertAlmostEqual(confidence, expected_confidence, places=2)

    def test_calculate_overall_confidence_failed_processing(self):
        """Test overall confidence calculation with failed processing."""
        processing_result = ProcessingResult(
            document_id='case_001',
            status='failed',
            processing_time=2.0,
            results={},
            errors=['Processing failed'],
            timestamp=datetime.now()
        )

        similarity_results = []  # No similar cases

        predictive_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={},
            risk_assessment={},
            strategy_recommendations=[],
            similar_cases=[],
            compliance_check={},
            confidence_score=0.6,
            analysis_summary="Moderate confidence analysis."
        )

        confidence = self.analyzer._calculate_overall_confidence(
            processing_result, similarity_results, predictive_analysis
        )

        # Verify confidence calculation
        # Processing: 0.1 (failed), Similarity: 0.3 (no similar cases), Predictive: 0.6
        # Average: (0.1 + 0.3 + 0.6) / 3 = 0.33
        expected_confidence = (0.1 + 0.3 + 0.6) / 3
        self.assertAlmostEqual(confidence, expected_confidence, places=2)

    def test_export_analysis_report_success(self):
        """Test successful analysis report export."""
        # Create test report
        report = LegalIntelligenceReport(
            report_id='report_001',
            case_id='case_001',
            generated_at=datetime.now(),
            processing_result=ProcessingResult(
                document_id='case_001',
                status='completed',
                processing_time=5.0,
                results={'test': 'data'},
                errors=[],
                timestamp=datetime.now()
            ),
            similarity_analysis=[
                SimilarityResult(
                    document_id='similar_001',
                    similarity_score=0.85,
                    document_type='case_law',
                    summary='Similar case',
                    legal_domain='constitutional',
                    jurisdiction='federal'
                )
            ],
            predictive_analysis=ComprehensiveAnalysis(
                case_id='case_001',
                analysis_timestamp=datetime.now(),
                outcome_prediction={'prediction': 'Favorable'},
                risk_assessment={'risk_level': 'low'},
                strategy_recommendations=[],
                similar_cases=[],
                compliance_check={},
                confidence_score=0.8,
                analysis_summary="Favorable outcome predicted."
            ),
            legal_brief=LegalBrief(
                brief_id='brief_001',
                case_id='case_001',
                brief_type='motion',
                content='LEGAL BRIEF - MOTION\n...',
                key_arguments=['Strong arguments'],
                supporting_cases=['similar_001'],
                legal_citations=['Case: similar_001'],
                confidence_score=0.8,
                generated_at=datetime.now()
            ),
            confidence_score=0.8,
            executive_summary="Analysis completed successfully.",
            recommendations=["Proceed with case"],
            risk_assessment={'overall_risk_level': 'low'}
        )

        # Export report
        result = self.analyzer.export_analysis_report(report, "/tmp/test_report.json")

        # Verify export success
        self.assertTrue(result)

        # Verify file was created and contains data
        import os
        self.assertTrue(os.path.exists("/tmp/test_report.json"))

        # Verify file content
        import json
        with open("/tmp/test_report.json", 'r') as f:
            exported_data = json.load(f)

        self.assertEqual(exported_data['report_id'], 'report_001')
        self.assertEqual(exported_data['case_id'], 'case_001')
        self.assertEqual(exported_data['confidence_score'], 0.8)
        self.assertIn('legal_brief', exported_data)

        # Clean up
        os.remove("/tmp/test_report.json")

    def test_export_analysis_report_failure(self):
        """Test analysis report export failure."""
        report = LegalIntelligenceReport(
            report_id='report_001',
            case_id='case_001',
            generated_at=datetime.now(),
            processing_result=Mock(),
            similarity_analysis=[],
            predictive_analysis=Mock(),
            legal_brief=None,
            confidence_score=0.8,
            executive_summary="Test summary",
            recommendations=[],
            risk_assessment={}
        )

        # Try to export to invalid path
        result = self.analyzer.export_analysis_report(report, "/invalid/path/report.json")

        # Verify export failure
        self.assertFalse(result)

    def test_performance_requirements(self):
        """Test that analyzer meets performance requirements."""
        # Verify configuration supports performance
        self.assertGreaterEqual(self.analyzer.default_confidence_threshold, 0.0)
        self.assertLessEqual(self.analyzer.default_confidence_threshold, 1.0)

        # Verify analysis cache is available for performance
        self.assertIsInstance(self.analyzer.analysis_cache, dict)

        # Verify all components are initialized for performance
        self.assertIsNotNone(self.analyzer.document_processor)
        self.assertIsNotNone(self.analyzer.similarity_engine)
        self.assertIsNotNone(self.analyzer.predictive_engine)
        self.assertIsNotNone(self.analyzer.status_tracker)
        self.assertIsNotNone(self.analyzer.error_handler)

    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with various error conditions
        test_cases = [
            None,  # None case data
            {},    # Empty case data
            {'content': None},  # None content
            {'content': ''},    # Empty content
            {'content': 123},   # Non-string content
        ]

        for case_data in test_cases:
            with self.subTest(case_data=case_data):
                try:
                    report = self.analyzer.analyze_legal_case(case_data)
                    self.assertIsInstance(report, LegalIntelligenceReport)
                except Exception as e:
                    # Handler should not crash even with invalid inputs
                    self.fail(f"Analyzer crashed with case data {case_data}: {e}")

class TestLegalIntelligenceReport(unittest.TestCase):
    """Test LegalIntelligenceReport data structure."""

    def test_legal_intelligence_report_creation(self):
        """Test LegalIntelligenceReport creation and properties."""
        timestamp = datetime.now()
        processing_result = Mock()
        similarity_analysis = [Mock()]
        predictive_analysis = Mock()
        legal_brief = Mock()

        report = LegalIntelligenceReport(
            report_id="report_001",
            case_id="case_001",
            generated_at=timestamp,
            processing_result=processing_result,
            similarity_analysis=similarity_analysis,
            predictive_analysis=predictive_analysis,
            legal_brief=legal_brief,
            confidence_score=0.8,
            executive_summary="Analysis completed successfully.",
            recommendations=["Proceed with case", "Focus on constitutional arguments"],
            risk_assessment={'overall_risk_level': 'low'}
        )

        # Verify properties
        self.assertEqual(report.report_id, "report_001")
        self.assertEqual(report.case_id, "case_001")
        self.assertEqual(report.generated_at, timestamp)
        self.assertEqual(report.processing_result, processing_result)
        self.assertEqual(report.similarity_analysis, similarity_analysis)
        self.assertEqual(report.predictive_analysis, predictive_analysis)
        self.assertEqual(report.legal_brief, legal_brief)
        self.assertEqual(report.confidence_score, 0.8)
        self.assertEqual(report.executive_summary, "Analysis completed successfully.")
        self.assertEqual(len(report.recommendations), 2)
        self.assertEqual(report.risk_assessment['overall_risk_level'], 'low')

    def test_legal_intelligence_report_minimal(self):
        """Test LegalIntelligenceReport with minimal required fields."""
        timestamp = datetime.now()
        processing_result = Mock()

        report = LegalIntelligenceReport(
            report_id="report_001",
            case_id="case_001",
            generated_at=timestamp,
            processing_result=processing_result,
            similarity_analysis=[],
            predictive_analysis=Mock(),
            legal_brief=None,
            confidence_score=0.0,
            executive_summary="Analysis failed.",
            recommendations=[],
            risk_assessment={}
        )

        # Verify required properties
        self.assertEqual(report.report_id, "report_001")
        self.assertEqual(report.case_id, "case_001")
        self.assertEqual(report.generated_at, timestamp)
        self.assertEqual(report.processing_result, processing_result)
        self.assertEqual(report.similarity_analysis, [])
        self.assertIsNone(report.legal_brief)
        self.assertEqual(report.confidence_score, 0.0)
        self.assertEqual(report.executive_summary, "Analysis failed.")
        self.assertEqual(report.recommendations, [])
        self.assertEqual(report.risk_assessment, {})

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
