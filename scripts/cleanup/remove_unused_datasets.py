#!/usr/bin/env python3
"""
Remove Unused BigQuery Datasets
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script removes unused datasets to clean up the BigQuery environment.
"""

import sys
from google.cloud import bigquery

def remove_unused_datasets():
    """Remove unused BigQuery datasets."""
    try:
        print("🧹 REMOVING UNUSED BIGQUERY DATASETS")
        print("=" * 50)
        print()

        # Initialize client
        client = bigquery.Client(project='faizal-hackathon')

        # Datasets to remove (old/unused)
        datasets_to_remove = [
            'legal_ai_platform',  # Old dataset with 2,500 rows
            'processed_data',     # Old processed data with 170 rows
            'raw_data',           # Old raw data with 138 rows
            'temp',               # Empty temporary dataset
            'functions'           # Empty functions dataset
        ]

        removed_count = 0

        for dataset_id in datasets_to_remove:
            try:
                print(f"🗑️ Removing dataset: {dataset_id}")

                # Delete the entire dataset (this removes all tables)
                client.delete_dataset(
                    dataset_id,
                    delete_contents=True,
                    not_found_ok=True
                )

                removed_count += 1
                print(f"✅ Successfully removed: {dataset_id}")

            except Exception as e:
                print(f"❌ Failed to remove {dataset_id}: {e}")

        print()
        print(f"🎉 Cleanup complete! Removed {removed_count} datasets")
        print()
        print("✅ REMAINING DATASETS:")
        print("  - ai_models (for AI models)")
        print("  - legal_ai_platform_raw_data (main data location)")
        print("  - legal_ai_platform_processed_data (processed data)")
        print("  - legal_ai_platform_results (results)")
        print("  - legal_ai_platform_vector_indexes (vector indexes)")

        return True

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def main():
    """Main function."""
    try:
        print("This will remove the following unused datasets:")
        print("  - legal_ai_platform (2,500 rows)")
        print("  - processed_data (170 rows)")
        print("  - raw_data (138 rows)")
        print("  - temp (empty)")
        print("  - functions (empty)")
        print()

        response = input("Do you want to proceed? (y/N): ")

        if response.lower() in ['y', 'yes']:
            if remove_unused_datasets():
                print("\n✅ Cleanup completed successfully!")
                return 0
            else:
                print("\n❌ Cleanup failed!")
                return 1
        else:
            print("\n❌ Cleanup cancelled")
            return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
