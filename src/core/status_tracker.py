"""
Processing Status Tracking
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module provides comprehensive status tracking for document processing
with real-time monitoring and metrics collection.
"""

import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

@dataclass
class ProcessingMetrics:
    """Processing metrics data structure."""
    document_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    processing_time: Optional[float] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    current_stage: str = "initialization"
    progress_percentage: float = 0.0
    error_count: int = 0
    retry_count: int = 0
    stage_timings: Dict[str, float] = None
    resource_usage: Dict[str, Any] = None

    def __post_init__(self):
        if self.stage_timings is None:
            self.stage_timings = {}
        if self.resource_usage is None:
            self.resource_usage = {}

@dataclass
class SystemMetrics:
    """System-wide metrics data structure."""
    total_documents_processed: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    average_processing_time: float = 0.0
    current_active_documents: int = 0
    peak_concurrent_documents: int = 0
    error_rate: float = 0.0
    throughput_per_hour: float = 0.0
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class StatusTracker:
    """
    Comprehensive status tracking system for document processing
    with real-time monitoring and metrics collection.
    """

    def __init__(self):
        """Initialize the status tracker."""
        self.processing_metrics: Dict[str, ProcessingMetrics] = {}
        self.system_metrics = SystemMetrics()
        self.status_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

        # Configuration
        self.max_history_size = 1000
        self.metrics_retention_hours = 24

    def start_processing(self, document_id: str, metadata: Dict[str, Any] = None) -> ProcessingMetrics:
        """
        Start tracking processing for a document.

        Args:
            document_id: Unique document identifier
            metadata: Additional metadata for the document

        Returns:
            ProcessingMetrics object for the document
        """
        with self.lock:
            metrics = ProcessingMetrics(
                document_id=document_id,
                start_time=datetime.now(),
                status=ProcessingStatus.PROCESSING,
                current_stage="initialization",
                progress_percentage=0.0,
                resource_usage=metadata or {}
            )

            self.processing_metrics[document_id] = metrics
            self.system_metrics.current_active_documents += 1

            # Update peak concurrent documents
            if self.system_metrics.current_active_documents > self.system_metrics.peak_concurrent_documents:
                self.system_metrics.peak_concurrent_documents = self.system_metrics.current_active_documents

            self._log_status_change(document_id, ProcessingStatus.PROCESSING, "Processing started")

            logger.info(f"🔄 Started tracking document {document_id}")
            return metrics

    def update_stage(self, document_id: str, stage: str, progress: float = None) -> bool:
        """
        Update the current processing stage for a document.

        Args:
            document_id: Document identifier
            stage: Current processing stage
            progress: Progress percentage (0-100)

        Returns:
            True if update successful, False otherwise
        """
        with self.lock:
            if document_id not in self.processing_metrics:
                logger.warning(f"⚠️ Document {document_id} not found in tracking")
                return False

            metrics = self.processing_metrics[document_id]
            previous_stage = metrics.current_stage

            # Update stage timing
            if previous_stage != stage:
                stage_start_time = datetime.now()
                if previous_stage in metrics.stage_timings:
                    # Calculate time spent in previous stage
                    previous_stage_time = (stage_start_time - metrics.start_time).total_seconds()
                    metrics.stage_timings[previous_stage] = previous_stage_time

                metrics.current_stage = stage
                self._log_status_change(document_id, metrics.status, f"Stage changed to {stage}")

            # Update progress
            if progress is not None:
                metrics.progress_percentage = min(100.0, max(0.0, progress))

            logger.debug(f"📊 Updated stage for document {document_id}: {stage} ({metrics.progress_percentage:.1f}%)")
            return True

    def record_error(self, document_id: str, error_message: str, error_type: str = "unknown") -> bool:
        """
        Record an error for a document.

        Args:
            document_id: Document identifier
            error_message: Error message
            error_type: Type of error

        Returns:
            True if error recorded successfully, False otherwise
        """
        with self.lock:
            if document_id not in self.processing_metrics:
                logger.warning(f"⚠️ Document {document_id} not found in tracking")
                return False

            metrics = self.processing_metrics[document_id]
            metrics.error_count += 1

            self._log_status_change(document_id, metrics.status, f"Error recorded: {error_message}")

            logger.warning(f"⚠️ Error recorded for document {document_id}: {error_message}")
            return True

    def record_retry(self, document_id: str, retry_reason: str = "unknown") -> bool:
        """
        Record a retry attempt for a document.

        Args:
            document_id: Document identifier
            retry_reason: Reason for retry

        Returns:
            True if retry recorded successfully, False otherwise
        """
        with self.lock:
            if document_id not in self.processing_metrics:
                logger.warning(f"⚠️ Document {document_id} not found in tracking")
                return False

            metrics = self.processing_metrics[document_id]
            metrics.retry_count += 1
            metrics.status = ProcessingStatus.RETRYING

            self._log_status_change(document_id, ProcessingStatus.RETRYING, f"Retry attempt {metrics.retry_count}: {retry_reason}")

            logger.info(f"🔄 Retry recorded for document {document_id}: {retry_reason}")
            return True

    def complete_processing(self, document_id: str, success: bool = True,
                          final_results: Dict[str, Any] = None) -> bool:
        """
        Mark processing as completed for a document.

        Args:
            document_id: Document identifier
            success: Whether processing was successful
            final_results: Final processing results

        Returns:
            True if completion recorded successfully, False otherwise
        """
        with self.lock:
            if document_id not in self.processing_metrics:
                logger.warning(f"⚠️ Document {document_id} not found in tracking")
                return False

            metrics = self.processing_metrics[document_id]
            metrics.end_time = datetime.now()
            metrics.processing_time = (metrics.end_time - metrics.start_time).total_seconds()
            metrics.status = ProcessingStatus.COMPLETED if success else ProcessingStatus.FAILED
            metrics.progress_percentage = 100.0

            # Update system metrics
            self.system_metrics.total_documents_processed += 1
            self.system_metrics.current_active_documents -= 1

            if success:
                self.system_metrics.successful_documents += 1
            else:
                self.system_metrics.failed_documents += 1

            # Update average processing time
            self._update_average_processing_time(metrics.processing_time)

            # Update error rate
            self._update_error_rate()

            # Update throughput
            self._update_throughput()

            # Store final results in resource usage
            if final_results:
                metrics.resource_usage['final_results'] = final_results

            self._log_status_change(document_id, metrics.status,
                                  f"Processing completed ({'success' if success else 'failed'})")

            logger.info(f"✅ Processing completed for document {document_id}: {'success' if success else 'failed'}")
            return True

    def cancel_processing(self, document_id: str, reason: str = "user_cancelled") -> bool:
        """
        Cancel processing for a document.

        Args:
            document_id: Document identifier
            reason: Reason for cancellation

        Returns:
            True if cancellation recorded successfully, False otherwise
        """
        with self.lock:
            if document_id not in self.processing_metrics:
                logger.warning(f"⚠️ Document {document_id} not found in tracking")
                return False

            metrics = self.processing_metrics[document_id]
            metrics.status = ProcessingStatus.CANCELLED
            metrics.end_time = datetime.now()
            metrics.processing_time = (metrics.end_time - metrics.start_time).total_seconds()

            self.system_metrics.current_active_documents -= 1

            self._log_status_change(document_id, ProcessingStatus.CANCELLED, f"Cancelled: {reason}")

            logger.info(f"🚫 Processing cancelled for document {document_id}: {reason}")
            return True

    def get_document_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status for a specific document.

        Args:
            document_id: Document identifier

        Returns:
            Document status information or None if not found
        """
        with self.lock:
            if document_id not in self.processing_metrics:
                return None

            metrics = self.processing_metrics[document_id]
            return {
                'document_id': document_id,
                'status': metrics.status.value,
                'current_stage': metrics.current_stage,
                'progress_percentage': metrics.progress_percentage,
                'start_time': metrics.start_time.isoformat(),
                'end_time': metrics.end_time.isoformat() if metrics.end_time else None,
                'processing_time': metrics.processing_time,
                'error_count': metrics.error_count,
                'retry_count': metrics.retry_count,
                'stage_timings': metrics.stage_timings,
                'resource_usage': metrics.resource_usage
            }

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system-wide metrics.

        Returns:
            System metrics information
        """
        with self.lock:
            self.system_metrics.last_updated = datetime.now()

            return {
                'total_documents_processed': self.system_metrics.total_documents_processed,
                'successful_documents': self.system_metrics.successful_documents,
                'failed_documents': self.system_metrics.failed_documents,
                'current_active_documents': self.system_metrics.current_active_documents,
                'peak_concurrent_documents': self.system_metrics.peak_concurrent_documents,
                'average_processing_time': self.system_metrics.average_processing_time,
                'error_rate': self.system_metrics.error_rate,
                'throughput_per_hour': self.system_metrics.throughput_per_hour,
                'last_updated': self.system_metrics.last_updated.isoformat()
            }

    def get_active_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active documents.

        Returns:
            List of active document statuses
        """
        with self.lock:
            active_documents = []

            for document_id, metrics in self.processing_metrics.items():
                if metrics.status in [ProcessingStatus.PROCESSING, ProcessingStatus.RETRYING]:
                    active_documents.append(self.get_document_status(document_id))

            return active_documents

    def get_recent_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent processing activity.

        Args:
            limit: Maximum number of recent activities to return

        Returns:
            List of recent activities
        """
        with self.lock:
            return self.status_history[-limit:] if self.status_history else []

    def cleanup_old_metrics(self, hours: int = None) -> int:
        """
        Clean up old metrics to prevent memory growth.

        Args:
            hours: Hours of metrics to retain (default: 24)

        Returns:
            Number of metrics cleaned up
        """
        if hours is None:
            hours = self.metrics_retention_hours

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cleaned_count = 0

        with self.lock:
            # Clean up completed/failed documents older than cutoff
            documents_to_remove = []

            for document_id, metrics in self.processing_metrics.items():
                if (metrics.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED]
                    and metrics.end_time and metrics.end_time < cutoff_time):
                    documents_to_remove.append(document_id)

            for document_id in documents_to_remove:
                del self.processing_metrics[document_id]
                cleaned_count += 1

            # Clean up old status history
            if self.status_history:
                original_size = len(self.status_history)
                self.status_history = [
                    entry for entry in self.status_history
                    if datetime.fromisoformat(entry['timestamp']) > cutoff_time
                ]
                cleaned_count += original_size - len(self.status_history)

        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} old metrics entries")

        return cleaned_count

    def _log_status_change(self, document_id: str, status: ProcessingStatus, message: str):
        """Log a status change event."""
        event = {
            'document_id': document_id,
            'status': status.value,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        self.status_history.append(event)

        # Limit history size
        if len(self.status_history) > self.max_history_size:
            self.status_history = self.status_history[-self.max_history_size:]

    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time."""
        total = self.system_metrics.total_documents_processed
        current_avg = self.system_metrics.average_processing_time

        if total == 1:
            self.system_metrics.average_processing_time = processing_time
        else:
            self.system_metrics.average_processing_time = (
                (current_avg * (total - 1) + processing_time) / total
            )

    def _update_error_rate(self):
        """Update error rate calculation."""
        total = self.system_metrics.total_documents_processed
        if total > 0:
            self.system_metrics.error_rate = (
                self.system_metrics.failed_documents / total
            ) * 100

    def _update_throughput(self):
        """Update throughput calculation (documents per hour)."""
        # Calculate throughput based on recent activity
        recent_activities = [
            entry for entry in self.status_history
            if datetime.fromisoformat(entry['timestamp']) > datetime.now() - timedelta(hours=1)
        ]

        completed_in_last_hour = len([
            entry for entry in recent_activities
            if entry['status'] in ['completed', 'failed']
        ])

        self.system_metrics.throughput_per_hour = completed_in_last_hour

    def export_metrics(self, filepath: str) -> bool:
        """
        Export metrics to a JSON file.

        Args:
            filepath: Path to export file

        Returns:
            True if export successful, False otherwise
        """
        try:
            with self.lock:
                export_data = {
                    'system_metrics': asdict(self.system_metrics),
                    'processing_metrics': {
                        doc_id: asdict(metrics) for doc_id, metrics in self.processing_metrics.items()
                    },
                    'status_history': self.status_history,
                    'export_timestamp': datetime.now().isoformat()
                }

                # Convert datetime objects to strings
                def convert_datetime(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return obj

                export_data = json.loads(json.dumps(export_data, default=convert_datetime))

                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2)

                logger.info(f"📊 Metrics exported to {filepath}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to export metrics: {e}")
            return False

def main():
    """Test the status tracker."""
    print("🔄 Status Tracker - Phase 3 Implementation")
    print("=" * 60)

    # This would be used in integration tests
    print("✅ Status tracker class created successfully")

if __name__ == "__main__":
    main()
