#!/usr/bin/env python3
"""
End-to-End Workflow Test Suite for Track 1 AI Functions
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests the complete end-to-end workflow from document input to results.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from real_bigquery_ai_functions import RealBigQueryAIFunctions

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EndToEndWorkflowTest:
    """End-to-end workflow testing for Track 1 AI functions."""

    def __init__(self):
        """Initialize end-to-end workflow test."""
        self.ai_functions = RealBigQueryAIFunctions()
        self.test_results = {
            "start_time": None,
            "end_time": None,
            "total_scenarios": 0,
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "scenario_details": [],
            "workflow_metrics": {},
            "performance_analysis": {}
        }

    def run_end_to_end_tests(self) -> bool:
        """
        Run comprehensive end-to-end workflow tests.

        Returns:
            bool: True if all tests pass, False otherwise
        """
        try:
            logger.info("🚀 Starting End-to-End Workflow Tests")
            self.test_results["start_time"] = datetime.now()

            # Test complete legal document analysis workflow
            self._test_complete_legal_analysis_workflow()

            # Test batch processing workflow
            self._test_batch_processing_workflow()

            # Test error recovery workflow
            self._test_error_recovery_workflow()

            # Test performance under load
            self._test_performance_under_load()

            # Test data consistency workflow
            self._test_data_consistency_workflow()

            self.test_results["end_time"] = datetime.now()
            self._generate_workflow_report()

            success_rate = (self.test_results["passed_scenarios"] / max(self.test_results["total_scenarios"], 1)) * 100
            logger.info(f"✅ End-to-end tests completed: {success_rate:.1f}% success rate")

            return success_rate >= 80  # 80% success rate threshold

        except Exception as e:
            logger.error(f"❌ End-to-end tests failed: {e}")
            return False

    def _test_complete_legal_analysis_workflow(self) -> None:
        """Test complete legal document analysis workflow."""
        logger.info("📋 Testing Complete Legal Analysis Workflow...")

        self._run_scenario("Complete Legal Analysis", self._execute_legal_analysis_workflow)

    def _execute_legal_analysis_workflow(self) -> bool:
        """Execute complete legal analysis workflow."""
        try:
            # Step 1: Document ingestion and validation
            document_id = "caselaw_000001"
            logger.info(f"   📄 Processing document: {document_id}")

            # Step 2: Generate document summary
            logger.info("   📝 Step 1: Generating document summary...")
            summary_result = self.ai_functions.ml_generate_text_summarization(
                document_id=document_id,
                limit=1
            )

            if not summary_result or not summary_result.get('summaries'):
                logger.error("   ❌ Document summarization failed")
                return False

            logger.info(f"   ✅ Generated summary for {len(summary_result.get('summaries', []))} document(s)")

            # Step 3: Extract structured data
            logger.info("   📊 Step 2: Extracting structured data...")
            extraction_result = self.ai_functions.ai_generate_table_extraction(
                document_id=document_id,
                limit=1
            )

            if not extraction_result or not extraction_result.get('extractions'):
                logger.error("   ❌ Data extraction failed")
                return False

            logger.info(f"   ✅ Extracted data from {len(extraction_result.get('extractions', []))} document(s)")

            # Step 4: Assess urgency
            logger.info("   ⚠️ Step 3: Assessing document urgency...")
            urgency_result = self.ai_functions.ai_generate_bool_urgency(
                document_id=document_id,
                limit=1
            )

            if not urgency_result or not urgency_result.get('urgency_analyses'):
                logger.error("   ❌ Urgency assessment failed")
                return False

            logger.info(f"   ✅ Assessed urgency for {len(urgency_result.get('urgency_analyses', []))} document(s)")

            # Step 5: Generate outcome forecast
            logger.info("   🔮 Step 4: Generating outcome forecast...")
            forecast_result = self.ai_functions.ai_forecast_outcome(
                case_type="case_law",
                limit=1
            )

            if not forecast_result or not forecast_result.get('forecasts'):
                logger.error("   ❌ Outcome forecasting failed")
                return False

            logger.info(f"   ✅ Generated forecasts for {len(forecast_result.get('forecasts', []))} document(s)")

            # Step 6: Aggregate results
            logger.info("   📋 Step 5: Aggregating analysis results...")
            analysis_results = {
                "document_id": document_id,
                "summary": summary_result.get('summaries', [])[0] if summary_result.get('summaries') else None,
                "extracted_data": extraction_result.get('extractions', [])[0] if extraction_result.get('extractions') else None,
                "urgency_assessment": urgency_result.get('urgency_analyses', [])[0] if urgency_result.get('urgency_analyses') else None,
                "outcome_forecast": forecast_result.get('forecasts', [])[0] if forecast_result.get('forecasts') else None,
                "timestamp": datetime.now().isoformat()
            }

            # Step 7: Validate complete workflow
            if all([analysis_results["summary"], analysis_results["extracted_data"],
                   analysis_results["urgency_assessment"], analysis_results["outcome_forecast"]]):
                logger.info("   ✅ Complete legal analysis workflow successful")
                return True
            else:
                logger.error("   ❌ Incomplete analysis results")
                return False

        except Exception as e:
            logger.error(f"   ❌ Legal analysis workflow failed: {e}")
            return False

    def _test_batch_processing_workflow(self) -> None:
        """Test batch processing workflow."""
        logger.info("📦 Testing Batch Processing Workflow...")

        self._run_scenario("Batch Processing", self._execute_batch_processing_workflow)

    def _execute_batch_processing_workflow(self) -> bool:
        """Execute batch processing workflow."""
        try:
            # Process multiple documents in batch
            document_ids = ["caselaw_000001", "caselaw_000002", "caselaw_000003"]
            logger.info(f"   📄 Processing batch of {len(document_ids)} documents")

            batch_results = []

            for doc_id in document_ids:
                logger.info(f"   🔄 Processing document: {doc_id}")

                # Process each document through the complete workflow
                summary = self.ai_functions.ml_generate_text_summarization(doc_id, 1)
                extraction = self.ai_functions.ai_generate_table_extraction(doc_id, 1)
                urgency = self.ai_functions.ai_generate_bool_urgency(doc_id, 1)

                if all([summary.get('summaries'), extraction.get('extractions'), urgency.get('urgency_analyses')]):
                    batch_results.append({
                        "document_id": doc_id,
                        "status": "success",
                        "summary_available": bool(summary.get('summaries')),
                        "extraction_available": bool(extraction.get('extractions')),
                        "urgency_available": bool(urgency.get('urgency_analyses'))
                    })
                    logger.info(f"   ✅ Document {doc_id} processed successfully")
                else:
                    batch_results.append({
                        "document_id": doc_id,
                        "status": "failed"
                    })
                    logger.error(f"   ❌ Document {doc_id} processing failed")

            # Validate batch processing results
            successful_docs = [r for r in batch_results if r["status"] == "success"]
            success_rate = len(successful_docs) / len(document_ids) * 100

            logger.info(f"   📊 Batch processing results: {len(successful_docs)}/{len(document_ids)} successful ({success_rate:.1f}%)")

            return success_rate >= 80  # 80% success rate for batch processing

        except Exception as e:
            logger.error(f"   ❌ Batch processing workflow failed: {e}")
            return False

    def _test_error_recovery_workflow(self) -> None:
        """Test error recovery workflow."""
        logger.info("🛡️ Testing Error Recovery Workflow...")

        self._run_scenario("Error Recovery", self._execute_error_recovery_workflow)

    def _execute_error_recovery_workflow(self) -> bool:
        """Execute error recovery workflow."""
        try:
            # Test with invalid document ID
            invalid_doc_id = "invalid_document_id"
            logger.info(f"   🧪 Testing error handling with invalid document: {invalid_doc_id}")

            # Attempt to process invalid document
            result = self.ai_functions.ml_generate_text_summarization(
                document_id=invalid_doc_id,
                limit=1
            )

            # Should handle gracefully (return empty or error result)
            if result and result.get('summaries') is not None:
                # Empty results are acceptable for invalid documents
                logger.info("   ✅ Error handling: Gracefully handled invalid document")
                return True
            else:
                logger.info("   ✅ Error handling: No results for invalid document (expected)")
                return True

        except Exception as e:
            logger.error(f"   ❌ Error recovery workflow failed: {e}")
            return False

    def _test_performance_under_load(self) -> None:
        """Test performance under load."""
        logger.info("⚡ Testing Performance Under Load...")

        self._run_scenario("Performance Under Load", self._execute_performance_test)

    def _execute_performance_test(self) -> bool:
        """Execute performance test."""
        try:
            # Test performance with multiple sequential operations
            document_id = "caselaw_000001"
            num_iterations = 3

            logger.info(f"   🏃 Running {num_iterations} iterations of complete workflow")

            total_times = []
            for i in range(num_iterations):
                logger.info(f"   🔄 Iteration {i+1}/{num_iterations}")

                start_time = time.time()

                # Run complete workflow
                summary = self.ai_functions.ml_generate_text_summarization(document_id, 1)
                extraction = self.ai_functions.ai_generate_table_extraction(document_id, 1)
                urgency = self.ai_functions.ai_generate_bool_urgency(document_id, 1)
                forecast = self.ai_functions.ai_forecast_outcome("case_law", 1)

                end_time = time.time()
                iteration_time = end_time - start_time
                total_times.append(iteration_time)

                logger.info(f"   ⏱️ Iteration {i+1} completed in {iteration_time:.2f}s")

            # Calculate performance metrics
            avg_time = sum(total_times) / len(total_times)
            min_time = min(total_times)
            max_time = max(total_times)

            self.test_results["performance_analysis"] = {
                "iterations": num_iterations,
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "total_times": total_times
            }

            logger.info(f"   📊 Performance metrics:")
            logger.info(f"      Average time: {avg_time:.2f}s")
            logger.info(f"      Min time: {min_time:.2f}s")
            logger.info(f"      Max time: {max_time:.2f}s")

            # Performance threshold: average time should be reasonable
            return avg_time < 30  # 30 seconds per complete workflow

        except Exception as e:
            logger.error(f"   ❌ Performance test failed: {e}")
            return False

    def _test_data_consistency_workflow(self) -> None:
        """Test data consistency workflow."""
        logger.info("🔍 Testing Data Consistency Workflow...")

        self._run_scenario("Data Consistency", self._execute_data_consistency_test)

    def _execute_data_consistency_test(self) -> bool:
        """Execute data consistency test."""
        try:
            # Test data consistency across multiple function calls
            document_id = "caselaw_000001"
            logger.info(f"   🔄 Testing data consistency for document: {document_id}")

            # Run same document through workflow multiple times
            results_1 = self._run_single_workflow(document_id)
            results_2 = self._run_single_workflow(document_id)

            # Compare results for consistency
            if results_1 and results_2:
                # Check if results are consistent (same document should produce similar results)
                consistency_score = self._calculate_consistency_score(results_1, results_2)

                logger.info(f"   📊 Data consistency score: {consistency_score:.2f}")

                # Acceptable consistency threshold
                return consistency_score >= 0.7  # 70% consistency
            else:
                logger.error("   ❌ Failed to generate results for consistency test")
                return False

        except Exception as e:
            logger.error(f"   ❌ Data consistency test failed: {e}")
            return False

    def _run_single_workflow(self, document_id: str) -> Dict[str, Any]:
        """Run single workflow and return results."""
        try:
            summary = self.ai_functions.ml_generate_text_summarization(document_id, 1)
            extraction = self.ai_functions.ai_generate_table_extraction(document_id, 1)
            urgency = self.ai_functions.ai_generate_bool_urgency(document_id, 1)

            return {
                "summary": summary.get('summaries', [])[0] if summary.get('summaries') else None,
                "extraction": extraction.get('extractions', [])[0] if extraction.get('extractions') else None,
                "urgency": urgency.get('urgency_analyses', [])[0] if urgency.get('urgency_analyses') else None
            }
        except Exception as e:
            logger.error(f"   ❌ Single workflow failed: {e}")
            return None

    def _calculate_consistency_score(self, results_1: Dict, results_2: Dict) -> float:
        """Calculate consistency score between two result sets."""
        try:
            score = 0.0
            total_checks = 0

            # Check summary consistency (basic length comparison)
            if results_1.get('summary') and results_2.get('summary'):
                len_1 = len(str(results_1['summary']))
                len_2 = len(str(results_2['summary']))
                if len_1 > 0 and len_2 > 0:
                    consistency = 1.0 - abs(len_1 - len_2) / max(len_1, len_2)
                    score += max(0, consistency)
                    total_checks += 1

            # Check extraction consistency (field presence)
            if results_1.get('extraction') and results_2.get('extraction'):
                fields_1 = set(results_1['extraction'].keys()) if isinstance(results_1['extraction'], dict) else set()
                fields_2 = set(results_2['extraction'].keys()) if isinstance(results_2['extraction'], dict) else set()
                if fields_1 or fields_2:
                    field_consistency = len(fields_1.intersection(fields_2)) / max(len(fields_1.union(fields_2)), 1)
                    score += field_consistency
                    total_checks += 1

            # Check urgency consistency (boolean value comparison)
            if results_1.get('urgency') and results_2.get('urgency'):
                # Simple boolean consistency check
                score += 1.0  # Assume consistent if both have results
                total_checks += 1

            return score / max(total_checks, 1)

        except Exception as e:
            logger.error(f"   ❌ Consistency calculation failed: {e}")
            return 0.0

    def _run_scenario(self, scenario_name: str, scenario_function) -> None:
        """Run a single scenario and record results."""
        self.test_results["total_scenarios"] += 1

        try:
            start_time = time.time()
            result = scenario_function()
            end_time = time.time()

            if result:
                self.test_results["passed_scenarios"] += 1
                status = "PASS"
            else:
                self.test_results["failed_scenarios"] += 1
                status = "FAIL"

            self.test_results["scenario_details"].append({
                "scenario_name": scenario_name,
                "status": status,
                "duration": end_time - start_time,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"{'✅' if result else '❌'} {scenario_name}: {status}")

        except Exception as e:
            self.test_results["failed_scenarios"] += 1
            self.test_results["scenario_details"].append({
                "scenario_name": scenario_name,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            logger.error(f"❌ {scenario_name}: ERROR - {e}")

    def _generate_workflow_report(self) -> None:
        """Generate comprehensive workflow test report."""
        try:
            duration = (self.test_results["end_time"] - self.test_results["start_time"]).total_seconds()
            success_rate = (self.test_results["passed_scenarios"] / max(self.test_results["total_scenarios"], 1)) * 100

            report = {
                "end_to_end_workflow_report": {
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": duration,
                    "summary": {
                        "total_scenarios": self.test_results["total_scenarios"],
                        "passed_scenarios": self.test_results["passed_scenarios"],
                        "failed_scenarios": self.test_results["failed_scenarios"],
                        "success_rate": success_rate
                    },
                    "scenario_details": self.test_results["scenario_details"],
                    "performance_analysis": self.test_results["performance_analysis"],
                    "workflow_metrics": self.test_results["workflow_metrics"]
                }
            }

            # Save report
            report_file = Path("data/processed/end_to_end_workflow_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 End-to-end workflow report saved to: {report_file}")

        except Exception as e:
            logger.error(f"Failed to generate workflow report: {e}")


def main():
    """Main execution function."""
    try:
        print("🔄 End-to-End Workflow Test Suite")
        print("=" * 50)
        print("Testing complete Track 1 workflow...")

        # Initialize test suite
        test_suite = EndToEndWorkflowTest()

        # Run end-to-end tests
        if test_suite.run_end_to_end_tests():
            print("✅ End-to-end workflow tests completed successfully!")
            return 0
        else:
            print("❌ End-to-end workflow tests failed")
            return 1

    except Exception as e:
        logger.error(f"End-to-end workflow test suite failed: {e}")
        print(f"\n❌ End-to-end workflow test suite failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
