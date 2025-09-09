"""
BigQuery Client for Legal Document Intelligence Platform
BigQuery AI Hackathon Entry

This module provides a wrapper around the BigQuery client for the legal AI platform.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound, BadRequest
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class BigQueryClient:
    """BigQuery client wrapper for the Legal Document Intelligence Platform."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BigQuery client.

        Args:
            config: Configuration dictionary containing BigQuery settings
        """
        self.config = config
        self.bigquery_config = config.get('bigquery', {})
        self.project_id = self.bigquery_config.get('project_id')
        self.location = self.bigquery_config.get('location', 'US')

        if not self.project_id:
            raise ValueError("BigQuery project_id is required in configuration")

        # Initialize BigQuery client
        self._initialize_client()

        logger.info(f"BigQuery client initialized for project: {self.project_id}")

    def _initialize_client(self):
        """Initialize the BigQuery client."""
        try:
            # Check for service account key file
            service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

            if service_account_path and os.path.exists(service_account_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_path
                )
                self.client = bigquery.Client(
                    project=self.project_id,
                    credentials=credentials,
                    location=self.location
                )
                logger.info("Using service account credentials")
            else:
                # Use default credentials (ADC)
                self.client = bigquery.Client(
                    project=self.project_id,
                    location=self.location
                )
                logger.info("Using default credentials (Application Default Credentials)")

        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test BigQuery connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple query to test connection
            query = "SELECT 1 as test_value"
            result = self.client.query(query).result()

            for row in result:
                if row.test_value == 1:
                    logger.info("BigQuery connection test successful")
                    return True

            return False

        except Exception as e:
            logger.error(f"BigQuery connection test failed: {e}")
            return False

    def create_dataset(self, dataset_id: str, description: str = "") -> bool:
        """
        Create a BigQuery dataset.

        Args:
            dataset_id: Dataset ID to create
            description: Dataset description

        Returns:
            True if dataset was created successfully, False otherwise
        """
        try:
            dataset_ref = self.client.dataset(dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.description = description
            dataset.location = self.location

            dataset = self.client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Dataset {dataset_id} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create dataset {dataset_id}: {e}")
            return False

    def create_table(self, table_id: str, schema: List[bigquery.SchemaField]) -> bool:
        """
        Create a BigQuery table.

        Args:
            table_id: Full table ID (project.dataset.table)
            schema: Table schema

        Returns:
            True if table was created successfully, False otherwise
        """
        try:
            table_ref = bigquery.TableReference.from_string(table_id)
            table = bigquery.Table(table_ref, schema=schema)

            table = self.client.create_table(table, exists_ok=True)
            logger.info(f"Table {table_id} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create table {table_id}: {e}")
            return False

    def execute_query(self, query: str) -> Optional[bigquery.QueryJob]:
        """
        Execute a BigQuery SQL query.

        Args:
            query: SQL query to execute

        Returns:
            QueryJob object if successful, None otherwise
        """
        try:
            job = self.client.query(query)
            result = job.result()  # Wait for job to complete

            logger.info(f"Query executed successfully: {job.job_id}")
            return job

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return None

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get BigQuery project information.

        Returns:
            Project information dictionary
        """
        try:
            # Get project info using the client's project property
            return {
                'project_id': self.project_id,
                'name': f"Project {self.project_id}",
                'project_number': 'N/A'
            }

        except Exception as e:
            logger.error(f"Failed to get project info: {e}")
            return {}

    def list_datasets(self) -> List[str]:
        """
        List all datasets in the project.

        Returns:
            List of dataset IDs
        """
        try:
            datasets = list(self.client.list_datasets())
            dataset_ids = [dataset.dataset_id for dataset in datasets]

            logger.info(f"Found {len(dataset_ids)} datasets")
            return dataset_ids

        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return []
