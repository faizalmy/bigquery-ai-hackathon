#!/usr/bin/env python3
"""
BigQuery Cleanup Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script removes unused tables and datasets to clean up the BigQuery environment.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
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

class BigQueryCleanup:
    """Cleans up unused BigQuery tables and datasets."""

    def __init__(self):
        """Initialize BigQuery cleanup."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']

        # Define what to keep (current working datasets)
        self.keep_datasets = {
            'ai_models',  # For AI models
            'legal_ai_platform_raw_data',  # Main data location
            'legal_ai_platform_processed_data',  # Processed data
            'legal_ai_platform_results',  # Results
            'legal_ai_platform_vector_indexes'  # Vector indexes
        }

        # Define what to remove (old/unused datasets)
        self.remove_datasets = {
            'legal_ai_platform',  # Old dataset with 500 rows
            'processed_data',  # Old processed data
            'raw_data',  # Old raw data
            'temp',  # Temporary dataset
            'functions'  # Empty functions dataset
        }

    def analyze_datasets(self) -> Dict[str, Any]:
        """Analyze all datasets and their usage."""
        try:
            logger.info("Analyzing BigQuery datasets...")

            analysis = {
                'datasets_to_keep': [],
                'datasets_to_remove': [],
                'total_tables': 0,
                'total_rows': 0,
                'total_size_bytes': 0
            }

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # List all datasets
            datasets = list(self.bigquery_client.client.list_datasets())

            for dataset in datasets:
                dataset_id = dataset.dataset_id

                try:
                    # List tables in dataset
                    tables = list(self.bigquery_client.client.list_tables(dataset_id))

                    dataset_info = {
                        'dataset_id': dataset_id,
                        'tables': [],
                        'total_rows': 0,
                        'total_size_bytes': 0,
                        'created': dataset.created
                    }

                    for table in tables:
                        try:
                            table_ref = self.bigquery_client.client.get_table(f'{dataset_id}.{table.table_id}')

                            table_info = {
                                'table_id': table.table_id,
                                'rows': table_ref.num_rows,
                                'size_bytes': table_ref.num_bytes,
                                'created': table_ref.created
                            }

                            dataset_info['tables'].append(table_info)
                            dataset_info['total_rows'] += table_ref.num_rows
                            dataset_info['total_size_bytes'] += table_ref.num_bytes

                            analysis['total_tables'] += 1
                            analysis['total_rows'] += table_ref.num_rows
                            analysis['total_size_bytes'] += table_ref.num_bytes

                        except Exception as e:
                            logger.warning(f"Error getting table info for {dataset_id}.{table.table_id}: {e}")

                    # Categorize dataset
                    if dataset_id in self.keep_datasets:
                        analysis['datasets_to_keep'].append(dataset_info)
                    elif dataset_id in self.remove_datasets:
                        analysis['datasets_to_remove'].append(dataset_info)
                    else:
                        # Unknown dataset - ask user
                        logger.info(f"Unknown dataset: {dataset_id} - will keep for safety")
                        analysis['datasets_to_keep'].append(dataset_info)

                except Exception as e:
                    logger.error(f"Error analyzing dataset {dataset_id}: {e}")

            logger.info(f"Analysis complete: {len(analysis['datasets_to_keep'])} to keep, {len(analysis['datasets_to_remove'])} to remove")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze datasets: {e}")
            raise

    def cleanup_unused_datasets(self, dry_run: bool = True) -> bool:
        """
        Remove unused datasets and tables.

        Args:
            dry_run: If True, only show what would be removed without actually removing

        Returns:
            bool: True if cleanup successful, False otherwise
        """
        try:
            logger.info(f"Starting cleanup (dry_run={dry_run})...")

            # Analyze datasets
            analysis = self.analyze_datasets()

            print(f"\n🧹 BIGQUERY CLEANUP ANALYSIS")
            print("=" * 50)
            print(f"Total datasets: {len(analysis['datasets_to_keep']) + len(analysis['datasets_to_remove'])}")
            print(f"Total tables: {analysis['total_tables']}")
            print(f"Total rows: {analysis['total_rows']:,}")
            print(f"Total size: {analysis['total_size_bytes']:,} bytes")
            print()

            # Show datasets to keep
            print("✅ DATASETS TO KEEP:")
            for dataset in analysis['datasets_to_keep']:
                print(f"  📁 {dataset['dataset_id']}")
                print(f"     Tables: {len(dataset['tables'])}")
                print(f"     Rows: {dataset['total_rows']:,}")
                print(f"     Size: {dataset['total_size_bytes']:,} bytes")
                print()

            # Show datasets to remove
            print("🗑️ DATASETS TO REMOVE:")
            for dataset in analysis['datasets_to_remove']:
                print(f"  📁 {dataset['dataset_id']}")
                print(f"     Tables: {len(dataset['tables'])}")
                print(f"     Rows: {dataset['total_rows']:,}")
                print(f"     Size: {dataset['total_size_bytes']:,} bytes")

                if len(dataset['tables']) > 0:
                    print("     Tables:")
                    for table in dataset['tables']:
                        print(f"       - {table['table_id']} ({table['rows']:,} rows)")
                print()

            if dry_run:
                print("🔍 DRY RUN - No changes made")
                print("Run with dry_run=False to actually remove datasets")
                return True

            # Actually remove datasets
            removed_count = 0
            for dataset in analysis['datasets_to_remove']:
                try:
                    dataset_id = dataset['dataset_id']
                    logger.info(f"Removing dataset: {dataset_id}")

                    # Delete the entire dataset (this removes all tables)
                    self.bigquery_client.client.delete_dataset(
                        dataset_id,
                        delete_contents=True,
                        not_found_ok=True
                    )

                    removed_count += 1
                    print(f"✅ Removed dataset: {dataset_id}")

                except Exception as e:
                    logger.error(f"Failed to remove dataset {dataset_id}: {e}")
                    print(f"❌ Failed to remove dataset: {dataset_id}")

            print(f"\n🎉 Cleanup complete! Removed {removed_count} datasets")
            return True

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False


def main():
    """Main cleanup function."""
    try:
        print("🧹 BigQuery Cleanup Tool")
        print("=" * 40)
        print("This tool will remove unused datasets and tables.")
        print()

        # Initialize cleanup
        cleanup = BigQueryCleanup()

        # First, run dry run to show what would be removed
        print("🔍 Running dry run analysis...")
        if cleanup.cleanup_unused_datasets(dry_run=True):
            print("\n" + "=" * 50)
            response = input("Do you want to proceed with the cleanup? (y/N): ")

            if response.lower() in ['y', 'yes']:
                print("\n🗑️ Proceeding with cleanup...")
                if cleanup.cleanup_unused_datasets(dry_run=False):
                    print("✅ Cleanup completed successfully!")
                    return 0
                else:
                    print("❌ Cleanup failed!")
                    return 1
            else:
                print("❌ Cleanup cancelled by user")
                return 0
        else:
            print("❌ Analysis failed!")
            return 1

    except Exception as e:
        logger.error(f"Cleanup tool failed: {e}")
        print(f"\n❌ Cleanup tool failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
