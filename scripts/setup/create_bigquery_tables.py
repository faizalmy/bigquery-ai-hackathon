#!/usr/bin/env python3
"""
BigQuery Dataset and Table Creation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script creates all required BigQuery datasets and tables based on the configuration.
"""

import sys
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_client import BigQueryClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BigQuerySetup:
    """Handles BigQuery dataset and table creation."""

    def __init__(self, config_path: str = "config/bigquery_config.yaml"):
        """Initialize BigQuery setup with configuration."""
        self.config_path = config_path
        self.client = BigQueryClient(config_path)
        self.config = self.client.get_config()

    def create_datasets(self) -> bool:
        """Create all required datasets and subdatasets."""
        try:
            logger.info("Creating BigQuery datasets...")

            # Connect to BigQuery
            if not self.client.connect():
                logger.error("Failed to connect to BigQuery")
                return False

            # Create main dataset
            main_dataset_name = list(self.config['datasets'].keys())[0]
            if self._create_main_dataset(main_dataset_name):
                logger.info(f"✅ Created main dataset: {main_dataset_name}")
            else:
                logger.error(f"❌ Failed to create main dataset: {main_dataset_name}")
                return False

            # Create subdatasets
            main_dataset_config = self.config['datasets'][main_dataset_name]
            if 'subdatasets' in main_dataset_config:
                for subdataset_name, subdataset_config in main_dataset_config['subdatasets'].items():
                    if self._create_subdataset(main_dataset_name, subdataset_name, subdataset_config):
                        logger.info(f"✅ Created subdataset: {main_dataset_name}_{subdataset_name}")
                    else:
                        logger.error(f"❌ Failed to create subdataset: {main_dataset_name}_{subdataset_name}")
                        return False

            logger.info("🎉 All datasets created successfully!")
            return True

        except Exception as e:
            logger.error(f"Dataset creation failed: {e}")
            return False

    def create_tables(self) -> bool:
        """Create all required tables with proper schemas."""
        try:
            logger.info("Creating BigQuery tables...")

            # Connect to BigQuery
            if not self.client.connect():
                logger.error("Failed to connect to BigQuery")
                return False

            # Create tables from configuration
            for table_name, table_config in self.config['tables'].items():
                if self._create_table(table_name, table_config):
                    logger.info(f"✅ Created table: {table_name}")
                else:
                    logger.error(f"❌ Failed to create table: {table_name}")
                    return False

            logger.info("🎉 All tables created successfully!")
            return True

        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            return False

    def _create_main_dataset(self, dataset_name: str) -> bool:
        """Create main dataset."""
        try:
            project_id = self.config['project']['id']
            location = self.config['project']['location']

            dataset_id = f"{project_id}.{dataset_name}"
            dataset_config = self.config['datasets'][dataset_name]

            # Check if dataset already exists
            if self.client._dataset_exists(dataset_id):
                logger.info(f"Dataset {dataset_id} already exists")
                return True

            # Create dataset
            return self.client.create_datasets()

        except Exception as e:
            logger.error(f"Failed to create main dataset {dataset_name}: {e}")
            return False

    def _create_subdataset(self, main_dataset_name: str, subdataset_name: str, subdataset_config: Dict[str, Any]) -> bool:
        """Create subdataset."""
        try:
            project_id = self.config['project']['id']
            location = self.config['project']['location']

            subdataset_id = f"{project_id}.{main_dataset_name}_{subdataset_name}"

            # Check if subdataset already exists
            if self.client._dataset_exists(subdataset_id):
                logger.info(f"Subdataset {subdataset_id} already exists")
                return True

            # Create subdataset
            return self.client.create_datasets()

        except Exception as e:
            logger.error(f"Failed to create subdataset {subdataset_name}: {e}")
            return False

    def _create_table(self, table_name: str, table_config: Dict[str, Any]) -> bool:
        """Create table with schema."""
        try:
            # Check if table already exists
            project_id = self.config['project']['id']
            # Fix dataset name format (remove dots, use underscores)
            dataset_name = table_config['dataset'].replace('.', '_')
            table_id = f"{project_id}.{dataset_name}.{table_name}"

            if self.client._table_exists(table_id):
                logger.info(f"Table {table_id} already exists")
                return True

            # Create table
            return self.client.create_tables()

        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            return False

    def validate_setup(self) -> Dict[str, Any]:
        """Validate complete BigQuery setup."""
        try:
            logger.info("Validating BigQuery setup...")

            # Connect to BigQuery
            if not self.client.connect():
                logger.error("Failed to connect to BigQuery")
                return {"overall_status": "FAILED", "error": "Connection failed"}

            # Run validation
            validation_results = self.client.validate_setup()

            # Log results
            if validation_results['overall_status'] == 'SUCCESS':
                logger.info("🎉 BigQuery setup validation passed!")
            else:
                logger.warning("⚠️ BigQuery setup validation failed")
                logger.warning(f"Results: {validation_results}")

            return validation_results

        except Exception as e:
            logger.error(f"Setup validation failed: {e}")
            return {"overall_status": "FAILED", "error": str(e)}

    def run_complete_setup(self) -> bool:
        """Run complete BigQuery setup process."""
        try:
            logger.info("🚀 Starting complete BigQuery setup...")

            # Step 1: Create datasets
            if not self.create_datasets():
                logger.error("Dataset creation failed")
                return False

            # Step 2: Create tables
            if not self.create_tables():
                logger.error("Table creation failed")
                return False

            # Step 3: Validate setup
            validation_results = self.validate_setup()
            if validation_results['overall_status'] != 'SUCCESS':
                logger.error("Setup validation failed")
                return False

            logger.info("🎉 Complete BigQuery setup successful!")
            return True

        except Exception as e:
            logger.error(f"Complete setup failed: {e}")
            return False


def main():
    """Main execution function."""
    try:
        print("🔧 BigQuery Dataset and Table Setup")
        print("=" * 50)

        # Initialize setup
        setup = BigQuerySetup()

        # Run complete setup
        if setup.run_complete_setup():
            print("\n✅ BigQuery setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: make test-bigquery")
            print("2. Start implementing BigQuery AI functions")
            print("3. Create development notebooks")
            return 0
        else:
            print("\n❌ BigQuery setup failed!")
            return 1

    except Exception as e:
        logger.error(f"Setup script failed: {e}")
        print(f"\n❌ Setup script failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
