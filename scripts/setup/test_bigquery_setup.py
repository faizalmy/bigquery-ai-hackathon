#!/usr/bin/env python3
"""
BigQuery Setup Test Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests the BigQuery setup and connection.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_bigquery_setup():
    """Test BigQuery setup and connection."""
    print("🧪 Testing BigQuery Setup")
    print("=" * 40)

    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded configuration for environment: {config.get('environment', 'development')}")

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Test 1: Connection test
        print("1️⃣ Testing BigQuery connection...")
        if bq_client.test_connection():
            print("   ✅ Connection successful")
        else:
            print("   ❌ Connection failed")
            return False

        # Test 2: Get project info
        print("2️⃣ Getting project information...")
        project_info = bq_client.get_project_info()
        if project_info:
            print(f"   ✅ Project ID: {project_info.get('project_id')}")
            print(f"   ✅ Project Name: {project_info.get('friendly_name')}")
            print(f"   ✅ Location: {project_info.get('location')}")
        else:
            print("   ❌ Failed to get project info")
            return False

        # Test 3: List datasets
        print("3️⃣ Listing datasets...")
        datasets = bq_client.list_datasets()
        if datasets:
            print(f"   ✅ Found {len(datasets)} datasets:")
            for dataset in datasets:
                print(f"      - {dataset}")
        else:
            print("   ⚠️  No datasets found (this is normal for a new project)")

        # Test 4: Test query execution
        print("4️⃣ Testing query execution...")
        test_query = """
        SELECT
            'BigQuery setup test' as test_message,
            CURRENT_TIMESTAMP() as test_timestamp,
            42 as test_number
        """

        job = bq_client.execute_query(test_query)
        if job:
            print("   ✅ Query executed successfully")
            # Get results
            for row in job.result():
                print(f"      - Message: {row.test_message}")
                print(f"      - Timestamp: {row.test_timestamp}")
                print(f"      - Number: {row.test_number}")
        else:
            print("   ❌ Query execution failed")
            return False

        print("\n🎉 All tests passed! BigQuery setup is working correctly.")
        return True

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        print(f"\n❌ Test failed: {e}")
        return False

def main():
    """Main function."""
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

    # Run tests
    success = test_bigquery_setup()

    if success:
        print("\n✅ BigQuery setup verification completed successfully!")
        print("\n🚀 You're ready to start using BigQuery in your application!")
    else:
        print("\n❌ BigQuery setup verification failed.")
        print("Please check your configuration and try again.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
