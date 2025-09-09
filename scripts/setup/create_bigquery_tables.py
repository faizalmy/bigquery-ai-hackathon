#!/usr/bin/env python3
"""
BigQuery Tables Creation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script creates all the necessary BigQuery tables based on the schema definitions.
"""

import os
import sys
import json
import logging
from pathlib import Path
from google.cloud import bigquery
from google.cloud.exceptions import NotFound, BadRequest

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_table_schemas():
    """Load table schemas from configuration files."""
    config_dir = Path(__file__).parent.parent.parent / 'config' / 'bigquery'

    with open(config_dir / 'table_schemas.json', 'r') as f:
        return json.load(f)

def create_schema_fields(schema_def):
    """Convert schema definition to BigQuery SchemaField objects."""
    fields = []

    for field in schema_def:
        field_type = field['type']

        # Handle ARRAY types
        if field_type.startswith('ARRAY<'):
            # Extract the inner type
            inner_type = field_type[6:-1]  # Remove 'ARRAY<' and '>'
            field_type = inner_type
            mode = 'REPEATED'
        else:
            mode = field['mode']

        schema_field = bigquery.SchemaField(
            name=field['name'],
            field_type=field_type,
            mode=mode,
            description=field.get('description', '')
        )
        fields.append(schema_field)

    return fields

def create_tables():
    """Create all BigQuery tables."""
    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded configuration for environment: {config.get('environment', 'development')}")

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Test connection
        if not bq_client.test_connection():
            logger.error("Failed to connect to BigQuery. Please check your credentials and project setup.")
            return False

        logger.info("✅ BigQuery connection successful")

        # Load table schemas
        table_schemas = load_table_schemas()
        project_id = config['bigquery']['project_id']

        # Create tables
        for table_name, table_config in table_schemas['tables'].items():
            logger.info(f"Creating table: {table_name}")

            # Convert schema definition to BigQuery schema
            schema_fields = create_schema_fields(table_config['schema'])

            # Create full table ID
            full_table_id = f"{project_id}.{table_name}"

            # Create table
            success = bq_client.create_table(full_table_id, schema_fields)

            if success:
                logger.info(f"✅ Table {table_name} created successfully")
            else:
                logger.error(f"❌ Failed to create table {table_name}")
                return False

        logger.info("🎉 All tables created successfully!")
        return True

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Creating BigQuery Tables for Legal Document Intelligence Platform")
    print("=" * 70)

    # Check if .env file exists
    env_file = Path(__file__).parent.parent.parent / '.env'
    if not env_file.exists():
        print("❌ .env file not found. Please run the BigQuery setup script first:")
        print("   ./scripts/setup/bigquery_setup.sh")
        return False

    # Load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

    # Create tables
    success = create_tables()

    if success:
        print("\n✅ BigQuery setup completed successfully!")
        print("\n📋 Created tables:")
        print("  - raw_data.legal_documents")
        print("  - processed_data.legal_documents")
        print("  - processed_data.document_embeddings")
        print("\n🚀 You can now start using BigQuery in your application!")
    else:
        print("\n❌ BigQuery setup failed. Please check the logs above.")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
