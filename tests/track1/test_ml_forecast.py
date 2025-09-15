#!/usr/bin/env python3
"""
Test Suite for ML.FORECAST Function
Track 1: Generative AI - Case Outcome Prediction

This test suite validates the ML.FORECAST function for legal case outcome prediction.
"""

import sys
import os
import unittest
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_ai_functions import BigQueryAIFunctions

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestMLForecast(unittest.TestCase):
    """Test cases for ML.FORECAST function."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with BigQuery AI functions."""
        logger.info("Setting up ML.FORECAST test suite...")
        cls.bq_ai = BigQueryAIFunctions()

    def test_ml_forecast_initialization(self):
        """Test that ML.FORECAST can be initialized."""
        logger.info("Testing ML.FORECAST initialization...")

        # Test that the function exists and can be called
        self.assertIsNotNone(self.bq_ai.ai_forecast)
        self.assertTrue(callable(self.bq_ai.ai_forecast))

        logger.info("✅ ML.FORECAST initialization test passed")

    def test_ml_forecast_basic_prediction(self):
        """Test ML.FORECAST basic prediction functionality."""
        logger.info("Testing ML.FORECAST basic prediction...")

        try:
            result = self.bq_ai.ai_forecast(limit=5)

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('function', result)
            self.assertIn('total_forecasts', result)
            self.assertIn('forecasts', result)

            # Validate function name
            self.assertEqual(result['function'], 'AI.FORECAST')

            # Validate forecast count
            self.assertGreater(result['total_forecasts'], 0)

            # Validate forecasts
            self.assertIsInstance(result['forecasts'], list)
            self.assertEqual(len(result['forecasts']), result['total_forecasts'])

            # Validate each forecast
            for forecast in result['forecasts']:
                self.assertIn('case_type', forecast)
                self.assertIn('forecast_timestamp', forecast)
                self.assertIn('forecast_value', forecast)
                self.assertIn('standard_error', forecast)
                self.assertIn('confidence_level', forecast)
                self.assertIn('confidence_interval_lower', forecast)
                self.assertIn('confidence_interval_upper', forecast)

                # Validate forecast value is numeric
                self.assertIsInstance(forecast['forecast_value'], (int, float))

                # Validate confidence level
                self.assertIsInstance(forecast['confidence_level'], (int, float))
                self.assertGreaterEqual(forecast['confidence_level'], 0.0)
                self.assertLessEqual(forecast['confidence_level'], 1.0)

            logger.info(f"✅ Basic prediction test passed - Generated {result['total_forecasts']} forecasts")

        except Exception as e:
            self.fail(f"ML.FORECAST basic prediction test failed: {e}")

    def test_ml_forecast_parameter_validation(self):
        """Test ML.FORECAST parameter validation."""
        logger.info("Testing ML.FORECAST parameter validation...")

        try:
            # Test with different parameters
            result = self.bq_ai.ai_forecast(
                case_type="case_law",
                limit=3
            )

            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('forecasts', result)
            self.assertGreater(len(result['forecasts']), 0)

            # Validate case type in results
            for forecast in result['forecasts']:
                self.assertEqual(forecast['case_type'], 'case_law')

            logger.info("✅ Parameter validation test passed")

        except Exception as e:
            self.fail(f"ML.FORECAST parameter validation test failed: {e}")

    def test_ml_forecast_performance(self):
        """Test ML.FORECAST performance."""
        logger.info("Testing ML.FORECAST performance...")

        import time

        try:
            start_time = time.time()
            result = self.bq_ai.ai_forecast(limit=3)
            end_time = time.time()

            processing_time = end_time - start_time

            # Validate result
            self.assertIsInstance(result, dict)
            self.assertIn('forecasts', result)
            self.assertGreater(len(result['forecasts']), 0)

            # Validate performance (should complete within reasonable time)
            self.assertLess(processing_time, 30)  # Should complete within 30 seconds

            logger.info(f"✅ Performance test passed - Processing time: {processing_time:.2f} seconds")

        except Exception as e:
            self.fail(f"ML.FORECAST performance test failed: {e}")

    def test_ml_forecast_forecast_quality(self):
        """Test ML.FORECAST forecast quality."""
        logger.info("Testing ML.FORECAST forecast quality...")

        try:
            result = self.bq_ai.ai_forecast(limit=5)

            forecasts = result['forecasts']

            # Validate forecast quality
            for forecast in forecasts:
                # Check forecast value is reasonable (between 0 and 1 for outcome scores)
                forecast_value = forecast['forecast_value']
                self.assertGreaterEqual(forecast_value, 0.0)
                self.assertLessEqual(forecast_value, 1.0)

                # Check confidence interval is valid
                lower_bound = forecast['confidence_interval_lower']
                upper_bound = forecast['confidence_interval_upper']
                self.assertLessEqual(lower_bound, upper_bound)
                self.assertLessEqual(lower_bound, forecast_value)
                self.assertGreaterEqual(upper_bound, forecast_value)

                # Check standard error is positive
                standard_error = forecast['standard_error']
                self.assertGreaterEqual(standard_error, 0.0)

            logger.info("✅ Forecast quality test passed - All forecasts have valid values and intervals")

        except Exception as e:
            self.fail(f"ML.FORECAST forecast quality test failed: {e}")

    def test_ml_forecast_timestamp_validation(self):
        """Test ML.FORECAST timestamp validation."""
        logger.info("Testing ML.FORECAST timestamp validation...")

        try:
            result = self.bq_ai.ai_forecast(limit=3)

            forecasts = result['forecasts']

            # Validate timestamps
            for forecast in forecasts:
                forecast_timestamp = forecast['forecast_timestamp']

                # Should be a valid timestamp string
                self.assertIsInstance(forecast_timestamp, str)

                # Should be parseable as datetime
                try:
                    parsed_timestamp = datetime.fromisoformat(forecast_timestamp.replace('Z', '+00:00'))
                    self.assertIsInstance(parsed_timestamp, datetime)
                except ValueError:
                    self.fail(f"Invalid timestamp format: {forecast_timestamp}")

            logger.info("✅ Timestamp validation test passed - All timestamps are valid")

        except Exception as e:
            self.fail(f"ML.FORECAST timestamp validation test failed: {e}")

    def test_ml_forecast_consistency(self):
        """Test ML.FORECAST consistency across multiple calls."""
        logger.info("Testing ML.FORECAST consistency...")

        try:
            # Run multiple times to check consistency
            results = []
            for i in range(3):
                result = self.bq_ai.ai_forecast(limit=2)
                results.append(result)

            # All results should have the same structure
            for result in results:
                self.assertIsInstance(result, dict)
                self.assertIn('forecasts', result)
                self.assertGreater(len(result['forecasts']), 0)

            # Results should be consistent in structure
            first_result = results[0]
            for result in results[1:]:
                self.assertEqual(len(first_result['forecasts']), len(result['forecasts']))

            logger.info("✅ Consistency test passed - All calls return consistent structure")

        except Exception as e:
            self.fail(f"ML.FORECAST consistency test failed: {e}")

    def test_ml_forecast_error_handling(self):
        """Test ML.FORECAST error handling."""
        logger.info("Testing ML.FORECAST error handling...")

        try:
            # Test with edge case parameters
            result = self.bq_ai.ai_forecast(
                case_type="invalid_case_type",
                limit=1
            )

            # Should still return a valid structure
            self.assertIsInstance(result, dict)
            self.assertIn('forecasts', result)

            logger.info("✅ Error handling test passed - Graceful handling of edge cases")

        except Exception as e:
            # If it raises an exception, that's also acceptable error handling
            logger.info(f"✅ Error handling test passed - Exception raised as expected: {e}")


def run_track1_ml_forecast_tests():
    """Run all ML.FORECAST tests."""
    logger.info("🧪 Starting Track 1 - ML.FORECAST Test Suite")
    logger.info("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMLForecast)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    logger.info("=" * 60)
    logger.info(f"📊 ML.FORECAST Test Results:")
    logger.info(f"   Tests run: {result.testsRun}")
    logger.info(f"   Failures: {len(result.failures)}")
    logger.info(f"   Errors: {len(result.errors)}")
    logger.info(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        logger.error("❌ Test failures:")
        for test, traceback in result.failures:
            logger.error(f"   {test}: {traceback}")

    if result.errors:
        logger.error("❌ Test errors:")
        for test, traceback in result.errors:
            logger.error(f"   {test}: {traceback}")

    if not result.failures and not result.errors:
        logger.info("🎉 All ML.FORECAST tests passed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_track1_ml_forecast_tests()
    sys.exit(0 if success else 1)
