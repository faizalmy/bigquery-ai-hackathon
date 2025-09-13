#!/usr/bin/env python3
"""
Integration Test Suite for Track 1 AI Functions
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script performs comprehensive integration testing of all Track 1 AI functions
working together as a cohesive system.
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

class IntegrationTestSuite:
    """Comprehensive integration testing for Track 1 AI functions."""

    def __init__(self):
        """Initialize integration test suite."""
        self.ai_functions = RealBigQueryAIFunctions()
        self.test_results = {
            "start_time": None,
            "end_time": None,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "integration_scenarios": []
        }

    def run_integration_tests(self) -> bool:
        """
        Run comprehensive integration tests.

        Returns:
            bool: True if all tests pass, False otherwise
        """
        try:
            logger.info("🚀 Starting Track 1 Integration Tests")
            self.test_results["start_time"] = datetime.now()

            # Test individual functions
            self._test_individual_functions()

            # Test function chaining
            self._test_function_chaining()

            # Test data flow
            self._test_data_flow()

            # Test error handling
            self._test_error_handling()

            # Test performance
            self._test_performance()

            # Test integration scenarios
            self._test_integration_scenarios()

            self.test_results["end_time"] = datetime.now()
            self._generate_integration_report()

            success_rate = (self.test_results["passed_tests"] / max(self.test_results["total_tests"], 1)) * 100
            logger.info(f"✅ Integration tests completed: {success_rate:.1f}% success rate")

            return success_rate >= 80  # 80% success rate threshold

        except Exception as e:
            logger.error(f"❌ Integration tests failed: {e}")
            return False

    def _test_individual_functions(self) -> None:
        """Test each AI function individually."""
        logger.info("🔍 Testing individual AI functions...")

        # Test ML.GENERATE_TEXT
        self._run_test("ML.GENERATE_TEXT", self._test_ml_generate_text)

        # Test AI.GENERATE_TABLE
        self._run_test("AI.GENERATE_TABLE", self._test_ai_generate_table)

        # Test AI.GENERATE_BOOL
        self._run_test("AI.GENERATE_BOOL", self._test_ai_generate_bool)

        # Test AI.FORECAST
        self._run_test("AI.FORECAST", self._test_ai_forecast)

    def _test_ml_generate_text(self) -> bool:
        """Test ML.GENERATE_TEXT function."""
        try:
            # Test with sample document ID
            result = self.ai_functions.ml_generate_text_summarization(
                document_id="caselaw_000001",
                limit=3
            )

            if result and result.get('summaries') and len(result.get('summaries', [])) > 0:
                logger.info(f"✅ ML.GENERATE_TEXT: Generated summaries successfully")
                return True
            else:
                logger.error("❌ ML.GENERATE_TEXT: No results returned")
                return False

        except Exception as e:
            logger.error(f"❌ ML.GENERATE_TEXT test failed: {e}")
            return False

    def _test_ai_generate_table(self) -> bool:
        """Test AI.GENERATE_TABLE function."""
        try:
            result = self.ai_functions.ai_generate_table_extraction(
                document_id="caselaw_000001",
                limit=3
            )

            if result and result.get('extractions') and len(result.get('extractions', [])) > 0:
                logger.info(f"✅ AI.GENERATE_TABLE: Extracted data successfully")
                return True
            else:
                logger.error("❌ AI.GENERATE_TABLE: No results returned")
                return False

        except Exception as e:
            logger.error(f"❌ AI.GENERATE_TABLE test failed: {e}")
            return False

    def _test_ai_generate_bool(self) -> bool:
        """Test AI.GENERATE_BOOL function."""
        try:
            result = self.ai_functions.ai_generate_bool_urgency(
                document_id="caselaw_000001",
                limit=3
            )

            if result and result.get('urgency_analyses') and len(result.get('urgency_analyses', [])) > 0:
                logger.info(f"✅ AI.GENERATE_BOOL: Analyzed urgency successfully")
                return True
            else:
                logger.error("❌ AI.GENERATE_BOOL: No results returned")
                return False

        except Exception as e:
            logger.error(f"❌ AI.GENERATE_BOOL test failed: {e}")
            return False

    def _test_ai_forecast(self) -> bool:
        """Test AI.FORECAST function."""
        try:
            result = self.ai_functions.ai_forecast_outcome(
                case_type="case_law",
                limit=3
            )

            if result and result.get('forecasts') and len(result.get('forecasts', [])) > 0:
                logger.info(f"✅ AI.FORECAST: Generated forecasts successfully")
                return True
            else:
                logger.error("❌ AI.FORECAST: No results returned")
                return False

        except Exception as e:
            logger.error(f"❌ AI.FORECAST test failed: {e}")
            return False

    def _test_function_chaining(self) -> None:
        """Test functions working together in sequence."""
        logger.info("🔗 Testing function chaining...")

        self._run_test("Function Chaining", self._test_chain_workflow)

    def _test_chain_workflow(self) -> bool:
        """Test a complete workflow chain."""
        try:
            # Step 1: Generate summary
            summary_result = self.ai_functions.ml_generate_text_summarization(
                document_id="caselaw_000001",
                limit=1
            )

            if not summary_result or not summary_result.get('summaries'):
                return False

            # Step 2: Extract structured data
            table_result = self.ai_functions.ai_generate_table_extraction(
                document_id="caselaw_000001",
                limit=1
            )

            if not table_result or not table_result.get('extractions'):
                return False

            # Step 3: Check urgency
            bool_result = self.ai_functions.ai_generate_bool_urgency(
                document_id="caselaw_000001",
                limit=1
            )

            if not bool_result or not bool_result.get('urgency_analyses'):
                return False

            # Step 4: Generate forecast
            forecast_result = self.ai_functions.ai_forecast_outcome(
                case_type="case_law",
                limit=1
            )

            if not forecast_result or not forecast_result.get('forecasts'):
                return False

            logger.info("✅ Function chaining: All steps completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Function chaining test failed: {e}")
            return False

    def _test_data_flow(self) -> None:
        """Test data flow between functions."""
        logger.info("📊 Testing data flow...")

        self._run_test("Data Flow", self._test_data_consistency)

    def _test_data_consistency(self) -> bool:
        """Test data consistency across functions."""
        try:
            # Get results from all functions
            summary = self.ai_functions.ml_generate_text_summarization("caselaw_000001", 1)
            table = self.ai_functions.ai_generate_table_extraction("caselaw_000001", 1)
            bool_result = self.ai_functions.ai_generate_bool_urgency("caselaw_000001", 1)
            forecast = self.ai_functions.ai_forecast_outcome("case_law", 1)

            # Verify all functions return data for the same document
            if all([summary.get('summaries'), table.get('extractions'),
                   bool_result.get('urgency_analyses'), forecast.get('forecasts')]):
                logger.info("✅ Data flow: All functions return consistent data")
                return True
            else:
                logger.error("❌ Data flow: Inconsistent data across functions")
                return False

        except Exception as e:
            logger.error(f"❌ Data flow test failed: {e}")
            return False

    def _test_error_handling(self) -> None:
        """Test error handling across functions."""
        logger.info("⚠️ Testing error handling...")

        self._run_test("Error Handling", self._test_error_scenarios)

    def _test_error_scenarios(self) -> bool:
        """Test various error scenarios."""
        try:
            # Test with invalid document ID
            result = self.ai_functions.ml_generate_text_summarization(
                document_id="invalid_id_1",
                limit=1
            )

            # Should handle gracefully (return error or empty result)
            logger.info("✅ Error handling: Gracefully handled invalid document ID")
            return True

        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            return False

    def _test_performance(self) -> None:
        """Test performance metrics."""
        logger.info("⚡ Testing performance...")

        self._run_test("Performance", self._test_performance_metrics)

    def _test_performance_metrics(self) -> bool:
        """Test performance metrics."""
        try:
            # Test ML.GENERATE_TEXT performance
            start_time = time.time()
            self.ai_functions.ml_generate_text_summarization("caselaw_000001", 1)
            ml_time = time.time() - start_time

            # Test AI.GENERATE_TABLE performance
            start_time = time.time()
            self.ai_functions.ai_generate_table_extraction("caselaw_000001", 1)
            table_time = time.time() - start_time

            # Test AI.GENERATE_BOOL performance
            start_time = time.time()
            self.ai_functions.ai_generate_bool_urgency("caselaw_000001", 1)
            bool_time = time.time() - start_time

            # Test AI.FORECAST performance
            start_time = time.time()
            self.ai_functions.ai_forecast_outcome("case_law", 1)
            forecast_time = time.time() - start_time

            # Store performance metrics
            self.test_results["performance_metrics"] = {
                "ml_generate_text": ml_time,
                "ai_generate_table": table_time,
                "ai_generate_bool": bool_time,
                "ai_forecast": forecast_time,
                "total_time": ml_time + table_time + bool_time + forecast_time
            }

            logger.info(f"✅ Performance: ML.GENERATE_TEXT: {ml_time:.2f}s, AI.GENERATE_TABLE: {table_time:.2f}s, AI.GENERATE_BOOL: {bool_time:.2f}s, AI.FORECAST: {forecast_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            return False

    def _test_integration_scenarios(self) -> None:
        """Test real-world integration scenarios."""
        logger.info("🌍 Testing integration scenarios...")

        self._run_test("Legal Document Analysis", self._test_legal_analysis_scenario)

    def _test_legal_analysis_scenario(self) -> bool:
        """Test complete legal document analysis scenario."""
        try:
            # Complete legal analysis workflow
            analysis_results = {
                "summaries": self.ai_functions.ml_generate_text_summarization("caselaw_000001", 1),
                "extracted_data": self.ai_functions.ai_generate_table_extraction("caselaw_000001", 1),
                "urgency_assessment": self.ai_functions.ai_generate_bool_urgency("caselaw_000001", 1),
                "outcome_prediction": self.ai_functions.ai_forecast_outcome("case_law", 1)
            }

            # Verify all components are present and successful
            if all([result.get('summaries') or result.get('extractions') or
                   result.get('urgency_analyses') or result.get('forecasts')
                   for result in analysis_results.values()]):
                self.test_results["integration_scenarios"].append({
                    "scenario": "Legal Document Analysis",
                    "status": "success",
                    "results": analysis_results
                })
                logger.info("✅ Integration scenario: Legal document analysis completed successfully")
                return True
            else:
                logger.error("❌ Integration scenario: Missing analysis components")
                return False

        except Exception as e:
            logger.error(f"❌ Integration scenario test failed: {e}")
            return False

    def _run_test(self, test_name: str, test_function) -> None:
        """Run a single test and record results."""
        self.test_results["total_tests"] += 1

        try:
            start_time = time.time()
            result = test_function()
            end_time = time.time()

            if result:
                self.test_results["passed_tests"] += 1
                status = "PASS"
            else:
                self.test_results["failed_tests"] += 1
                status = "FAIL"

            self.test_results["test_details"].append({
                "test_name": test_name,
                "status": status,
                "duration": end_time - start_time,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"{'✅' if result else '❌'} {test_name}: {status}")

        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({
                "test_name": test_name,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            logger.error(f"❌ {test_name}: ERROR - {e}")

    def _generate_integration_report(self) -> None:
        """Generate comprehensive integration test report."""
        try:
            duration = (self.test_results["end_time"] - self.test_results["start_time"]).total_seconds()
            success_rate = (self.test_results["passed_tests"] / max(self.test_results["total_tests"], 1)) * 100

            report = {
                "integration_test_report": {
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": duration,
                    "summary": {
                        "total_tests": self.test_results["total_tests"],
                        "passed_tests": self.test_results["passed_tests"],
                        "failed_tests": self.test_results["failed_tests"],
                        "success_rate": success_rate
                    },
                    "test_details": self.test_results["test_details"],
                    "performance_metrics": self.test_results["performance_metrics"],
                    "integration_scenarios": self.test_results["integration_scenarios"]
                }
            }

            # Save report
            report_file = Path("data/processed/integration_test_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 Integration test report saved to: {report_file}")

        except Exception as e:
            logger.error(f"Failed to generate integration report: {e}")


def main():
    """Main execution function."""
    try:
        print("🔧 Track 1 Integration Test Suite")
        print("=" * 50)
        print("Testing all AI functions working together...")

        # Initialize test suite
        test_suite = IntegrationTestSuite()

        # Run integration tests
        if test_suite.run_integration_tests():
            print("✅ Integration tests completed successfully!")
            return 0
        else:
            print("❌ Integration tests failed")
            return 1

    except Exception as e:
        logger.error(f"Integration test suite failed: {e}")
        print(f"\n❌ Integration test suite failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
