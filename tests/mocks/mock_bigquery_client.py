#!/usr/bin/env python3
"""
Mock BigQuery Client for Unit Testing
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module provides mock implementations of BigQuery components for unit testing
without requiring actual BigQuery dependencies.
"""

import logging
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
from datetime import datetime

logger = logging.getLogger(__name__)

class MockBigQueryClient:
    """Mock BigQuery client for unit testing."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize mock BigQuery client."""
        self.config = config
        self.bigquery_config = config.get('bigquery', {})
        self.project_id = self.bigquery_config.get('project_id', 'test-project')
        self.location = self.bigquery_config.get('location', 'US')

        # Mock client
        self.client = Mock()
        self.client.project = self.project_id

        # Mock query results
        self._mock_query_results = {}
        self._mock_datasets = []
        self._mock_tables = {}

        logger.info(f"Mock BigQuery client initialized for project: {self.project_id}")

    def test_connection(self) -> bool:
        """Mock connection test - always returns True."""
        logger.info("Mock BigQuery connection test successful")
        return True

    def create_dataset(self, dataset_id: str, description: str = "") -> bool:
        """Mock dataset creation."""
        self._mock_datasets.append(dataset_id)
        logger.info(f"Mock dataset {dataset_id} created successfully")
        return True

    def create_table(self, table_id: str, schema: List[Any]) -> bool:
        """Mock table creation."""
        self._mock_tables[table_id] = {'schema': schema, 'created_at': datetime.now()}
        logger.info(f"Mock table {table_id} created successfully")
        return True

    def execute_query(self, query: str) -> Optional[Mock]:
        """Mock query execution."""
        # Create mock query job
        mock_job = Mock()
        mock_job.job_id = f"mock_job_{datetime.now().timestamp()}"
        mock_job.result.return_value = self._get_mock_query_result(query)

        logger.info(f"Mock query executed successfully: {mock_job.job_id}")
        return mock_job

    def _get_mock_query_result(self, query: str) -> Mock:
        """Get mock query result based on query type."""
        mock_result = Mock()

        if "SELECT 1 as test_value" in query:
            # Mock test query result
            mock_row = Mock()
            mock_row.test_value = 1
            mock_result.__iter__ = lambda: iter([mock_row])
        elif "document_id" in query.lower():
            # Mock document query result
            mock_row = Mock()
            mock_row.document_id = "test_doc_001"
            mock_row.document_type = "case_law"
            mock_row.cleaned_content = "Test case content"
            mock_row.extracted_metadata = {"jurisdiction": "federal"}
            mock_row.quality_score = 0.9
            mock_row.source_system = "test"
            mock_result.__iter__ = lambda: iter([mock_row])
        else:
            # Default empty result
            mock_result.__iter__ = lambda: iter([])

        return mock_result

    def get_project_info(self) -> Dict[str, Any]:
        """Mock project info."""
        return {
            'project_id': self.project_id,
            'name': f"Mock Project {self.project_id}",
            'project_number': '123456789'
        }

    def list_datasets(self) -> List[str]:
        """Mock dataset listing."""
        logger.info(f"Mock found {len(self._mock_datasets)} datasets")
        return self._mock_datasets.copy()

class MockBigQueryRow:
    """Mock BigQuery row for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockQueryJob:
    """Mock BigQuery query job for testing."""

    def __init__(self, job_id: str = "mock_job_001"):
        self.job_id = job_id
        self._result = None

    def result(self):
        """Return mock query result."""
        if self._result is None:
            self._result = Mock()
            self._result.__iter__ = lambda: iter([])
        return self._result

class MockBigQueryTable:
    """Mock BigQuery table for testing."""

    def __init__(self, table_id: str, schema: List[Any] = None):
        self.table_id = table_id
        self.schema = schema or []
        self.created = datetime.now()

class MockBigQueryDataset:
    """Mock BigQuery dataset for testing."""

    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.description = ""
        self.location = "US"
        self.created = datetime.now()

# Mock the google.cloud.bigquery module
class MockBigQueryModule:
    """Mock BigQuery module for testing."""

    class Client:
        def __init__(self, project=None, credentials=None, location=None):
            self.project = project
            self.credentials = credentials
            self.location = location

        def query(self, query: str):
            return MockQueryJob()

        def list_datasets(self):
            return []

        def create_dataset(self, dataset, exists_ok=False):
            return MockBigQueryDataset(dataset.dataset_id)

        def create_table(self, table, exists_ok=False):
            return MockBigQueryTable(table.table_id, table.schema)

    class Dataset:
        def __init__(self, dataset_ref):
            self.dataset_id = dataset_ref.dataset_id
            self.description = ""
            self.location = "US"

    class Table:
        def __init__(self, table_ref, schema=None):
            self.table_id = table_ref.table_id
            self.schema = schema or []

    class TableReference:
        @staticmethod
        def from_string(table_id: str):
            return MockTableReference(table_id)

    class SchemaField:
        def __init__(self, name, field_type, mode="NULLABLE", description=""):
            self.name = name
            self.field_type = field_type
            self.mode = mode
            self.description = description

    class QueryJob:
        def __init__(self, job_id: str = "mock_job_001"):
            self.job_id = job_id
            self._result = None

        def result(self):
            """Return mock query result."""
            if self._result is None:
                self._result = Mock()
                self._result.__iter__ = lambda: iter([])
            return self._result

class MockTableReference:
    """Mock table reference for testing."""

    def __init__(self, table_id: str):
        self.table_id = table_id

class MockServiceAccount:
    """Mock service account credentials for testing."""

    class Credentials:
        @staticmethod
        def from_service_account_file(file_path: str):
            return Mock()

# Mock the google.cloud.exceptions module
class MockBigQueryExceptions:
    class NotFound(Exception):
        pass

    class BadRequest(Exception):
        pass

# Mock the google.oauth2 module
class MockOAuth2:
    class service_account:
        Credentials = MockServiceAccount.Credentials

# Create mock modules
mock_bigquery = MockBigQueryModule()
mock_exceptions = MockBigQueryExceptions()
mock_oauth2 = MockOAuth2()

def setup_mock_imports():
    """Set up mock imports for testing."""
    import sys

    # Mock the google.cloud.bigquery module
    sys.modules['google.cloud.bigquery'] = mock_bigquery
    sys.modules['google.cloud.exceptions'] = mock_exceptions
    sys.modules['google.oauth2'] = mock_oauth2
    sys.modules['google.oauth2.service_account'] = mock_oauth2.service_account

    return True
