#!/usr/bin/env python3
"""
Unit Tests for Error Handler
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
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from core.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity, ProcessingError, RetryConfig

class TestErrorHandler(unittest.TestCase):
    """
    Comprehensive unit tests for ErrorHandler following tester protocol.

    Test Coverage Areas:
    1. Initialization and Configuration
    2. Error Classification and Handling
    3. Retry Logic and Exponential Backoff
    4. Fallback Strategy Execution
    5. Error Logging and Metrics
    """

    def setUp(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()

    def test_initialization_success(self):
        """Test successful handler initialization."""
        # Verify initialization
        self.assertIsInstance(self.handler.error_log, list)
        self.assertIsInstance(self.handler.retry_configs, dict)
        self.assertIsInstance(self.handler.error_patterns, dict)
        self.assertIsInstance(self.handler.fallback_strategies, dict)

        # Verify retry configurations for all categories
        expected_categories = [
            ErrorCategory.INPUT_VALIDATION,
            ErrorCategory.AI_MODEL,
            ErrorCategory.BIGQUERY,
            ErrorCategory.SYSTEM,
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.UNKNOWN
        ]

        for category in expected_categories:
            self.assertIn(category, self.handler.retry_configs)
            config = self.handler.retry_configs[category]
            self.assertIsInstance(config, RetryConfig)
            self.assertGreater(config.max_retries, 0)
            self.assertGreater(config.base_delay, 0)
            self.assertGreater(config.max_delay, 0)
            self.assertGreater(config.exponential_base, 1.0)

    def test_handle_error_success(self):
        """Test successful error handling."""
        error = ValueError("Test validation error")
        context = {"document_id": "doc_001", "stage": "validation"}

        processing_error = self.handler.handle_error(error, context)

        # Verify ProcessingError structure
        self.assertIsInstance(processing_error, ProcessingError)
        self.assertIsNotNone(processing_error.error_id)
        self.assertEqual(processing_error.category, ErrorCategory.INPUT_VALIDATION)
        self.assertEqual(processing_error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(processing_error.message, "Test validation error")
        self.assertEqual(processing_error.exception, error)
        self.assertEqual(processing_error.context, context)
        self.assertFalse(processing_error.retryable)
        self.assertIsNotNone(processing_error.stack_trace)

        # Verify error was logged
        self.assertEqual(len(self.handler.error_log), 1)
        self.assertEqual(self.handler.error_log[0], processing_error)

    def test_handle_error_without_context(self):
        """Test error handling without context."""
        error = Exception("Test error")

        processing_error = self.handler.handle_error(error)

        # Verify ProcessingError structure
        self.assertEqual(processing_error.context, {})
        self.assertIsNotNone(processing_error.error_id)

    def test_classify_error_input_validation(self):
        """Test error classification for input validation errors."""
        test_cases = [
            ValueError("Missing required field: content"),
            ValueError("Invalid format: document"),
            ValueError("Empty content provided"),
            ValueError("Content too short for processing"),
            ValueError("Content too long for processing")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                self.assertEqual(category, ErrorCategory.INPUT_VALIDATION)

    def test_classify_error_ai_model(self):
        """Test error classification for AI model errors."""
        test_cases = [
            Exception("Model not found: legal_extractor"),
            Exception("Model error: generation failed"),
            Exception("Embedding failed for document"),
            Exception("Prediction failed due to model error")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                self.assertEqual(category, ErrorCategory.AI_MODEL)

    def test_classify_error_bigquery(self):
        """Test error classification for BigQuery errors."""
        test_cases = [
            Exception("BigQuery table not found"),
            Exception("Dataset not found: legal_ai_platform"),
            Exception("Query failed: syntax error"),
            Exception("Permission denied for BigQuery access"),
            Exception("Quota exceeded for BigQuery requests")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                self.assertEqual(category, ErrorCategory.BIGQUERY)

    def test_classify_error_system(self):
        """Test error classification for system errors."""
        test_cases = [
            MemoryError("Out of memory"),
            OSError("Disk space insufficient"),
            Exception("Resource allocation failed")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                self.assertEqual(category, ErrorCategory.SYSTEM)

    def test_classify_error_network(self):
        """Test error classification for network errors."""
        test_cases = [
            ConnectionError("Network connection failed"),
            Exception("Connection timeout occurred"),
            Exception("Network error during request")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                self.assertEqual(category, ErrorCategory.NETWORK)

    def test_classify_error_timeout(self):
        """Test error classification for timeout errors."""
        test_cases = [
            TimeoutError("Request timeout"),
            Exception("Operation timeout after 30 seconds")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                self.assertEqual(category, ErrorCategory.TIMEOUT)

    def test_classify_error_unknown(self):
        """Test error classification for unknown errors."""
        error = Exception("Unknown error type")

        category = self.handler._classify_error(error)

        self.assertEqual(category, ErrorCategory.UNKNOWN)

    def test_determine_severity(self):
        """Test error severity determination."""
        test_cases = [
            (ErrorCategory.INPUT_VALIDATION, ErrorSeverity.MEDIUM),
            (ErrorCategory.AI_MODEL, ErrorSeverity.HIGH),
            (ErrorCategory.BIGQUERY, ErrorSeverity.HIGH),
            (ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL),
            (ErrorCategory.NETWORK, ErrorSeverity.MEDIUM),
            (ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM),
            (ErrorCategory.UNKNOWN, ErrorSeverity.LOW)
        ]

        for category, expected_severity in test_cases:
            with self.subTest(category=category):
                error = Exception("Test error")
                severity = self.handler._determine_severity(error, category)
                self.assertEqual(severity, expected_severity)

    def test_is_retryable_true(self):
        """Test retryable error detection for retryable errors."""
        test_cases = [
            Exception("Network connection failed"),
            Exception("Timeout occurred"),
            Exception("Model temporarily unavailable"),
            Exception("BigQuery service temporarily down")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                retryable = self.handler._is_retryable(error, category)
                self.assertTrue(retryable)

    def test_is_retryable_false(self):
        """Test retryable error detection for non-retryable errors."""
        test_cases = [
            Exception("Permission denied for BigQuery access"),
            Exception("Invalid credentials provided"),
            Exception("Quota exceeded for BigQuery requests"),
            Exception("Table not found: legal_documents"),
            Exception("Dataset not found: legal_ai_platform"),
            Exception("Missing required field: content"),
            Exception("Invalid format: document")
        ]

        for error in test_cases:
            with self.subTest(error=str(error)):
                category = self.handler._classify_error(error)
                retryable = self.handler._is_retryable(error, category)
                self.assertFalse(retryable)

    def test_calculate_retry_delay(self):
        """Test retry delay calculation with exponential backoff."""
        error = Exception("Test error")
        processing_error = ProcessingError(
            error_id="test_error",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
            exception=error,
            timestamp=datetime.now(),
            retryable=True,
            context={}
        )

        # Test exponential backoff
        delay1 = self.handler._calculate_retry_delay(processing_error, 1)
        delay2 = self.handler._calculate_retry_delay(processing_error, 2)
        delay3 = self.handler._calculate_retry_delay(processing_error, 3)

        # Verify exponential increase
        self.assertLess(delay1, delay2)
        self.assertLess(delay2, delay3)

        # Verify delays are within configured limits
        config = self.handler.retry_configs[ErrorCategory.NETWORK]
        self.assertLessEqual(delay1, config.max_delay)
        self.assertLessEqual(delay2, config.max_delay)
        self.assertLessEqual(delay3, config.max_delay)

    def test_calculate_retry_delay_with_jitter(self):
        """Test retry delay calculation with jitter."""
        error = Exception("Test error")
        processing_error = ProcessingError(
            error_id="test_error",
            category=ErrorCategory.AI_MODEL,  # Has jitter enabled
            severity=ErrorSeverity.HIGH,
            message="Test error",
            exception=error,
            timestamp=datetime.now(),
            retryable=True,
            context={}
        )

        # Calculate delay multiple times to test jitter
        delays = []
        for _ in range(10):
            delay = self.handler._calculate_retry_delay(processing_error, 1)
            delays.append(delay)

        # Verify jitter is applied (delays should vary)
        unique_delays = set(delays)
        self.assertGreater(len(unique_delays), 1)

    def test_execute_with_retry_success(self):
        """Test successful function execution with retry."""
        def successful_function():
            return "success"

        result, error = self.handler.execute_with_retry(successful_function)

        # Verify success
        self.assertEqual(result, "success")
        self.assertIsNone(error)

    def test_execute_with_retry_retryable_error(self):
        """Test function execution with retryable error."""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network error")
            return "success"

        with patch('time.sleep'):  # Mock sleep to speed up test
            result, error = self.handler.execute_with_retry(failing_function)

        # Verify retry succeeded
        self.assertEqual(result, "success")
        self.assertIsNone(error)
        self.assertEqual(call_count, 3)

    def test_execute_with_retry_non_retryable_error(self):
        """Test function execution with non-retryable error."""
        def failing_function():
            raise ValueError("Missing required field")

        result, error = self.handler.execute_with_retry(failing_function)

        # Verify immediate failure
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.category, ErrorCategory.INPUT_VALIDATION)
        self.assertFalse(error.retryable)

    def test_execute_with_retry_max_retries_exceeded(self):
        """Test function execution when max retries exceeded."""
        def always_failing_function():
            raise ConnectionError("Persistent network error")

        with patch('time.sleep'):  # Mock sleep to speed up test
            result, error = self.handler.execute_with_retry(always_failing_function)

        # Verify failure after max retries
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.category, ErrorCategory.NETWORK)

    def test_execute_with_fallback_success(self):
        """Test function execution with fallback strategy."""
        def primary_function():
            raise ConnectionError("Primary function failed")

        def fallback_function():
            return "fallback_success"

        result, error = self.handler.execute_with_fallback(primary_function, fallback_function)

        # Verify fallback succeeded
        self.assertEqual(result, "fallback_success")
        self.assertIsNone(error)

    def test_execute_with_fallback_both_fail(self):
        """Test function execution when both primary and fallback fail."""
        def primary_function():
            raise ConnectionError("Primary function failed")

        def fallback_function():
            raise Exception("Fallback function failed")

        with patch('time.sleep'):  # Mock sleep to speed up test
            result, error = self.handler.execute_with_fallback(primary_function, fallback_function)

        # Verify both functions failed
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.category, ErrorCategory.NETWORK)

    def test_fallback_simple_extraction(self):
        """Test simple extraction fallback strategy."""
        result = self.handler._fallback_simple_extraction("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["extraction_method"], "fallback_keyword")
        self.assertEqual(result["status"], "success")

    def test_fallback_keyword_analysis(self):
        """Test keyword analysis fallback strategy."""
        result = self.handler._fallback_keyword_analysis("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["analysis_method"], "fallback_keyword")
        self.assertEqual(result["status"], "success")

    def test_fallback_local_storage(self):
        """Test local storage fallback strategy."""
        result = self.handler._fallback_local_storage("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["storage_method"], "fallback_local")
        self.assertEqual(result["status"], "success")

    def test_fallback_retry_later(self):
        """Test retry later fallback strategy."""
        result = self.handler._fallback_retry_later("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["retry_method"], "fallback_later")
        self.assertEqual(result["status"], "deferred")

    def test_fallback_offline_mode(self):
        """Test offline mode fallback strategy."""
        result = self.handler._fallback_offline_mode("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["mode"], "fallback_offline")
        self.assertEqual(result["status"], "success")

    def test_fallback_cached_results(self):
        """Test cached results fallback strategy."""
        result = self.handler._fallback_cached_results("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["source"], "fallback_cache")
        self.assertEqual(result["status"], "success")

    def test_fallback_reduce_complexity(self):
        """Test reduce complexity fallback strategy."""
        result = self.handler._fallback_reduce_complexity("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["complexity"], "fallback_reduced")
        self.assertEqual(result["status"], "success")

    def test_fallback_batch_processing(self):
        """Test batch processing fallback strategy."""
        result = self.handler._fallback_batch_processing("test_arg", keyword="test")

        # Verify fallback result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["processing"], "fallback_batch")
        self.assertEqual(result["status"], "success")

    def test_get_error_summary_empty(self):
        """Test error summary with no errors."""
        summary = self.handler.get_error_summary()

        # Verify empty summary
        self.assertEqual(summary["total_errors"], 0)

    def test_get_error_summary_with_errors(self):
        """Test error summary with multiple errors."""
        # Add various errors
        self.handler.handle_error(ValueError("Validation error"), {"doc": "doc_001"})
        self.handler.handle_error(ConnectionError("Network error"), {"doc": "doc_002"})
        self.handler.handle_error(Exception("BigQuery error"), {"doc": "doc_003"})
        self.handler.handle_error(ValueError("Another validation error"), {"doc": "doc_004"})

        summary = self.handler.get_error_summary()

        # Verify summary structure
        self.assertEqual(summary["total_errors"], 4)
        self.assertIn("category_counts", summary)
        self.assertIn("severity_counts", summary)
        self.assertIn("recent_errors", summary)

        # Verify category counts
        self.assertEqual(summary["category_counts"]["input_validation"], 2)
        self.assertEqual(summary["category_counts"]["network"], 1)
        self.assertEqual(summary["category_counts"]["bigquery"], 1)

        # Verify severity counts
        self.assertEqual(summary["severity_counts"]["medium"], 2)
        self.assertEqual(summary["severity_counts"]["high"], 1)

        # Verify recent errors
        self.assertEqual(len(summary["recent_errors"]), 4)
        for error_info in summary["recent_errors"]:
            self.assertIn("error_id", error_info)
            self.assertIn("category", error_info)
            self.assertIn("severity", error_info)
            self.assertIn("message", error_info)
            self.assertIn("timestamp", error_info)
            self.assertIn("retryable", error_info)

    def test_get_error_summary_recent_errors_limit(self):
        """Test error summary with many errors (recent limit)."""
        # Add many errors
        for i in range(15):
            self.handler.handle_error(Exception(f"Error {i}"), {"doc": f"doc_{i:03d}"})

        summary = self.handler.get_error_summary()

        # Verify total count
        self.assertEqual(summary["total_errors"], 15)

        # Verify recent errors limit (should be 10)
        self.assertEqual(len(summary["recent_errors"]), 10)

        # Verify most recent errors are included
        recent_error_ids = [error["error_id"] for error in summary["recent_errors"]]
        self.assertIn(self.handler.error_log[-1].error_id, recent_error_ids)

    def test_retry_config_validation(self):
        """Test retry configuration validation."""
        for category, config in self.handler.retry_configs.items():
            with self.subTest(category=category):
                # Verify configuration values are reasonable
                self.assertGreater(config.max_retries, 0)
                self.assertLessEqual(config.max_retries, 10)  # Reasonable upper limit
                self.assertGreater(config.base_delay, 0)
                self.assertLessEqual(config.base_delay, 10)  # Reasonable upper limit
                self.assertGreater(config.max_delay, config.base_delay)
                self.assertLessEqual(config.max_delay, 300)  # 5 minutes max
                self.assertGreater(config.exponential_base, 1.0)
                self.assertLessEqual(config.exponential_base, 3.0)  # Reasonable upper limit
                self.assertIsInstance(config.jitter, bool)

    def test_error_patterns_coverage(self):
        """Test error patterns coverage."""
        # Verify all expected patterns are covered
        expected_patterns = [
            "missing required field",
            "invalid format",
            "empty content",
            "content too short",
            "content too long",
            "model not found",
            "model error",
            "generation failed",
            "embedding failed",
            "prediction failed",
            "bigquery",
            "table not found",
            "dataset not found",
            "query failed",
            "permission denied",
            "quota exceeded",
            "memory",
            "disk space",
            "resource",
            "connection",
            "timeout",
            "network"
        ]

        for pattern in expected_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, self.handler.error_patterns)

    def test_fallback_strategies_coverage(self):
        """Test fallback strategies coverage."""
        # Verify all expected categories have fallback strategies
        expected_categories = [
            ErrorCategory.AI_MODEL,
            ErrorCategory.BIGQUERY,
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT
        ]

        for category in expected_categories:
            with self.subTest(category=category):
                self.assertIn(category, self.handler.fallback_strategies)
                strategies = self.handler.fallback_strategies[category]
                self.assertIsInstance(strategies, list)
                self.assertGreater(len(strategies), 0)

    def test_performance_requirements(self):
        """Test that handler meets performance requirements."""
        # Test error handling performance
        start_time = time.time()

        for i in range(100):
            error = Exception(f"Test error {i}")
            self.handler.handle_error(error, {"test": True})

        end_time = time.time()
        processing_time = end_time - start_time

        # Verify performance (should handle 100 errors quickly)
        self.assertLess(processing_time, 1.0)  # Less than 1 second for 100 errors

        # Verify error log size is manageable
        self.assertEqual(len(self.handler.error_log), 100)

    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with various error types
        test_errors = [
            ValueError("Test ValueError"),
            TypeError("Test TypeError"),
            KeyError("Test KeyError"),
            AttributeError("Test AttributeError"),
            RuntimeError("Test RuntimeError"),
            Exception("Test generic Exception"),
            None,  # Test None error
            "String error",  # Test string error
            123,  # Test numeric error
        ]

        for error in test_errors:
            with self.subTest(error=error):
                try:
                    processing_error = self.handler.handle_error(error)
                    self.assertIsInstance(processing_error, ProcessingError)
                    self.assertIsNotNone(processing_error.error_id)
                except Exception as e:
                    # Handler should not crash even with invalid inputs
                    self.fail(f"Error handler crashed with error {error}: {e}")

    def test_concurrent_error_handling(self):
        """Test concurrent error handling."""
        import threading
        import time

        results = []
        errors = []

        def error_worker(worker_id):
            try:
                for i in range(10):
                    error = Exception(f"Worker {worker_id} error {i}")
                    processing_error = self.handler.handle_error(error, {"worker": worker_id})
                    results.append(processing_error.error_id)
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=error_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all workers completed successfully
        self.assertEqual(len(results), 50)  # 5 workers * 10 errors each
        self.assertEqual(len(errors), 0)

        # Verify all errors were logged
        self.assertEqual(len(self.handler.error_log), 50)

class TestProcessingError(unittest.TestCase):
    """Test ProcessingError data structure."""

    def test_processing_error_creation(self):
        """Test ProcessingError creation and properties."""
        error = ValueError("Test error")
        timestamp = datetime.now()
        context = {"document_id": "doc_001", "stage": "validation"}

        processing_error = ProcessingError(
            error_id="error_001",
            category=ErrorCategory.INPUT_VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
            exception=error,
            timestamp=timestamp,
            retryable=False,
            context=context,
            stack_trace="Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\n    raise ValueError(\"Test error\")\nValueError: Test error"
        )

        # Verify properties
        self.assertEqual(processing_error.error_id, "error_001")
        self.assertEqual(processing_error.category, ErrorCategory.INPUT_VALIDATION)
        self.assertEqual(processing_error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(processing_error.message, "Test error")
        self.assertEqual(processing_error.exception, error)
        self.assertEqual(processing_error.timestamp, timestamp)
        self.assertFalse(processing_error.retryable)
        self.assertEqual(processing_error.context, context)
        self.assertIn("ValueError: Test error", processing_error.stack_trace)

    def test_processing_error_minimal(self):
        """Test ProcessingError with minimal required fields."""
        error = Exception("Test error")
        timestamp = datetime.now()

        processing_error = ProcessingError(
            error_id="error_001",
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.LOW,
            message="Test error",
            exception=error,
            timestamp=timestamp,
            retryable=True,
            context={}
        )

        # Verify required properties
        self.assertEqual(processing_error.error_id, "error_001")
        self.assertEqual(processing_error.category, ErrorCategory.UNKNOWN)
        self.assertEqual(processing_error.severity, ErrorSeverity.LOW)
        self.assertEqual(processing_error.message, "Test error")
        self.assertEqual(processing_error.exception, error)
        self.assertEqual(processing_error.timestamp, timestamp)
        self.assertTrue(processing_error.retryable)
        self.assertEqual(processing_error.context, {})
        self.assertIsNone(processing_error.stack_trace)

class TestRetryConfig(unittest.TestCase):
    """Test RetryConfig data structure."""

    def test_retry_config_creation(self):
        """Test RetryConfig creation and properties."""
        config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True
        )

        # Verify properties
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.base_delay, 1.0)
        self.assertEqual(config.max_delay, 30.0)
        self.assertEqual(config.exponential_base, 2.0)
        self.assertTrue(config.jitter)

    def test_retry_config_validation(self):
        """Test RetryConfig validation."""
        # Test valid configuration
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=60.0,
            exponential_base=2.5,
            jitter=False
        )

        # Verify configuration is reasonable
        self.assertGreater(config.max_retries, 0)
        self.assertGreater(config.base_delay, 0)
        self.assertGreater(config.max_delay, config.base_delay)
        self.assertGreater(config.exponential_base, 1.0)
        self.assertIsInstance(config.jitter, bool)

class TestErrorCategory(unittest.TestCase):
    """Test ErrorCategory enumeration."""

    def test_error_category_values(self):
        """Test ErrorCategory enumeration values."""
        self.assertEqual(ErrorCategory.INPUT_VALIDATION.value, "input_validation")
        self.assertEqual(ErrorCategory.AI_MODEL.value, "ai_model")
        self.assertEqual(ErrorCategory.BIGQUERY.value, "bigquery")
        self.assertEqual(ErrorCategory.SYSTEM.value, "system")
        self.assertEqual(ErrorCategory.NETWORK.value, "network")
        self.assertEqual(ErrorCategory.TIMEOUT.value, "timeout")
        self.assertEqual(ErrorCategory.UNKNOWN.value, "unknown")

    def test_error_category_enumeration(self):
        """Test ErrorCategory enumeration membership."""
        self.assertIn(ErrorCategory.INPUT_VALIDATION, ErrorCategory)
        self.assertIn(ErrorCategory.AI_MODEL, ErrorCategory)
        self.assertIn(ErrorCategory.BIGQUERY, ErrorCategory)
        self.assertIn(ErrorCategory.SYSTEM, ErrorCategory)
        self.assertIn(ErrorCategory.NETWORK, ErrorCategory)
        self.assertIn(ErrorCategory.TIMEOUT, ErrorCategory)
        self.assertIn(ErrorCategory.UNKNOWN, ErrorCategory)

class TestErrorSeverity(unittest.TestCase):
    """Test ErrorSeverity enumeration."""

    def test_error_severity_values(self):
        """Test ErrorSeverity enumeration values."""
        self.assertEqual(ErrorSeverity.LOW.value, "low")
        self.assertEqual(ErrorSeverity.MEDIUM.value, "medium")
        self.assertEqual(ErrorSeverity.HIGH.value, "high")
        self.assertEqual(ErrorSeverity.CRITICAL.value, "critical")

    def test_error_severity_enumeration(self):
        """Test ErrorSeverity enumeration membership."""
        self.assertIn(ErrorSeverity.LOW, ErrorSeverity)
        self.assertIn(ErrorSeverity.MEDIUM, ErrorSeverity)
        self.assertIn(ErrorSeverity.HIGH, ErrorSeverity)
        self.assertIn(ErrorSeverity.CRITICAL, ErrorSeverity)

    def test_error_severity_ordering(self):
        """Test ErrorSeverity ordering (if applicable)."""
        # Verify severity levels are distinct
        severities = [ErrorSeverity.LOW, ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        self.assertEqual(len(severities), len(set(severities)))

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
