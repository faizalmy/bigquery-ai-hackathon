#!/usr/bin/env python3
"""
Legal Data Loading Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script loads processed legal documents into BigQuery tables
for Track 1 AI function implementation.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from google.cloud import bigquery

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_client import BigQueryClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LegalDataLoader:
    """Loads legal documents into BigQuery tables."""

    def __init__(self):
        """Initialize legal data loader."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']
        self.loading_stats = {
            "total_documents": 0,
            "loaded_documents": 0,
            "failed_documents": 0,
            "start_time": None,
            "end_time": None
        }

    def load_legal_documents(self) -> bool:
        """
        Load processed legal documents into BigQuery.

        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            logger.info("Starting legal document loading to BigQuery...")
            self.loading_stats["start_time"] = datetime.now()

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                logger.error("Failed to connect to BigQuery")
                return False

            # Load processed documents
            processed_file = Path("data/processed/processed_hf_legal_documents.json")
            if not processed_file.exists():
                logger.error(f"Processed data file not found: {processed_file}")
                return False

            # Load and process documents
            with open(processed_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)

            logger.info(f"Loading {len(documents)} legal documents...")
            self.loading_stats["total_documents"] = len(documents)

            # Load documents in batches
            success = self._load_documents_in_batches(documents)

            self.loading_stats["end_time"] = datetime.now()

            if success:
                logger.info("✅ Legal documents loaded successfully!")
                self._generate_loading_report()
                return True
            else:
                logger.error("❌ Failed to load legal documents")
                return False

        except Exception as e:
            logger.error(f"Failed to load legal documents: {e}")
            return False

    def _load_documents_in_batches(self, documents: List[Dict]) -> bool:
        """Load documents in batches to BigQuery."""
        try:
            batch_size = 100
            total_batches = (len(documents) + batch_size - 1) // batch_size

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                logger.info(f"Loading batch {batch_num}/{total_batches} ({len(batch)} documents)...")

                if self._load_document_batch(batch):
                    self.loading_stats["loaded_documents"] += len(batch)
                    logger.info(f"✅ Batch {batch_num} loaded successfully")
                else:
                    self.loading_stats["failed_documents"] += len(batch)
                    logger.error(f"❌ Batch {batch_num} failed")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to load documents in batches: {e}")
            return False

    def _load_document_batch(self, documents: List[Dict]) -> bool:
        """Load a batch of documents to BigQuery."""
        try:
            # Prepare data for BigQuery
            rows = []
            for doc in documents:
                row = self._prepare_document_row(doc)
                if row:
                    rows.append(row)

            if not rows:
                logger.warning("No valid rows to insert")
                return False

            # Insert into BigQuery
            table_id = f"{self.project_id}.legal_ai_platform_raw_data.legal_documents"

            # Insert rows directly
            table = self.bigquery_client.client.get_table(table_id)

            # Convert rows to BigQuery format
            bq_rows = []
            for row in rows:
                bq_row = {
                    'document_id': row['document_id'],
                    'content': row['content'],
                    'document_type': row['document_type'],
                    'metadata': None,  # Skip JSON for now
                    'file_path': row['file_path'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                bq_rows.append(bq_row)

            # Insert rows
            errors = self.bigquery_client.client.insert_rows(table, bq_rows)

            if errors:
                raise Exception(f"Insert errors: {errors}")

            logger.info(f"Loaded {len(rows)} documents to {table_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to load document batch: {e}")
            return False

    def _prepare_document_row(self, doc: Dict) -> Optional[Dict]:
        """Prepare a document for BigQuery insertion."""
        try:
            # Extract required fields
            document_id = doc.get('document_id', '')
            content = doc.get('content', '')
            document_type = doc.get('document_type', '')
            metadata = doc.get('metadata', {})
            created_at = doc.get('created_at', datetime.now().isoformat())
            updated_at = doc.get('updated_at', datetime.now().isoformat())

            # Validate required fields
            if not document_id or not content or not document_type:
                logger.warning(f"Skipping document with missing required fields: {document_id}")
                return None

            # Prepare row (simplified for initial load)
            row = {
                'document_id': document_id,
                'content': content,
                'document_type': document_type,
                'metadata': None,  # Skip JSON field for now
                'file_path': metadata.get('source_dataset', 'HFforLegal/case-law'),
                'created_at': pd.to_datetime(created_at),
                'updated_at': pd.to_datetime(updated_at)
            }

            return row

        except Exception as e:
            logger.error(f"Failed to prepare document row: {e}")
            return None

    def _generate_loading_report(self) -> None:
        """Generate loading report."""
        try:
            duration = (self.loading_stats["end_time"] - self.loading_stats["start_time"]).total_seconds()

            report = {
                "timestamp": datetime.now().isoformat(),
                "loading_stats": self.loading_stats,
                "duration_seconds": duration,
                "success_rate": (self.loading_stats["loaded_documents"] / max(self.loading_stats["total_documents"], 1)) * 100,
                "table_info": {
                    "project_id": self.project_id,
                    "dataset": "legal_ai_platform_raw_data",
                    "table": "legal_documents"
                }
            }

            # Save report
            report_file = Path("data/processed/legal_data_loading_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"Loading report saved to: {report_file}")

        except Exception as e:
            logger.error(f"Failed to generate loading report: {e}")

    def validate_loaded_data(self) -> bool:
        """Validate that data was loaded correctly."""
        try:
            logger.info("Validating loaded data...")

            # Query loaded data
            query = f"""
            SELECT
                COUNT(*) as total_documents,
                COUNT(DISTINCT document_type) as document_types,
                AVG(LENGTH(content)) as avg_content_length
            FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
            """

            result = self.bigquery_client.execute_query(query)

            # Get results
            for row in result:
                total_docs = row.total_documents
                doc_types = row.document_types
                avg_length = row.avg_content_length

                logger.info(f"✅ Validation Results:")
                logger.info(f"   Total documents: {total_docs}")
                logger.info(f"   Document types: {doc_types}")
                logger.info(f"   Average content length: {avg_length:.0f} characters")

                if total_docs > 0:
                    logger.info("✅ Data validation passed")
                    return True
                else:
                    logger.error("❌ No documents found in BigQuery")
                    return False

            return False

        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False


def main():
    """Main execution function."""
    try:
        print("📊 Legal Data Loader")
        print("=" * 40)
        print("Loading processed legal documents to BigQuery...")

        # Initialize loader
        loader = LegalDataLoader()

        # Load documents
        if loader.load_legal_documents():
            print("✅ Legal documents loaded successfully!")

            # Validate loaded data
            if loader.validate_loaded_data():
                print("✅ Data validation passed!")

                # Print statistics
                stats = loader.loading_stats
                print(f"\n📊 Loading Statistics:")
                print(f"  Total Documents: {stats['total_documents']}")
                print(f"  Loaded: {stats['loaded_documents']}")
                print(f"  Failed: {stats['failed_documents']}")
                print(f"  Success Rate: {(stats['loaded_documents'] / max(stats['total_documents'], 1)) * 100:.1f}%")

                return 0
            else:
                print("❌ Data validation failed")
                return 1
        else:
            print("❌ Failed to load legal documents")
            return 1

    except Exception as e:
        logger.error(f"Loading script failed: {e}")
        print(f"\n❌ Loading script failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
