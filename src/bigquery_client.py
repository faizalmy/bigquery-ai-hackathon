"""
BigQuery Client Wrapper
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module provides a unified BigQuery client with configuration management,
connection handling, and automated setup capabilities.
"""

import logging
import yaml
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import os

from google.cloud import bigquery
from google.cloud.exceptions import NotFound, BadRequest
import bigframes
import bigframes.pandas as bpd

logger = logging.getLogger(__name__)

class BigQueryClient:
    """Unified BigQuery client with configuration management."""

    def __init__(self, config_path: str = "config/bigquery_config.yaml"):
        """
        Initialize BigQuery client with configuration.

        Args:
            config_path: Path to BigQuery configuration YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.client = None
        self.bigframes_session = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise

    def connect(self) -> bool:
        """
        Establish connection to BigQuery.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            project_id = self.config['project']['id']

            # Get location from config
            location = self.config.get('bigquery', {}).get('location', 'US')

            # Initialize BigQuery client with explicit location
            self.client = bigquery.Client(project=project_id, location=location)

            # Initialize BigFrames session with explicit location
            # Suppress the DefaultLocationWarning since we're using US location
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="No explicit location is set, so using location US for the session.")
                self.bigframes_session = bigframes.connect()

            # Test connection by listing datasets
            list(self.client.list_datasets(max_results=1))
            logger.info(f"Successfully connected to BigQuery project: {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to BigQuery: {e}")
            return False

    def execute_query(self, query: str, params: dict = None, **kwargs) -> bigquery.QueryJob:
        """
        Execute a BigQuery SQL query with optional parameters.

        Args:
            query: SQL query string
            params: Dictionary of query parameters
            **kwargs: Additional query job configuration

        Returns:
            bigquery.QueryJob: Query job object
        """
        try:
            # Ensure client is connected
            if self.client is None:
                self.connect()

            # Convert params dict to BigQuery parameter list
            query_params = []
            if params:
                for key, value in params.items():
                    if isinstance(value, str):
                        query_params.append(bigquery.ScalarQueryParameter(key, "STRING", value))
                    elif isinstance(value, int):
                        query_params.append(bigquery.ScalarQueryParameter(key, "INT64", value))
                    elif isinstance(value, float):
                        query_params.append(bigquery.ScalarQueryParameter(key, "FLOAT64", value))
                    else:
                        query_params.append(bigquery.ScalarQueryParameter(key, "STRING", str(value)))

            job_config = bigquery.QueryJobConfig(
                query_parameters=query_params,
                **kwargs
            )
            query_job = self.client.query(query, job_config=job_config)
            logger.info(f"Executed query: {query[:100]}...")
            return query_job
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

def create_bigquery_client(config_path: str = "config/bigquery_config.yaml") -> BigQueryClient:
    """
    Factory function to create and configure BigQuery client.

    Args:
        config_path: Path to configuration file

    Returns:
        BigQueryClient: Configured client instance
    """
    return BigQueryClient(config_path)
# Example usage
if __name__ == "__main__":
    # Initialize client
    client = create_bigquery_client()

    # Connect to BigQuery
    if client.connect():
        print("✅ Connected to BigQuery")
    else:
        print("❌ Failed to connect to BigQuery")
