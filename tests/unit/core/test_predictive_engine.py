#!/usr/bin/env python3
"""
Unit Tests for Predictive Engine
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

from core.predictive_engine import PredictiveEngine, ComprehensiveAnalysis, LegalBrief
from utils.bigquery_client import BigQueryClient

class TestPredictiveEngine(unittest.TestCase):
    """
    Comprehensive unit tests for PredictiveEngine following tester protocol.

    Test Coverage Areas:
    1. Initialization and Configuration
    2. Case Analysis Operations
    3. Legal Brief Generation
    4. Risk Assessment and Strategy Recommendations
    5. Error Handling and Edge Cases
    """

    def setUp(self):
        """Set up test fixtures with mock dependencies."""
        self.project_id = "test-project"
        self.mock_bq_client = Mock(spec=BigQueryClient)

        # Mock the predictive analytics and similarity engine
        with patch('core.predictive_engine.PredictiveAnalytics') as mock_predictive, \
             patch('core.predictive_engine.SimilarityEngine') as mock_similarity:

            self.engine = PredictiveEngine(self.project_id, self.mock_bq_client)

            # Store mock references for assertions
            self.mock_predictive_analytics = mock_predictive.return_value
            self.mock_similarity_engine = mock_similarity.return_value

    def test_initialization_success(self):
        """Test successful engine initialization."""
        # Verify initialization
        self.assertEqual(self.engine.project_id, self.project_id)
        self.assertEqual(self.engine.bq_client, self.mock_bq_client)
        self.assertIsNotNone(self.engine.predictive_analytics)
        self.assertIsNotNone(self.engine.similarity_engine)

        # Verify configuration
        self.assertEqual(self.engine.default_confidence_threshold, 0.7)
        self.assertEqual(self.engine.max_similar_cases, 10)
        self.assertIsInstance(self.engine.analysis_cache, dict)

    def test_analyze_case_success(self):
        """Test successful comprehensive case analysis."""
        # Mock case data
        case_data = {
            'case_id': 'case_001',
            'content': 'This is a constitutional law case involving free speech rights.',
            'type': 'constitutional_law',
            'metadata': {'jurisdiction': 'federal'}
        }

        # Mock predictive analytics results
        self.mock_predictive_analytics.predict_case_outcome.return_value = {
            'prediction': 'Favorable',
            'confidence_score': 0.85,
            'reasoning': 'Strong constitutional arguments'
        }

        self.mock_predictive_analytics.assess_legal_risk.return_value = {
            'risk_level': 'low',
            'confidence_score': 0.8,
            'risk_factors': ['Strong precedent', 'Clear constitutional basis']
        }

        self.mock_predictive_analytics.generate_legal_strategy.return_value = {
            'strategy': 'File motion for summary judgment',
            'confidence_score': 0.75,
            'steps': ['Research precedent', 'Draft motion', 'File with court']
        }

        self.mock_predictive_analytics.check_compliance.return_value = {
            'compliant': True,
            'confidence_score': 0.9,
            'compliance_issues': []
        }

        # Mock similar cases
        mock_similar_cases = [
            {
                'document_id': 'similar_001',
                'similarity_score': 0.85,
                'document_type': 'case_law',
                'legal_domain': 'constitutional',
                'jurisdiction': 'federal',
                'case_outcome': 'favorable',
                'summary': 'Similar constitutional case'
            }
        ]

        with patch.object(self.engine, '_find_similar_cases_for_analysis', return_value=mock_similar_cases), \
             patch.object(self.engine, '_generate_strategy_recommendations') as mock_gen_strategies, \
             patch.object(self.engine, '_calculate_analysis_confidence') as mock_calc_confidence, \
             patch.object(self.engine, '_generate_analysis_summary') as mock_gen_summary:

            mock_gen_strategies.return_value = [
                {
                    'strategy_type': 'outcome_based',
                    'title': 'Constitutional Strategy',
                    'description': 'Focus on constitutional arguments',
                    'confidence': 0.85,
                    'priority': 'high'
                }
            ]
            mock_calc_confidence.return_value = 0.8
            mock_gen_summary.return_value = "High-confidence analysis with favorable outcome prediction."

            analysis = self.engine.analyze_case(case_data)

            # Verify analysis structure
            self.assertIsInstance(analysis, ComprehensiveAnalysis)
            self.assertEqual(analysis.case_id, 'case_001')
            self.assertEqual(analysis.confidence_score, 0.8)
            self.assertEqual(analysis.analysis_summary, "High-confidence analysis with favorable outcome prediction.")

            # Verify components
            self.assertIn('prediction', analysis.outcome_prediction)
            self.assertIn('risk_level', analysis.risk_assessment)
            self.assertEqual(len(analysis.strategy_recommendations), 1)
            self.assertEqual(len(analysis.similar_cases), 1)
            self.assertIn('compliant', analysis.compliance_check)

    def test_analyze_case_with_error(self):
        """Test case analysis with error handling."""
        case_data = {
            'case_id': 'case_001',
            'content': 'Test case content'
        }

        # Mock error in predictive analytics
        self.mock_predictive_analytics.predict_case_outcome.side_effect = Exception("Analysis failed")

        analysis = self.engine.analyze_case(case_data)

        # Verify error handling
        self.assertIsInstance(analysis, ComprehensiveAnalysis)
        self.assertEqual(analysis.case_id, 'case_001')
        self.assertEqual(analysis.confidence_score, 0.0)
        self.assertIn('error', analysis.outcome_prediction)
        self.assertIn('Analysis failed', analysis.analysis_summary)

    def test_generate_legal_brief_success(self):
        """Test successful legal brief generation."""
        case_data = {
            'case_id': 'case_001',
            'content': 'This is a contract dispute case.'
        }

        # Mock comprehensive analysis
        mock_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable'},
            risk_assessment={'risk_level': 'low'},
            strategy_recommendations=[
                {
                    'strategy_type': 'outcome_based',
                    'title': 'Contract Strategy',
                    'description': 'Focus on contract terms'
                }
            ],
            similar_cases=[
                {
                    'document_id': 'similar_001',
                    'summary': 'Similar contract case'
                }
            ],
            compliance_check={'compliant': True},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted."
        )

        with patch.object(self.engine, 'analyze_case', return_value=mock_analysis), \
             patch.object(self.engine, '_generate_brief_content') as mock_gen_content, \
             patch.object(self.engine, '_extract_key_arguments') as mock_extract_args, \
             patch.object(self.engine, '_extract_legal_citations') as mock_extract_citations:

            mock_gen_content.return_value = "LEGAL BRIEF - MOTION\nCase ID: case_001\n..."
            mock_extract_args.return_value = ["Strong contract terms", "Clear breach evidence"]
            mock_extract_citations.return_value = ["Case: similar_001"]

            brief = self.engine.generate_legal_brief(case_data, brief_type="motion")

            # Verify brief structure
            self.assertIsInstance(brief, LegalBrief)
            self.assertEqual(brief.case_id, 'case_001')
            self.assertEqual(brief.brief_type, 'motion')
            self.assertEqual(brief.confidence_score, 0.8)
            self.assertEqual(len(brief.key_arguments), 2)
            self.assertEqual(len(brief.supporting_cases), 1)
            self.assertEqual(len(brief.legal_citations), 1)
            self.assertIn('LEGAL BRIEF - MOTION', brief.content)

    def test_generate_legal_brief_with_error(self):
        """Test legal brief generation with error handling."""
        case_data = {
            'case_id': 'case_001',
            'content': 'Test case content'
        }

        # Mock error in analysis
        with patch.object(self.engine, 'analyze_case', side_effect=Exception("Analysis failed")):
            brief = self.engine.generate_legal_brief(case_data, brief_type="motion")

            # Verify error handling
            self.assertIsInstance(brief, LegalBrief)
            self.assertEqual(brief.case_id, 'case_001')
            self.assertEqual(brief.brief_type, 'motion')
            self.assertEqual(brief.confidence_score, 0.0)
            self.assertIn('Brief generation failed', brief.content)

    def test_assess_litigation_risk_success(self):
        """Test successful litigation risk assessment."""
        case_data = {
            'case_id': 'case_001',
            'content': 'This is a high-risk litigation case.'
        }

        # Mock risk assessment results
        self.mock_predictive_analytics.assess_legal_risk.return_value = {
            'risk_level': 'high',
            'confidence_score': 0.8,
            'risk_factors': ['Complex legal issues', 'High damages']
        }

        self.mock_predictive_analytics.predict_case_outcome.return_value = {
            'prediction': 'Unfavorable',
            'confidence_score': 0.7
        }

        with patch.object(self.engine, '_calculate_litigation_risk_factors') as mock_calc_factors, \
             patch.object(self.engine, '_generate_risk_mitigation_strategies') as mock_gen_strategies, \
             patch.object(self.engine, '_determine_overall_risk_level') as mock_determine_level:

            mock_calc_factors.return_value = {
                'case_complexity': 'high',
                'jurisdiction_risk': 'medium',
                'precedent_risk': 'high',
                'financial_risk': 'high',
                'timeline_risk': 'medium'
            }
            mock_gen_strategies.return_value = [
                'Engage specialized legal counsel',
                'Conduct thorough precedent research'
            ]
            mock_determine_level.return_value = 'high'

            risk_assessment = self.engine.assess_litigation_risk(case_data)

            # Verify risk assessment structure
            self.assertIn('risk_assessment', risk_assessment)
            self.assertIn('outcome_prediction', risk_assessment)
            self.assertIn('risk_factors', risk_assessment)
            self.assertIn('mitigation_strategies', risk_assessment)
            self.assertIn('overall_risk_level', risk_assessment)
            self.assertIn('assessment_timestamp', risk_assessment)

            # Verify values
            self.assertEqual(risk_assessment['overall_risk_level'], 'high')
            self.assertEqual(len(risk_assessment['mitigation_strategies']), 2)

    def test_assess_litigation_risk_with_error(self):
        """Test litigation risk assessment with error handling."""
        case_data = {
            'case_id': 'case_001',
            'content': 'Test case content'
        }

        # Mock error in risk assessment
        self.mock_predictive_analytics.assess_legal_risk.side_effect = Exception("Risk assessment failed")

        risk_assessment = self.engine.assess_litigation_risk(case_data)

        # Verify error handling
        self.assertIn('error', risk_assessment)
        self.assertEqual(risk_assessment['error'], 'Risk assessment failed')

    def test_recommend_strategies_success(self):
        """Test successful strategy recommendations."""
        case_data = {
            'case_id': 'case_001',
            'content': 'This is a contract dispute case.'
        }

        # Mock comprehensive analysis
        mock_analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable', 'confidence_score': 0.8},
            risk_assessment={'risk_level': 'low', 'confidence_score': 0.7},
            strategy_recommendations=[],
            similar_cases=[
                {
                    'document_id': 'similar_001',
                    'similarity_score': 0.85,
                    'summary': 'Similar case'
                }
            ],
            compliance_check={'compliant': True},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted."
        )

        with patch.object(self.engine, 'analyze_case', return_value=mock_analysis), \
             patch.object(self.engine, '_generate_strategy_recommendations') as mock_gen_strategies, \
             patch.object(self.engine, '_rank_strategies') as mock_rank_strategies:

            mock_strategies = [
                {
                    'strategy_type': 'outcome_based',
                    'title': 'Contract Strategy',
                    'description': 'Focus on contract terms',
                    'confidence': 0.8,
                    'priority': 'high'
                },
                {
                    'strategy_type': 'risk_mitigation',
                    'title': 'Risk Strategy',
                    'description': 'Mitigate identified risks',
                    'confidence': 0.7,
                    'priority': 'medium'
                }
            ]

            mock_gen_strategies.return_value = mock_strategies
            mock_rank_strategies.return_value = mock_strategies  # Already ranked

            strategies = self.engine.recommend_strategies(case_data)

            # Verify strategies
            self.assertEqual(len(strategies), 2)
            self.assertEqual(strategies[0]['strategy_type'], 'outcome_based')
            self.assertEqual(strategies[1]['strategy_type'], 'risk_mitigation')

    def test_recommend_strategies_with_error(self):
        """Test strategy recommendations with error handling."""
        case_data = {
            'case_id': 'case_001',
            'content': 'Test case content'
        }

        # Mock error in analysis
        with patch.object(self.engine, 'analyze_case', side_effect=Exception("Analysis failed")):
            strategies = self.engine.recommend_strategies(case_data)

            # Verify error handling
            self.assertEqual(len(strategies), 1)
            self.assertIn('error', strategies[0])
            self.assertEqual(strategies[0]['error'], 'Analysis failed')

    def test_find_similar_cases_for_analysis(self):
        """Test finding similar cases for analysis context."""
        case_data = {
            'content': 'This is a constitutional law case.',
            'type': 'constitutional_law'
        }

        # Mock similarity search results
        mock_similarity_results = [
            Mock(
                document_id='similar_001',
                similarity_score=0.85,
                document_type='case_law',
                legal_domain='constitutional',
                jurisdiction='federal',
                case_outcome='favorable',
                summary='Similar constitutional case'
            ),
            Mock(
                document_id='similar_002',
                similarity_score=0.75,
                document_type='case_law',
                legal_domain='constitutional',
                jurisdiction='state',
                case_outcome='unfavorable',
                summary='Another constitutional case'
            )
        ]

        self.mock_similarity_engine.search_by_content.return_value = mock_similarity_results

        similar_cases = self.engine._find_similar_cases_for_analysis(case_data)

        # Verify similar cases
        self.assertEqual(len(similar_cases), 2)
        self.assertEqual(similar_cases[0]['document_id'], 'similar_001')
        self.assertEqual(similar_cases[0]['similarity_score'], 0.85)
        self.assertEqual(similar_cases[1]['document_id'], 'similar_002')
        self.assertEqual(similar_cases[1]['similarity_score'], 0.75)

    def test_find_similar_cases_for_analysis_with_error(self):
        """Test finding similar cases with error handling."""
        case_data = {
            'content': 'Test case content'
        }

        # Mock error in similarity search
        self.mock_similarity_engine.search_by_content.side_effect = Exception("Search failed")

        similar_cases = self.engine._find_similar_cases_for_analysis(case_data)

        # Verify error handling
        self.assertEqual(len(similar_cases), 0)

    def test_generate_strategy_recommendations(self):
        """Test strategy recommendations generation."""
        case_data = {
            'content': 'This is a contract dispute case.'
        }

        outcome_result = {
            'prediction': 'Favorable',
            'confidence_score': 0.8
        }

        risk_result = {
            'risk_level': 'low',
            'confidence_score': 0.7
        }

        similar_cases = [
            {
                'document_id': 'similar_001',
                'similarity_score': 0.85,
                'summary': 'Similar case'
            }
        ]

        strategies = self.engine._generate_strategy_recommendations(
            case_data, outcome_result, risk_result, similar_cases
        )

        # Verify strategies generated
        self.assertEqual(len(strategies), 3)  # outcome, risk, and similar case strategies

        # Verify outcome-based strategy
        outcome_strategy = strategies[0]
        self.assertEqual(outcome_strategy['strategy_type'], 'outcome_based')
        self.assertIn('Favorable', outcome_strategy['description'])
        self.assertEqual(outcome_strategy['confidence'], 0.8)

        # Verify risk-based strategy
        risk_strategy = strategies[1]
        self.assertEqual(risk_strategy['strategy_type'], 'risk_mitigation')
        self.assertIn('low', risk_strategy['description'])
        self.assertEqual(risk_strategy['confidence'], 0.7)

        # Verify precedent-based strategy
        precedent_strategy = strategies[2]
        self.assertEqual(precedent_strategy['strategy_type'], 'precedent_based')
        self.assertIn('1 similar cases', precedent_strategy['description'])
        self.assertEqual(len(precedent_strategy['supporting_cases']), 1)

    def test_calculate_analysis_confidence(self):
        """Test analysis confidence calculation."""
        outcome_result = {'confidence_score': 0.8}
        risk_result = {'confidence_score': 0.7}
        strategy_result = {'confidence_score': 0.75}
        compliance_result = {'confidence_score': 0.9}

        confidence = self.engine._calculate_analysis_confidence(
            outcome_result, risk_result, strategy_result, compliance_result
        )

        # Verify confidence calculation (average of all scores)
        expected_confidence = (0.8 + 0.7 + 0.75 + 0.9) / 4
        self.assertEqual(confidence, expected_confidence)

    def test_calculate_analysis_confidence_missing_scores(self):
        """Test analysis confidence calculation with missing scores."""
        outcome_result = {'confidence_score': 0.8}
        risk_result = {}  # Missing confidence score
        strategy_result = {'confidence_score': 0.75}
        compliance_result = {}  # Missing confidence score

        confidence = self.engine._calculate_analysis_confidence(
            outcome_result, risk_result, strategy_result, compliance_result
        )

        # Verify confidence calculation (average of available scores)
        expected_confidence = (0.8 + 0.75) / 2
        self.assertEqual(confidence, expected_confidence)

    def test_calculate_analysis_confidence_no_scores(self):
        """Test analysis confidence calculation with no scores."""
        outcome_result = {}
        risk_result = {}
        strategy_result = {}
        compliance_result = {}

        confidence = self.engine._calculate_analysis_confidence(
            outcome_result, risk_result, strategy_result, compliance_result
        )

        # Verify default confidence
        self.assertEqual(confidence, 0.5)

    def test_generate_analysis_summary(self):
        """Test analysis summary generation."""
        outcome_result = {'prediction': 'Favorable'}
        risk_result = {'risk_level': 'low'}
        strategy_recommendations = [
            {'title': 'Strategy 1', 'description': 'First strategy'},
            {'title': 'Strategy 2', 'description': 'Second strategy'}
        ]
        confidence_score = 0.8

        summary = self.engine._generate_analysis_summary(
            outcome_result, risk_result, strategy_recommendations, confidence_score
        )

        # Verify summary content
        self.assertIn('Favorable', summary)
        self.assertIn('low', summary)
        self.assertIn('2 strategy recommendations', summary)
        self.assertIn('high', summary)  # confidence level

    def test_generate_brief_content(self):
        """Test brief content generation."""
        analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable'},
            risk_assessment={'risk_level': 'low'},
            strategy_recommendations=[
                {
                    'title': 'Contract Strategy',
                    'description': 'Focus on contract terms'
                }
            ],
            similar_cases=[
                {
                    'document_id': 'similar_001',
                    'summary': 'Similar contract case'
                }
            ],
            compliance_check={'compliant': True},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted."
        )

        content = self.engine._generate_brief_content(analysis, "motion")

        # Verify brief content structure
        self.assertIn('LEGAL BRIEF - MOTION', content)
        self.assertIn('Case ID: case_001', content)
        self.assertIn('Favorable outcome predicted.', content)
        self.assertIn('PREDICTED OUTCOME:', content)
        self.assertIn('Favorable', content)
        self.assertIn('RISK ASSESSMENT:', content)
        self.assertIn('low', content)
        self.assertIn('RECOMMENDED STRATEGIES:', content)
        self.assertIn('Contract Strategy', content)
        self.assertIn('RELEVANT PRECEDENTS:', content)
        self.assertIn('similar_001', content)

    def test_extract_key_arguments(self):
        """Test key arguments extraction."""
        analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={'prediction': 'Favorable'},
            risk_assessment={'risk_level': 'low'},
            strategy_recommendations=[],
            similar_cases=[
                {'document_id': 'similar_001', 'summary': 'Similar case'},
                {'document_id': 'similar_002', 'summary': 'Another case'}
            ],
            compliance_check={'compliant': True},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted."
        )

        arguments = self.engine._extract_key_arguments(analysis, "motion")

        # Verify arguments
        self.assertEqual(len(arguments), 3)
        self.assertIn('Predicted outcome supports motion', arguments[0])
        self.assertIn('Risk level: low', arguments[1])
        self.assertIn('Supported by 2 similar cases', arguments[2])

    def test_extract_legal_citations(self):
        """Test legal citations extraction."""
        analysis = ComprehensiveAnalysis(
            case_id='case_001',
            analysis_timestamp=datetime.now(),
            outcome_prediction={},
            risk_assessment={},
            strategy_recommendations=[],
            similar_cases=[
                {'document_id': 'similar_001', 'summary': 'Similar case'},
                {'document_id': 'similar_002', 'summary': 'Another case'}
            ],
            compliance_check={},
            confidence_score=0.8,
            analysis_summary="Test analysis."
        )

        citations = self.engine._extract_legal_citations(analysis)

        # Verify citations
        self.assertEqual(len(citations), 2)
        self.assertIn('Case: similar_001', citations)
        self.assertIn('Case: similar_002', citations)

    def test_calculate_litigation_risk_factors(self):
        """Test litigation risk factors calculation."""
        case_data = {
            'content': 'This is a complex legal case.',
            'type': 'complex_litigation'
        }

        risk_result = {
            'risk_level': 'high',
            'confidence_score': 0.8
        }

        outcome_result = {
            'prediction': 'Unfavorable',
            'confidence_score': 0.7
        }

        factors = self.engine._calculate_litigation_risk_factors(case_data, risk_result, outcome_result)

        # Verify risk factors structure
        self.assertIn('case_complexity', factors)
        self.assertIn('jurisdiction_risk', factors)
        self.assertIn('precedent_risk', factors)
        self.assertIn('financial_risk', factors)
        self.assertIn('timeline_risk', factors)

        # Verify high risk factors are set correctly
        self.assertEqual(factors['case_complexity'], 'high')
        self.assertEqual(factors['precedent_risk'], 'high')

    def test_generate_risk_mitigation_strategies(self):
        """Test risk mitigation strategies generation."""
        risk_factors = {
            'case_complexity': 'high',
            'jurisdiction_risk': 'low',
            'precedent_risk': 'high',
            'financial_risk': 'medium',
            'timeline_risk': 'low'
        }

        strategies = self.engine._generate_risk_mitigation_strategies(risk_factors)

        # Verify strategies generated for high-risk factors
        self.assertEqual(len(strategies), 2)
        self.assertIn('Engage specialized legal counsel', strategies)
        self.assertIn('Conduct thorough precedent research', strategies)

    def test_determine_overall_risk_level(self):
        """Test overall risk level determination."""
        # Test high risk
        high_risk_factors = {
            'case_complexity': 'high',
            'jurisdiction_risk': 'high',
            'precedent_risk': 'medium',
            'financial_risk': 'low',
            'timeline_risk': 'low'
        }

        risk_level = self.engine._determine_overall_risk_level(high_risk_factors)
        self.assertEqual(risk_level, 'high')

        # Test medium risk
        medium_risk_factors = {
            'case_complexity': 'high',
            'jurisdiction_risk': 'medium',
            'precedent_risk': 'medium',
            'financial_risk': 'medium',
            'timeline_risk': 'low'
        }

        risk_level = self.engine._determine_overall_risk_level(medium_risk_factors)
        self.assertEqual(risk_level, 'medium')

        # Test low risk
        low_risk_factors = {
            'case_complexity': 'low',
            'jurisdiction_risk': 'low',
            'precedent_risk': 'low',
            'financial_risk': 'low',
            'timeline_risk': 'low'
        }

        risk_level = self.engine._determine_overall_risk_level(low_risk_factors)
        self.assertEqual(risk_level, 'low')

    def test_rank_strategies(self):
        """Test strategy ranking by effectiveness."""
        strategies = [
            {
                'strategy_type': 'outcome_based',
                'title': 'High Priority Strategy',
                'confidence': 0.9,
                'priority': 'high'
            },
            {
                'strategy_type': 'risk_mitigation',
                'title': 'Medium Priority Strategy',
                'confidence': 0.7,
                'priority': 'medium'
            },
            {
                'strategy_type': 'precedent_based',
                'title': 'Low Priority Strategy',
                'confidence': 0.6,
                'priority': 'low'
            }
        ]

        case_data = {'content': 'Test case'}

        ranked_strategies = self.engine._rank_strategies(strategies, case_data)

        # Verify strategies are ranked by score (confidence * priority_multiplier)
        # High priority (0.9 * 3) = 2.7
        # Medium priority (0.7 * 2) = 1.4
        # Low priority (0.6 * 1) = 0.6
        self.assertEqual(ranked_strategies[0]['title'], 'High Priority Strategy')
        self.assertEqual(ranked_strategies[1]['title'], 'Medium Priority Strategy')
        self.assertEqual(ranked_strategies[2]['title'], 'Low Priority Strategy')

    def test_performance_requirements(self):
        """Test that engine meets performance requirements."""
        # Verify configuration supports performance requirements
        self.assertLessEqual(self.engine.max_similar_cases, 50)  # Reasonable limit
        self.assertGreaterEqual(self.engine.default_confidence_threshold, 0.0)
        self.assertLessEqual(self.engine.default_confidence_threshold, 1.0)

        # Verify analysis cache is available for performance
        self.assertIsInstance(self.engine.analysis_cache, dict)

    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with various error conditions
        case_data = {'content': 'Test case'}

        # Test with None case data
        with self.assertRaises(AttributeError):
            self.engine.analyze_case(None)

        # Test with empty case data
        analysis = self.engine.analyze_case({})
        self.assertIsInstance(analysis, ComprehensiveAnalysis)
        self.assertEqual(analysis.confidence_score, 0.0)

class TestComprehensiveAnalysis(unittest.TestCase):
    """Test ComprehensiveAnalysis data structure."""

    def test_comprehensive_analysis_creation(self):
        """Test ComprehensiveAnalysis creation and properties."""
        timestamp = datetime.now()
        analysis = ComprehensiveAnalysis(
            case_id="case_001",
            analysis_timestamp=timestamp,
            outcome_prediction={'prediction': 'Favorable'},
            risk_assessment={'risk_level': 'low'},
            strategy_recommendations=[
                {'title': 'Strategy 1', 'description': 'First strategy'}
            ],
            similar_cases=[
                {'document_id': 'similar_001', 'summary': 'Similar case'}
            ],
            compliance_check={'compliant': True},
            confidence_score=0.8,
            analysis_summary="Favorable outcome predicted."
        )

        # Verify properties
        self.assertEqual(analysis.case_id, "case_001")
        self.assertEqual(analysis.analysis_timestamp, timestamp)
        self.assertEqual(analysis.outcome_prediction, {'prediction': 'Favorable'})
        self.assertEqual(analysis.risk_assessment, {'risk_level': 'low'})
        self.assertEqual(len(analysis.strategy_recommendations), 1)
        self.assertEqual(len(analysis.similar_cases), 1)
        self.assertEqual(analysis.compliance_check, {'compliant': True})
        self.assertEqual(analysis.confidence_score, 0.8)
        self.assertEqual(analysis.analysis_summary, "Favorable outcome predicted.")

class TestLegalBrief(unittest.TestCase):
    """Test LegalBrief data structure."""

    def test_legal_brief_creation(self):
        """Test LegalBrief creation and properties."""
        timestamp = datetime.now()
        brief = LegalBrief(
            brief_id="brief_001",
            case_id="case_001",
            brief_type="motion",
            content="LEGAL BRIEF - MOTION\nCase ID: case_001\n...",
            key_arguments=["Strong contract terms", "Clear breach evidence"],
            supporting_cases=["similar_001", "similar_002"],
            legal_citations=["Case: similar_001", "Case: similar_002"],
            confidence_score=0.8,
            generated_at=timestamp
        )

        # Verify properties
        self.assertEqual(brief.brief_id, "brief_001")
        self.assertEqual(brief.case_id, "case_001")
        self.assertEqual(brief.brief_type, "motion")
        self.assertIn("LEGAL BRIEF - MOTION", brief.content)
        self.assertEqual(len(brief.key_arguments), 2)
        self.assertEqual(len(brief.supporting_cases), 2)
        self.assertEqual(len(brief.legal_citations), 2)
        self.assertEqual(brief.confidence_score, 0.8)
        self.assertEqual(brief.generated_at, timestamp)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
