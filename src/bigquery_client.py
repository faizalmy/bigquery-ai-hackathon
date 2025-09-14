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

    def create_datasets(self) -> bool:
        """
        Create all required datasets and subdatasets.

        Returns:
            bool: True if all datasets created successfully, False otherwise
        """
        try:
            project_id = self.config['project']['id']
            location = self.config['project']['location']

            # Create main dataset
            main_dataset_id = f"{project_id}.{list(self.config['datasets'].keys())[0]}"
            main_dataset = bigquery.Dataset(main_dataset_id)
            main_dataset.location = location
            main_dataset.description = self.config['datasets'][list(self.config['datasets'].keys())[0]]['description']

            if not self._dataset_exists(main_dataset_id):
                self.client.create_dataset(main_dataset, timeout=30)
                logger.info(f"Created dataset: {main_dataset_id}")
            else:
                logger.info(f"Dataset already exists: {main_dataset_id}")

            # Create subdatasets
            for dataset_name, dataset_config in self.config['datasets'].items():
                if 'subdatasets' in dataset_config:
                    for subdataset_name, subdataset_config in dataset_config['subdatasets'].items():
                        subdataset_id = f"{project_id}.{dataset_name}_{subdataset_name}"
                        subdataset = bigquery.Dataset(subdataset_id)
                        subdataset.location = location
                        subdataset.description = subdataset_config['description']

                        if not self._dataset_exists(subdataset_id):
                            self.client.create_dataset(subdataset, timeout=30)
                            logger.info(f"Created subdataset: {subdataset_id}")
                        else:
                            logger.info(f"Subdataset already exists: {subdataset_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to create datasets: {e}")
            return False

    def create_tables(self) -> bool:
        """
        Create all required tables with proper schemas.

        Returns:
            bool: True if all tables created successfully, False otherwise
        """
        try:
            for table_name, table_config in self.config['tables'].items():
                # Fix dataset name format (remove dots, use underscores)
                dataset_name = table_config['dataset'].replace('.', '_')
                table_id = f"{self.config['project']['id']}.{dataset_name}.{table_name}"

                if not self._table_exists(table_id):
                    # Create table schema
                    schema = []
                    for field in table_config['schema']:
                        schema.append(
                            bigquery.SchemaField(
                                name=field['name'],
                                field_type=field['type'],
                                mode=field['mode'],
                                description=field['description']
                            )
                        )

                    # Create table
                    table = bigquery.Table(table_id, schema=schema)
                    table.description = table_config['description']

                    self.client.create_table(table, timeout=30)
                    logger.info(f"Created table: {table_id}")
                else:
                    logger.info(f"Table already exists: {table_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
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

    def execute_ai_query(self, query: str, **kwargs) -> bigquery.QueryJob:
        """
        Execute a BigQuery AI query (ML.GENERATE_TEXT, AI.GENERATE_TABLE, etc.).

        Args:
            query: SQL query with AI functions
            **kwargs: Additional query job configuration

        Returns:
            bigquery.QueryJob: Query job object
        """
        try:
            # AI queries require specific job configuration
            job_config = bigquery.QueryJobConfig(
                use_legacy_sql=False,
                **kwargs
            )
            query_job = self.client.query(query, job_config=job_config)
            logger.info(f"Executed AI query: {query[:100]}...")
            return query_job
        except Exception as e:
            logger.error(f"AI query execution failed: {e}")
            raise

    def get_client(self) -> bigquery.Client:
        """Get the BigQuery client instance."""
        if self.client is None:
            self.connect()
        return self.client

    def get_bigframes_session(self) -> bigframes.Session:
        """Get the BigFrames session instance."""
        if self.bigframes_session is None:
            self.connect()
        return self.bigframes_session

    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate complete BigQuery setup.

        Returns:
            Dict containing validation results
        """
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'project_id': self.config['project']['id'],
            'connection': False,
            'datasets': {},
            'tables': {},
            'ai_models': {},
            'overall_status': 'FAILED'
        }

        try:
            # Test connection
            if self.connect():
                validation_results['connection'] = True
                logger.info("✅ Connection validation passed")
            else:
                logger.error("❌ Connection validation failed")
                return validation_results

            # Validate datasets
            for dataset_name, dataset_config in self.config['datasets'].items():
                dataset_id = f"{self.config['project']['id']}.{dataset_name}"
                exists = self._dataset_exists(dataset_id)
                validation_results['datasets'][dataset_name] = exists

                if exists:
                    logger.info(f"✅ Dataset validation passed: {dataset_name}")
                else:
                    logger.error(f"❌ Dataset validation failed: {dataset_name}")

            # Validate tables
            for table_name, table_config in self.config['tables'].items():
                # Fix dataset name format (remove dots, use underscores)
                dataset_name = table_config['dataset'].replace('.', '_')
                table_id = f"{self.config['project']['id']}.{dataset_name}.{table_name}"
                exists = self._table_exists(table_id)
                validation_results['tables'][table_name] = exists

                if exists:
                    logger.info(f"✅ Table validation passed: {table_name}")
                else:
                    logger.error(f"❌ Table validation failed: {table_name}")

            # Test AI model access
            ai_models_status = self._test_ai_models()
            validation_results['ai_models'] = ai_models_status

            # Determine overall status
            all_datasets_exist = all(validation_results['datasets'].values())
            all_tables_exist = all(validation_results['tables'].values())
            ai_models_working = all(validation_results['ai_models'].values())

            if validation_results['connection'] and all_datasets_exist and all_tables_exist and ai_models_working:
                validation_results['overall_status'] = 'SUCCESS'
                logger.info("🎉 All validations passed!")
            else:
                logger.warning("⚠️ Some validations failed")

            return validation_results

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_results['error'] = str(e)
            return validation_results

    def _dataset_exists(self, dataset_id: str) -> bool:
        """Check if dataset exists."""
        try:
            self.client.get_dataset(dataset_id)
            return True
        except NotFound:
            return False

    def _table_exists(self, table_id: str) -> bool:
        """Check if table exists."""
        try:
            self.client.get_table(table_id)
            return True
        except NotFound:
            return False

    def _test_ai_models(self) -> Dict[str, bool]:
        """Test AI model access."""
        ai_models_status = {}

        try:
            # Test Gemini Pro model
            test_query = """
            SELECT ML.GENERATE_TEXT(
                MODEL `gemini-pro`,
                'Test query for model validation'
            ) as test_result
            """
            self.execute_ai_query(test_query)
            ai_models_status['gemini_pro'] = True
            logger.info("✅ Gemini Pro model test passed")

        except Exception as e:
            ai_models_status['gemini_pro'] = False
            logger.error(f"❌ Gemini Pro model test failed: {e}")

        try:
            # Test text embedding model
            test_query = """
            SELECT ML.GENERATE_EMBEDDING(
                MODEL `text-embedding-preview-0409`,
                'Test text for embedding validation'
            ) as test_embedding
            """
            self.execute_ai_query(test_query)
            ai_models_status['text_embedding'] = True
            logger.info("✅ Text embedding model test passed")

        except Exception as e:
            ai_models_status['text_embedding'] = False
            logger.error(f"❌ Text embedding model test failed: {e}")

        return ai_models_status

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        self.config.update(updates)
        logger.info("Configuration updated")

    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        path = config_path or self.config_path
        with open(path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False, indent=2)
        logger.info(f"Configuration saved to {path}")


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

    # Connect and setup
    if client.connect():
        print("✅ Connected to BigQuery")

        # Create datasets and tables
        if client.create_datasets():
            print("✅ Datasets created")

        if client.create_tables():
            print("✅ Tables created")

        # Validate setup
        validation_results = client.validate_setup()
        print(f"Validation results: {validation_results['overall_status']}")

    else:
        print("❌ Failed to connect to BigQuery")
