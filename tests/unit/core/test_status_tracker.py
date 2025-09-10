#!/usr/bin/env python3
"""
Unit Tests for Status Tracker
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

Following World-Class Production Tester Protocol:
- Comprehensive Coverage: Validate every specification, requirement, and edge case
- Risk-Based Prioritization: Focus testing on highest impact and failure probability areas
- Data-Driven Decisions: Base testing priorities on measurable metrics and trends
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
from pathlib import Path
import threading
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from core.status_tracker import StatusTracker, ProcessingStatus, ProcessingMetrics, SystemMetrics

class TestStatusTracker(unittest.TestCase):
    """
    Comprehensive unit tests for StatusTracker following tester protocol.

    Test Coverage Areas:
    1. Initialization and Configuration
    2. Processing Status Management
    3. Metrics Collection and Calculation
    4. Thread Safety and Concurrency
    5. Error Handling and Edge Cases
    """

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = StatusTracker()

    def test_initialization_success(self):
        """Test successful tracker initialization."""
        # Verify initialization
        self.assertIsInstance(self.tracker.processing_metrics, dict)
        self.assertIsInstance(self.tracker.system_metrics, SystemMetrics)
        self.assertIsInstance(self.tracker.status_history, list)
        self.assertIsInstance(self.tracker.lock, threading.Lock)

        # Verify configuration
        self.assertEqual(self.tracker.max_history_size, 1000)
        self.assertEqual(self.tracker.metrics_retention_hours, 24)

        # Verify initial system metrics
        self.assertEqual(self.tracker.system_metrics.total_documents_processed, 0)
        self.assertEqual(self.tracker.system_metrics.successful_documents, 0)
        self.assertEqual(self.tracker.system_metrics.failed_documents, 0)
        self.assertEqual(self.tracker.system_metrics.current_active_documents, 0)
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 0)
        self.assertEqual(self.tracker.system_metrics.error_rate, 0.0)
        self.assertEqual(self.tracker.system_metrics.throughput_per_hour, 0.0)

    def test_start_processing_success(self):
        """Test successful processing start."""
        document_id = "doc_001"
        metadata = {"source": "test", "type": "contract"}

        metrics = self.tracker.start_processing(document_id, metadata)

        # Verify metrics creation
        self.assertIsInstance(metrics, ProcessingMetrics)
        self.assertEqual(metrics.document_id, document_id)
        self.assertEqual(metrics.status, ProcessingStatus.PROCESSING)
        self.assertEqual(metrics.current_stage, "initialization")
        self.assertEqual(metrics.progress_percentage, 0.0)
        self.assertEqual(metrics.error_count, 0)
        self.assertEqual(metrics.retry_count, 0)
        self.assertEqual(metrics.resource_usage, metadata)

        # Verify tracking
        self.assertIn(document_id, self.tracker.processing_metrics)
        self.assertEqual(self.tracker.system_metrics.current_active_documents, 1)
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 1)

    def test_start_processing_without_metadata(self):
        """Test processing start without metadata."""
        document_id = "doc_002"

        metrics = self.tracker.start_processing(document_id)

        # Verify metrics creation
        self.assertEqual(metrics.document_id, document_id)
        self.assertEqual(metrics.resource_usage, {})

    def test_update_stage_success(self):
        """Test successful stage update."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        # Update stage
        result = self.tracker.update_stage(document_id, "ai_processing", 25.0)

        # Verify update
        self.assertTrue(result)
        metrics = self.tracker.processing_metrics[document_id]
        self.assertEqual(metrics.current_stage, "ai_processing")
        self.assertEqual(metrics.progress_percentage, 25.0)

    def test_update_stage_progress_clamping(self):
        """Test stage update with progress percentage clamping."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        # Test negative progress
        self.tracker.update_stage(document_id, "test_stage", -10.0)
        self.assertEqual(self.tracker.processing_metrics[document_id].progress_percentage, 0.0)

        # Test progress over 100%
        self.tracker.update_stage(document_id, "test_stage", 150.0)
        self.assertEqual(self.tracker.processing_metrics[document_id].progress_percentage, 100.0)

    def test_update_stage_document_not_found(self):
        """Test stage update for non-existent document."""
        result = self.tracker.update_stage("non_existent_doc", "test_stage", 50.0)

        # Verify failure
        self.assertFalse(result)

    def test_record_error_success(self):
        """Test successful error recording."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        # Record error
        result = self.tracker.record_error(document_id, "Test error message", "validation_error")

        # Verify recording
        self.assertTrue(result)
        metrics = self.tracker.processing_metrics[document_id]
        self.assertEqual(metrics.error_count, 1)

    def test_record_error_document_not_found(self):
        """Test error recording for non-existent document."""
        result = self.tracker.record_error("non_existent_doc", "Test error", "test_error")

        # Verify failure
        self.assertFalse(result)

    def test_record_retry_success(self):
        """Test successful retry recording."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        # Record retry
        result = self.tracker.record_retry(document_id, "Network timeout")

        # Verify recording
        self.assertTrue(result)
        metrics = self.tracker.processing_metrics[document_id]
        self.assertEqual(metrics.retry_count, 1)
        self.assertEqual(metrics.status, ProcessingStatus.RETRYING)

    def test_record_retry_document_not_found(self):
        """Test retry recording for non-existent document."""
        result = self.tracker.record_retry("non_existent_doc", "Test retry")

        # Verify failure
        self.assertFalse(result)

    def test_complete_processing_success(self):
        """Test successful processing completion."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        final_results = {"processing_time": 5.0, "status": "completed"}

        # Complete processing
        result = self.tracker.complete_processing(document_id, success=True, final_results=final_results)

        # Verify completion
        self.assertTrue(result)
        metrics = self.tracker.processing_metrics[document_id]
        self.assertEqual(metrics.status, ProcessingStatus.COMPLETED)
        self.assertEqual(metrics.progress_percentage, 100.0)
        self.assertIsNotNone(metrics.end_time)
        self.assertIsNotNone(metrics.processing_time)
        self.assertEqual(metrics.resource_usage['final_results'], final_results)

        # Verify system metrics
        self.assertEqual(self.tracker.system_metrics.total_documents_processed, 1)
        self.assertEqual(self.tracker.system_metrics.successful_documents, 1)
        self.assertEqual(self.tracker.system_metrics.failed_documents, 0)
        self.assertEqual(self.tracker.system_metrics.current_active_documents, 0)

    def test_complete_processing_failure(self):
        """Test processing completion with failure."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        # Complete with failure
        result = self.tracker.complete_processing(document_id, success=False)

        # Verify failure completion
        self.assertTrue(result)
        metrics = self.tracker.processing_metrics[document_id]
        self.assertEqual(metrics.status, ProcessingStatus.FAILED)

        # Verify system metrics
        self.assertEqual(self.tracker.system_metrics.total_documents_processed, 1)
        self.assertEqual(self.tracker.system_metrics.successful_documents, 0)
        self.assertEqual(self.tracker.system_metrics.failed_documents, 1)

    def test_complete_processing_document_not_found(self):
        """Test processing completion for non-existent document."""
        result = self.tracker.complete_processing("non_existent_doc", success=True)

        # Verify failure
        self.assertFalse(result)

    def test_cancel_processing_success(self):
        """Test successful processing cancellation."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)

        # Cancel processing
        result = self.tracker.cancel_processing(document_id, "user_requested")

        # Verify cancellation
        self.assertTrue(result)
        metrics = self.tracker.processing_metrics[document_id]
        self.assertEqual(metrics.status, ProcessingStatus.CANCELLED)
        self.assertIsNotNone(metrics.end_time)
        self.assertIsNotNone(metrics.processing_time)

        # Verify system metrics
        self.assertEqual(self.tracker.system_metrics.current_active_documents, 0)

    def test_cancel_processing_document_not_found(self):
        """Test processing cancellation for non-existent document."""
        result = self.tracker.cancel_processing("non_existent_doc", "test_reason")

        # Verify failure
        self.assertFalse(result)

    def test_get_document_status_existing(self):
        """Test getting status for existing document."""
        document_id = "doc_001"
        self.tracker.start_processing(document_id)
        self.tracker.update_stage(document_id, "ai_processing", 50.0)

        status = self.tracker.get_document_status(document_id)

        # Verify status structure
        self.assertIsNotNone(status)
        self.assertEqual(status['document_id'], document_id)
        self.assertEqual(status['status'], 'processing')
        self.assertEqual(status['current_stage'], 'ai_processing')
        self.assertEqual(status['progress_percentage'], 50.0)
        self.assertIn('start_time', status)
        self.assertIsNone(status['end_time'])
        self.assertIsNone(status['processing_time'])
        self.assertEqual(status['error_count'], 0)
        self.assertEqual(status['retry_count'], 0)

    def test_get_document_status_not_found(self):
        """Test getting status for non-existent document."""
        status = self.tracker.get_document_status("non_existent_doc")

        # Verify not found
        self.assertIsNone(status)

    def test_get_system_metrics(self):
        """Test getting system metrics."""
        # Set up some test data
        self.tracker.system_metrics.total_documents_processed = 10
        self.tracker.system_metrics.successful_documents = 8
        self.tracker.system_metrics.failed_documents = 2
        self.tracker.system_metrics.current_active_documents = 1
        self.tracker.system_metrics.peak_concurrent_documents = 3
        self.tracker.system_metrics.average_processing_time = 2.5
        self.tracker.system_metrics.error_rate = 20.0
        self.tracker.system_metrics.throughput_per_hour = 5.0

        metrics = self.tracker.get_system_metrics()

        # Verify metrics structure
        self.assertIn('total_documents_processed', metrics)
        self.assertIn('successful_documents', metrics)
        self.assertIn('failed_documents', metrics)
        self.assertIn('current_active_documents', metrics)
        self.assertIn('peak_concurrent_documents', metrics)
        self.assertIn('average_processing_time', metrics)
        self.assertIn('error_rate', metrics)
        self.assertIn('throughput_per_hour', metrics)
        self.assertIn('last_updated', metrics)

        # Verify values
        self.assertEqual(metrics['total_documents_processed'], 10)
        self.assertEqual(metrics['successful_documents'], 8)
        self.assertEqual(metrics['failed_documents'], 2)
        self.assertEqual(metrics['current_active_documents'], 1)
        self.assertEqual(metrics['peak_concurrent_documents'], 3)
        self.assertEqual(metrics['average_processing_time'], 2.5)
        self.assertEqual(metrics['error_rate'], 20.0)
        self.assertEqual(metrics['throughput_per_hour'], 5.0)

    def test_get_active_documents(self):
        """Test getting active documents."""
        # Set up test documents
        self.tracker.start_processing("doc_001")
        self.tracker.start_processing("doc_002")
        self.tracker.start_processing("doc_003")

        # Complete one document
        self.tracker.complete_processing("doc_001", success=True)

        # Cancel one document
        self.tracker.cancel_processing("doc_002", "test_reason")

        # Record retry for one document
        self.tracker.record_retry("doc_003", "test_retry")

        active_documents = self.tracker.get_active_documents()

        # Verify active documents (processing and retrying)
        self.assertEqual(len(active_documents), 1)  # Only doc_003 should be active
        self.assertEqual(active_documents[0]['document_id'], 'doc_003')
        self.assertEqual(active_documents[0]['status'], 'retrying')

    def test_get_recent_activity(self):
        """Test getting recent activity."""
        # Set up test activity
        self.tracker.start_processing("doc_001")
        self.tracker.update_stage("doc_001", "ai_processing", 50.0)
        self.tracker.complete_processing("doc_001", success=True)

        recent_activity = self.tracker.get_recent_activity(limit=10)

        # Verify activity structure
        self.assertGreater(len(recent_activity), 0)
        for activity in recent_activity:
            self.assertIn('document_id', activity)
            self.assertIn('status', activity)
            self.assertIn('message', activity)
            self.assertIn('timestamp', activity)

    def test_get_recent_activity_with_limit(self):
        """Test getting recent activity with limit."""
        # Set up more activity than limit
        for i in range(15):
            doc_id = f"doc_{i:03d}"
            self.tracker.start_processing(doc_id)
            self.tracker.complete_processing(doc_id, success=True)

        recent_activity = self.tracker.get_recent_activity(limit=5)

        # Verify limit applied
        self.assertEqual(len(recent_activity), 5)

    def test_cleanup_old_metrics(self):
        """Test cleanup of old metrics."""
        # Set up old metrics
        old_time = datetime.now() - timedelta(hours=25)

        # Mock old processing metrics
        old_metrics = ProcessingMetrics(
            document_id="old_doc",
            start_time=old_time,
            status=ProcessingStatus.COMPLETED,
            end_time=old_time + timedelta(minutes=5)
        )
        self.tracker.processing_metrics["old_doc"] = old_metrics

        # Set up old status history
        old_history = {
            'document_id': 'old_doc',
            'status': 'completed',
            'message': 'Old activity',
            'timestamp': old_time.isoformat()
        }
        self.tracker.status_history.append(old_history)

        # Cleanup old metrics
        cleaned_count = self.tracker.cleanup_old_metrics(hours=24)

        # Verify cleanup
        self.assertGreater(cleaned_count, 0)
        self.assertNotIn("old_doc", self.tracker.processing_metrics)
        self.assertEqual(len(self.tracker.status_history), 0)

    def test_cleanup_old_metrics_with_custom_hours(self):
        """Test cleanup with custom retention hours."""
        # Set up metrics with different ages
        recent_time = datetime.now() - timedelta(hours=1)
        old_time = datetime.now() - timedelta(hours=3)

        # Recent metrics
        recent_metrics = ProcessingMetrics(
            document_id="recent_doc",
            start_time=recent_time,
            status=ProcessingStatus.COMPLETED,
            end_time=recent_time + timedelta(minutes=5)
        )
        self.tracker.processing_metrics["recent_doc"] = recent_metrics

        # Old metrics
        old_metrics = ProcessingMetrics(
            document_id="old_doc",
            start_time=old_time,
            status=ProcessingStatus.COMPLETED,
            end_time=old_time + timedelta(minutes=5)
        )
        self.tracker.processing_metrics["old_doc"] = old_metrics

        # Cleanup with 2-hour retention
        cleaned_count = self.tracker.cleanup_old_metrics(hours=2)

        # Verify only old metrics cleaned
        self.assertEqual(cleaned_count, 1)
        self.assertIn("recent_doc", self.tracker.processing_metrics)
        self.assertNotIn("old_doc", self.tracker.processing_metrics)

    def test_update_average_processing_time(self):
        """Test average processing time calculation."""
        # First processing time
        self.tracker._update_average_processing_time(2.0)
        self.assertEqual(self.tracker.system_metrics.average_processing_time, 2.0)

        # Second processing time
        self.tracker._update_average_processing_time(4.0)
        expected_avg = (2.0 + 4.0) / 2
        self.assertEqual(self.tracker.system_metrics.average_processing_time, expected_avg)

        # Third processing time
        self.tracker._update_average_processing_time(6.0)
        expected_avg = (2.0 + 4.0 + 6.0) / 3
        self.assertEqual(self.tracker.system_metrics.average_processing_time, expected_avg)

    def test_update_error_rate(self):
        """Test error rate calculation."""
        # Set up test data
        self.tracker.system_metrics.total_documents_processed = 10
        self.tracker.system_metrics.failed_documents = 2

        self.tracker._update_error_rate()

        # Verify error rate calculation (2/10 * 100 = 20%)
        self.assertEqual(self.tracker.system_metrics.error_rate, 20.0)

    def test_update_error_rate_zero_total(self):
        """Test error rate calculation with zero total documents."""
        # Set up test data
        self.tracker.system_metrics.total_documents_processed = 0
        self.tracker.system_metrics.failed_documents = 0

        self.tracker._update_error_rate()

        # Verify error rate is 0 when no documents processed
        self.assertEqual(self.tracker.system_metrics.error_rate, 0.0)

    def test_update_throughput(self):
        """Test throughput calculation."""
        # Set up recent activity
        recent_time = datetime.now() - timedelta(minutes=30)
        old_time = datetime.now() - timedelta(hours=2)

        # Recent completed activities
        recent_activity = {
            'document_id': 'recent_doc',
            'status': 'completed',
            'message': 'Recent completion',
            'timestamp': recent_time.isoformat()
        }
        self.tracker.status_history.append(recent_activity)

        # Old completed activity
        old_activity = {
            'document_id': 'old_doc',
            'status': 'completed',
            'message': 'Old completion',
            'timestamp': old_time.isoformat()
        }
        self.tracker.status_history.append(old_activity)

        # Failed activity (should not count)
        failed_activity = {
            'document_id': 'failed_doc',
            'status': 'failed',
            'message': 'Failed processing',
            'timestamp': recent_time.isoformat()
        }
        self.tracker.status_history.append(failed_activity)

        self.tracker._update_throughput()

        # Verify throughput (only recent completed activities count)
        self.assertEqual(self.tracker.system_metrics.throughput_per_hour, 1)

    def test_export_metrics_success(self):
        """Test successful metrics export."""
        # Set up test data
        self.tracker.start_processing("doc_001")
        self.tracker.complete_processing("doc_001", success=True)

        # Export metrics
        result = self.tracker.export_metrics("/tmp/test_metrics.json")

        # Verify export success
        self.assertTrue(result)

        # Verify file was created and contains data
        import os
        self.assertTrue(os.path.exists("/tmp/test_metrics.json"))

        # Clean up
        os.remove("/tmp/test_metrics.json")

    def test_export_metrics_failure(self):
        """Test metrics export failure."""
        # Try to export to invalid path
        result = self.tracker.export_metrics("/invalid/path/test_metrics.json")

        # Verify export failure
        self.assertFalse(result)

    def test_thread_safety(self):
        """Test thread safety of status tracker."""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id):
            try:
                doc_id = f"doc_{worker_id}"
                self.tracker.start_processing(doc_id)
                time.sleep(0.01)  # Small delay
                self.tracker.update_stage(doc_id, "processing", 50.0)
                time.sleep(0.01)
                self.tracker.complete_processing(doc_id, success=True)
                results.append(worker_id)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all workers completed successfully
        self.assertEqual(len(results), 10)
        self.assertEqual(len(errors), 0)

        # Verify system metrics
        self.assertEqual(self.tracker.system_metrics.total_documents_processed, 10)
        self.assertEqual(self.tracker.system_metrics.successful_documents, 10)
        self.assertEqual(self.tracker.system_metrics.current_active_documents, 0)

    def test_peak_concurrent_documents_tracking(self):
        """Test peak concurrent documents tracking."""
        # Start multiple documents
        self.tracker.start_processing("doc_001")
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 1)

        self.tracker.start_processing("doc_002")
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 2)

        self.tracker.start_processing("doc_003")
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 3)

        # Complete one document
        self.tracker.complete_processing("doc_001", success=True)
        self.assertEqual(self.tracker.system_metrics.current_active_documents, 2)
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 3)  # Peak should remain

        # Complete remaining documents
        self.tracker.complete_processing("doc_002", success=True)
        self.tracker.complete_processing("doc_003", success=True)

        self.assertEqual(self.tracker.system_metrics.current_active_documents, 0)
        self.assertEqual(self.tracker.system_metrics.peak_concurrent_documents, 3)

    def test_status_history_management(self):
        """Test status history management and size limits."""
        # Add more activities than max history size
        for i in range(1500):  # More than max_history_size (1000)
            self.tracker._log_status_change(f"doc_{i:04d}", ProcessingStatus.PROCESSING, f"Activity {i}")

        # Verify history size is limited
        self.assertEqual(len(self.tracker.status_history), 1000)

        # Verify most recent activities are kept
        self.assertIn("doc_1499", self.tracker.status_history[-1]['document_id'])
        self.assertNotIn("doc_0000", [activity['document_id'] for activity in self.tracker.status_history])

    def test_performance_requirements(self):
        """Test that tracker meets performance requirements."""
        # Verify configuration supports performance
        self.assertGreaterEqual(self.tracker.max_history_size, 100)
        self.assertGreaterEqual(self.tracker.metrics_retention_hours, 1)

        # Verify thread safety is implemented
        self.assertIsInstance(self.tracker.lock, threading.Lock)

        # Test performance with many operations
        start_time = time.time()

        for i in range(100):
            doc_id = f"perf_doc_{i:03d}"
            self.tracker.start_processing(doc_id)
            self.tracker.update_stage(doc_id, "processing", 50.0)
            self.tracker.complete_processing(doc_id, success=True)

        end_time = time.time()
        processing_time = end_time - start_time

        # Verify performance (should complete 100 operations quickly)
        self.assertLess(processing_time, 1.0)  # Less than 1 second for 100 operations

    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        # Test with invalid document IDs
        self.assertFalse(self.tracker.update_stage(None, "test", 50.0))
        self.assertFalse(self.tracker.record_error("", "test error", "test"))
        self.assertFalse(self.tracker.complete_processing(123, success=True))

        # Test with invalid progress values
        self.tracker.start_processing("test_doc")
        self.tracker.update_stage("test_doc", "test", float('inf'))
        self.tracker.update_stage("test_doc", "test", float('-inf'))
        self.tracker.update_stage("test_doc", "test", float('nan'))

        # Verify tracker still functions
        self.tracker.complete_processing("test_doc", success=True)
        self.assertEqual(self.tracker.system_metrics.total_documents_processed, 1)

class TestProcessingMetrics(unittest.TestCase):
    """Test ProcessingMetrics data structure."""

    def test_processing_metrics_creation(self):
        """Test ProcessingMetrics creation and properties."""
        start_time = datetime.now()
        metrics = ProcessingMetrics(
            document_id="doc_001",
            start_time=start_time,
            status=ProcessingStatus.PROCESSING,
            current_stage="ai_processing",
            progress_percentage=50.0,
            error_count=1,
            retry_count=2
        )

        # Verify properties
        self.assertEqual(metrics.document_id, "doc_001")
        self.assertEqual(metrics.start_time, start_time)
        self.assertIsNone(metrics.end_time)
        self.assertIsNone(metrics.processing_time)
        self.assertEqual(metrics.status, ProcessingStatus.PROCESSING)
        self.assertEqual(metrics.current_stage, "ai_processing")
        self.assertEqual(metrics.progress_percentage, 50.0)
        self.assertEqual(metrics.error_count, 1)
        self.assertEqual(metrics.retry_count, 2)
        self.assertIsInstance(metrics.stage_timings, dict)
        self.assertIsInstance(metrics.resource_usage, dict)

    def test_processing_metrics_with_end_time(self):
        """Test ProcessingMetrics with end time and processing time."""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=5)

        metrics = ProcessingMetrics(
            document_id="doc_001",
            start_time=start_time,
            end_time=end_time,
            processing_time=300.0,  # 5 minutes
            status=ProcessingStatus.COMPLETED
        )

        # Verify properties
        self.assertEqual(metrics.end_time, end_time)
        self.assertEqual(metrics.processing_time, 300.0)
        self.assertEqual(metrics.status, ProcessingStatus.COMPLETED)

class TestSystemMetrics(unittest.TestCase):
    """Test SystemMetrics data structure."""

    def test_system_metrics_creation(self):
        """Test SystemMetrics creation and properties."""
        metrics = SystemMetrics(
            total_documents_processed=100,
            successful_documents=90,
            failed_documents=10,
            average_processing_time=2.5,
            current_active_documents=5,
            peak_concurrent_documents=15,
            error_rate=10.0,
            throughput_per_hour=25.0
        )

        # Verify properties
        self.assertEqual(metrics.total_documents_processed, 100)
        self.assertEqual(metrics.successful_documents, 90)
        self.assertEqual(metrics.failed_documents, 10)
        self.assertEqual(metrics.average_processing_time, 2.5)
        self.assertEqual(metrics.current_active_documents, 5)
        self.assertEqual(metrics.peak_concurrent_documents, 15)
        self.assertEqual(metrics.error_rate, 10.0)
        self.assertEqual(metrics.throughput_per_hour, 25.0)
        self.assertIsNotNone(metrics.last_updated)

    def test_system_metrics_defaults(self):
        """Test SystemMetrics with default values."""
        metrics = SystemMetrics()

        # Verify defaults
        self.assertEqual(metrics.total_documents_processed, 0)
        self.assertEqual(metrics.successful_documents, 0)
        self.assertEqual(metrics.failed_documents, 0)
        self.assertEqual(metrics.average_processing_time, 0.0)
        self.assertEqual(metrics.current_active_documents, 0)
        self.assertEqual(metrics.peak_concurrent_documents, 0)
        self.assertEqual(metrics.error_rate, 0.0)
        self.assertEqual(metrics.throughput_per_hour, 0.0)
        self.assertIsNotNone(metrics.last_updated)

class TestProcessingStatus(unittest.TestCase):
    """Test ProcessingStatus enumeration."""

    def test_processing_status_values(self):
        """Test ProcessingStatus enumeration values."""
        self.assertEqual(ProcessingStatus.PENDING.value, "pending")
        self.assertEqual(ProcessingStatus.PROCESSING.value, "processing")
        self.assertEqual(ProcessingStatus.COMPLETED.value, "completed")
        self.assertEqual(ProcessingStatus.FAILED.value, "failed")
        self.assertEqual(ProcessingStatus.RETRYING.value, "retrying")
        self.assertEqual(ProcessingStatus.CANCELLED.value, "cancelled")

    def test_processing_status_enumeration(self):
        """Test ProcessingStatus enumeration membership."""
        self.assertIn(ProcessingStatus.PROCESSING, ProcessingStatus)
        self.assertIn(ProcessingStatus.COMPLETED, ProcessingStatus)
        self.assertIn(ProcessingStatus.FAILED, ProcessingStatus)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
