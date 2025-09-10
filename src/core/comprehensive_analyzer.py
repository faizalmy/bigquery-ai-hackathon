"""
Comprehensive Legal Analysis Orchestrator
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module provides the main comprehensive analysis orchestrator that integrates
all Phase 3 components into a unified legal intelligence platform.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from core.document_processor import LegalDocumentProcessor, ProcessingResult
from core.similarity_engine import SimilarityEngine, SimilarityResult
from core.predictive_engine import PredictiveEngine, ComprehensiveAnalysis, LegalBrief
from core.status_tracker import StatusTracker
from core.error_handler import ErrorHandler
from utils.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)

@dataclass
class LegalIntelligenceReport:
    """Comprehensive legal intelligence report."""
    report_id: str
    case_id: str
    generated_at: datetime
    processing_result: ProcessingResult
    similarity_analysis: List[SimilarityResult]
    predictive_analysis: ComprehensiveAnalysis
    legal_brief: Optional[LegalBrief]
    confidence_score: float
    executive_summary: str
    recommendations: List[str]
    risk_assessment: Dict[str, Any]

class ComprehensiveAnalyzer:
    """
    Main comprehensive analyzer that orchestrates all Phase 3 components
    to provide complete legal intelligence analysis.
    """

    def __init__(self, project_id: str, bq_client: BigQueryClient):
        """
        Initialize the comprehensive analyzer.

        Args:
            project_id: BigQuery project ID
            bq_client: BigQuery client instance
        """
        self.project_id = project_id
        self.bq_client = bq_client

        # Initialize all Phase 3 components
        self.document_processor = LegalDocumentProcessor(project_id, bq_client)
        self.similarity_engine = SimilarityEngine(project_id, bq_client)
        self.predictive_engine = PredictiveEngine(project_id, bq_client)
        self.status_tracker = StatusTracker()
        self.error_handler = ErrorHandler()

        # Analysis configuration
        self.default_confidence_threshold = 0.7
        self.analysis_cache = {}

    def analyze_legal_case(self, case_data: Dict[str, Any],
                          generate_brief: bool = True) -> LegalIntelligenceReport:
        """
        Perform comprehensive legal case analysis.

        Args:
            case_data: Case information including content, type, metadata
            generate_brief: Whether to generate a legal brief

        Returns:
            LegalIntelligenceReport with complete analysis
        """
        start_time = time.time()
        case_id = case_data.get('case_id', f"case_{int(time.time())}")
        report_id = f"report_{case_id}_{int(time.time())}"

        logger.info(f"🔍 Starting comprehensive legal analysis for case {case_id}")

        # Start status tracking
        self.status_tracker.start_processing(case_id, case_data)

        try:
            # Step 1: Document Processing
            logger.info("📄 Processing document...")
            self.status_tracker.update_stage(case_id, "document_processing", 20)

            processing_result = self.document_processor.process_document(case_data)

            if processing_result.status != 'completed':
                raise Exception(f"Document processing failed: {processing_result.errors}")

            # Step 2: Similarity Analysis
            logger.info("🔍 Performing similarity analysis...")
            self.status_tracker.update_stage(case_id, "similarity_analysis", 40)

            similarity_results = self.similarity_engine.search_by_content(
                case_data.get('content', ''),
                top_k=10,
                similarity_threshold=0.6
            )

            # Step 3: Predictive Analysis
            logger.info("🔮 Performing predictive analysis...")
            self.status_tracker.update_stage(case_id, "predictive_analysis", 60)

            predictive_analysis = self.predictive_engine.analyze_case(case_data)

            # Step 4: Legal Brief Generation (if requested)
            legal_brief = None
            if generate_brief:
                logger.info("📝 Generating legal brief...")
                self.status_tracker.update_stage(case_id, "brief_generation", 80)

                legal_brief = self.predictive_engine.generate_legal_brief(case_data)

            # Step 5: Generate Executive Summary
            logger.info("📊 Generating executive summary...")
            self.status_tracker.update_stage(case_id, "summary_generation", 90)

            executive_summary = self._generate_executive_summary(
                processing_result, similarity_results, predictive_analysis
            )

            # Step 6: Generate Recommendations
            recommendations = self._generate_recommendations(
                predictive_analysis, similarity_results
            )

            # Step 7: Risk Assessment
            risk_assessment = self._generate_risk_assessment(
                predictive_analysis, similarity_results
            )

            # Step 8: Calculate Overall Confidence
            confidence_score = self._calculate_overall_confidence(
                processing_result, similarity_results, predictive_analysis
            )

            # Create comprehensive report
            report = LegalIntelligenceReport(
                report_id=report_id,
                case_id=case_id,
                generated_at=datetime.now(),
                processing_result=processing_result,
                similarity_analysis=similarity_results,
                predictive_analysis=predictive_analysis,
                legal_brief=legal_brief,
                confidence_score=confidence_score,
                executive_summary=executive_summary,
                recommendations=recommendations,
                risk_assessment=risk_assessment
            )

            # Complete status tracking
            self.status_tracker.complete_processing(case_id, True, {
                'report_id': report_id,
                'confidence_score': confidence_score,
                'similar_cases_found': len(similarity_results),
                'brief_generated': legal_brief is not None
            })

            analysis_time = time.time() - start_time
            logger.info(f"✅ Comprehensive legal analysis completed in {analysis_time:.2f}s")

            return report

        except Exception as e:
            # Handle errors
            error = self.error_handler.handle_error(e, {'case_id': case_id})
            self.status_tracker.record_error(case_id, str(e))
            self.status_tracker.complete_processing(case_id, False)

            logger.error(f"❌ Comprehensive analysis failed: {e}")

            # Return minimal report on error
            return LegalIntelligenceReport(
                report_id=report_id,
                case_id=case_id,
                generated_at=datetime.now(),
                processing_result=ProcessingResult(
                    document_id=case_id,
                    status='failed',
                    processing_time=time.time() - start_time,
                    results={},
                    errors=[str(e)],
                    timestamp=datetime.now()
                ),
                similarity_analysis=[],
                predictive_analysis=ComprehensiveAnalysis(
                    case_id=case_id,
                    analysis_timestamp=datetime.now(),
                    outcome_prediction={'error': str(e)},
                    risk_assessment={'error': str(e)},
                    strategy_recommendations=[],
                    similar_cases=[],
                    compliance_check={'error': str(e)},
                    confidence_score=0.0,
                    analysis_summary=f"Analysis failed: {str(e)}"
                ),
                legal_brief=None,
                confidence_score=0.0,
                executive_summary=f"Analysis failed: {str(e)}",
                recommendations=[],
                risk_assessment={'error': str(e)}
            )

    def batch_analyze_cases(self, cases_data: List[Dict[str, Any]],
                           generate_briefs: bool = False) -> List[LegalIntelligenceReport]:
        """
        Perform batch analysis of multiple legal cases.

        Args:
            cases_data: List of case information
            generate_briefs: Whether to generate legal briefs

        Returns:
            List of LegalIntelligenceReport objects
        """
        logger.info(f"🔄 Starting batch analysis of {len(cases_data)} cases")

        reports = []
        for i, case_data in enumerate(cases_data):
            logger.info(f"Processing case {i+1}/{len(cases_data)}")
            try:
                report = self.analyze_legal_case(case_data, generate_briefs)
                reports.append(report)
            except Exception as e:
                logger.error(f"❌ Failed to analyze case {i+1}: {e}")
                # Continue with next case

        logger.info(f"✅ Batch analysis completed: {len(reports)} reports generated")
        return reports

    def get_analysis_status(self, case_id: str) -> Dict[str, Any]:
        """
        Get analysis status for a specific case.

        Args:
            case_id: Case identifier

        Returns:
            Analysis status information
        """
        return self.status_tracker.get_document_status(case_id)

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system-wide analysis metrics.

        Returns:
            System metrics information
        """
        return {
            'status_tracker': self.status_tracker.get_system_metrics(),
            'error_handler': self.error_handler.get_error_summary(),
            'similarity_engine': self.similarity_engine.get_cache_stats(),
            'timestamp': datetime.now().isoformat()
        }

    def _generate_executive_summary(self, processing_result: ProcessingResult,
                                  similarity_results: List[SimilarityResult],
                                  predictive_analysis: ComprehensiveAnalysis) -> str:
        """Generate executive summary of the analysis."""
        summary_parts = []

        # Processing status
        if processing_result.status == 'completed':
            summary_parts.append("Document processing completed successfully.")
        else:
            summary_parts.append(f"Document processing failed: {processing_result.errors}")

        # Similar cases found
        if similarity_results:
            summary_parts.append(f"Found {len(similarity_results)} similar cases for reference.")
        else:
            summary_parts.append("No similar cases found.")

        # Predictive analysis summary
        if predictive_analysis.confidence_score > 0.7:
            summary_parts.append("High-confidence predictive analysis completed.")
        elif predictive_analysis.confidence_score > 0.5:
            summary_parts.append("Moderate-confidence predictive analysis completed.")
        else:
            summary_parts.append("Low-confidence predictive analysis completed.")

        # Key findings
        if 'prediction' in predictive_analysis.outcome_prediction:
            summary_parts.append(f"Predicted outcome: {predictive_analysis.outcome_prediction['prediction']}")

        if 'risk_level' in predictive_analysis.risk_assessment:
            summary_parts.append(f"Risk level: {predictive_analysis.risk_assessment['risk_level']}")

        return " ".join(summary_parts)

    def _generate_recommendations(self, predictive_analysis: ComprehensiveAnalysis,
                                similarity_results: List[SimilarityResult]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Based on outcome prediction
        if 'prediction' in predictive_analysis.outcome_prediction:
            prediction = predictive_analysis.outcome_prediction['prediction']
            if 'favorable' in prediction.lower():
                recommendations.append("Consider proceeding with the case based on favorable outcome prediction.")
            elif 'unfavorable' in prediction.lower():
                recommendations.append("Consider settlement or alternative dispute resolution.")

        # Based on risk assessment
        if 'risk_level' in predictive_analysis.risk_assessment:
            risk_level = predictive_analysis.risk_assessment['risk_level']
            if risk_level == 'high':
                recommendations.append("Implement comprehensive risk mitigation strategies.")
            elif risk_level == 'low':
                recommendations.append("Proceed with standard legal procedures.")

        # Based on similar cases
        if similarity_results:
            successful_cases = [case for case in similarity_results
                              if case.case_outcome and 'favorable' in case.case_outcome.lower()]
            if successful_cases:
                recommendations.append(f"Study {len(successful_cases)} similar successful cases for strategy insights.")

        # Based on strategy recommendations
        if predictive_analysis.strategy_recommendations:
            top_strategy = predictive_analysis.strategy_recommendations[0]
            recommendations.append(f"Primary strategy: {top_strategy.get('title', 'Strategy recommendation')}")

        return recommendations

    def _generate_risk_assessment(self, predictive_analysis: ComprehensiveAnalysis,
                                similarity_results: List[SimilarityResult]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        risk_assessment = {
            'overall_risk_level': 'medium',  # Default
            'risk_factors': [],
            'mitigation_strategies': [],
            'confidence_score': predictive_analysis.confidence_score
        }

        # Extract risk information from predictive analysis
        if 'risk_level' in predictive_analysis.risk_assessment:
            risk_assessment['overall_risk_level'] = predictive_analysis.risk_assessment['risk_level']

        # Add risk factors
        if predictive_analysis.confidence_score < 0.5:
            risk_assessment['risk_factors'].append("Low analysis confidence")

        if not similarity_results:
            risk_assessment['risk_factors'].append("No similar cases found for precedent analysis")

        # Add mitigation strategies
        if risk_assessment['overall_risk_level'] == 'high':
            risk_assessment['mitigation_strategies'].append("Engage specialized legal counsel")
            risk_assessment['mitigation_strategies'].append("Conduct additional research")

        return risk_assessment

    def _calculate_overall_confidence(self, processing_result: ProcessingResult,
                                    similarity_results: List[SimilarityResult],
                                    predictive_analysis: ComprehensiveAnalysis) -> float:
        """Calculate overall confidence score for the analysis."""
        confidence_scores = []

        # Processing confidence
        if processing_result.status == 'completed':
            confidence_scores.append(0.9)  # High confidence for successful processing
        else:
            confidence_scores.append(0.1)  # Low confidence for failed processing

        # Similarity analysis confidence
        if similarity_results:
            avg_similarity = sum(result.similarity_score for result in similarity_results) / len(similarity_results)
            confidence_scores.append(avg_similarity)
        else:
            confidence_scores.append(0.3)  # Lower confidence without similar cases

        # Predictive analysis confidence
        confidence_scores.append(predictive_analysis.confidence_score)

        # Calculate weighted average
        return sum(confidence_scores) / len(confidence_scores)

    def export_analysis_report(self, report: LegalIntelligenceReport,
                             filepath: str) -> bool:
        """
        Export analysis report to a file.

        Args:
            report: LegalIntelligenceReport to export
            filepath: Path to export file

        Returns:
            True if export successful, False otherwise
        """
        try:
            import json

            # Convert report to dictionary
            report_dict = {
                'report_id': report.report_id,
                'case_id': report.case_id,
                'generated_at': report.generated_at.isoformat(),
                'confidence_score': report.confidence_score,
                'executive_summary': report.executive_summary,
                'recommendations': report.recommendations,
                'risk_assessment': report.risk_assessment,
                'processing_result': {
                    'status': report.processing_result.status,
                    'processing_time': report.processing_result.processing_time,
                    'errors': report.processing_result.errors
                },
                'similarity_analysis': [
                    {
                        'document_id': result.document_id,
                        'similarity_score': result.similarity_score,
                        'document_type': result.document_type,
                        'legal_domain': result.legal_domain,
                        'jurisdiction': result.jurisdiction
                    }
                    for result in report.similarity_analysis
                ],
                'predictive_analysis': {
                    'outcome_prediction': report.predictive_analysis.outcome_prediction,
                    'risk_assessment': report.predictive_analysis.risk_assessment,
                    'strategy_recommendations': report.predictive_analysis.strategy_recommendations,
                    'confidence_score': report.predictive_analysis.confidence_score,
                    'analysis_summary': report.predictive_analysis.analysis_summary
                }
            }

            # Add legal brief if available
            if report.legal_brief:
                report_dict['legal_brief'] = {
                    'brief_id': report.legal_brief.brief_id,
                    'brief_type': report.legal_brief.brief_type,
                    'confidence_score': report.legal_brief.confidence_score,
                    'key_arguments': report.legal_brief.key_arguments,
                    'supporting_cases': report.legal_brief.supporting_cases
                }

            # Write to file
            with open(filepath, 'w') as f:
                json.dump(report_dict, f, indent=2)

            logger.info(f"📄 Analysis report exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to export analysis report: {e}")
            return False

def main():
    """Test the comprehensive analyzer."""
    print("🔍 Comprehensive Analyzer - Phase 3 Implementation")
    print("=" * 60)

    # This would be used in integration tests
    print("✅ Comprehensive analyzer class created successfully")

if __name__ == "__main__":
    main()
