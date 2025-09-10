#!/usr/bin/env python3
"""
Legal Document Processing Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script processes raw legal documents and loads them into BigQuery.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient
from data.preprocessing import LegalDocumentPreprocessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing orchestrator."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the document processor."""
        self.config = config
        self.bq_client = BigQueryClient(config)
        self.preprocessor = LegalDocumentPreprocessor()

        # BigQuery table references
        self.project_id = config['bigquery']['project_id']
        self.raw_table = f"{self.project_id}.raw_data.legal_documents"
        self.processed_table = f"{self.project_id}.processed_data.legal_documents"

    def create_processed_table(self) -> bool:
        """Create the processed data table in BigQuery."""
        try:
            # Create processed data dataset if it doesn't exist
            dataset_id = f"{self.project_id}.processed_data"
            try:
                self.bq_client.client.get_dataset(dataset_id)
                logger.info(f"Dataset {dataset_id} already exists")
            except Exception:
                self.bq_client.client.create_dataset(dataset_id)
                logger.info(f"Created dataset {dataset_id}")

            # Create processed documents table
            table_schema = [
                {"name": "document_id", "type": "STRING", "mode": "REQUIRED"},
                {"name": "source_system", "type": "STRING", "mode": "NULLABLE"},
                {"name": "document_type", "type": "STRING", "mode": "NULLABLE"},
                {"name": "cleaned_content", "type": "STRING", "mode": "NULLABLE"},
                {"name": "extracted_metadata", "type": "JSON", "mode": "NULLABLE"},
                {"name": "quality_score", "type": "FLOAT64", "mode": "NULLABLE"},
                {"name": "processed_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
                {"name": "original_metadata", "type": "JSON", "mode": "NULLABLE"}
            ]

            table_ref = self.bq_client.client.dataset('processed_data').table('legal_documents')

            try:
                self.bq_client.client.get_table(table_ref)
                logger.info(f"Table {self.processed_table} already exists")
                return True
            except Exception:
                table = self.bq_client.client.create_table(
                    self.bq_client.client.table(table_ref, schema=table_schema)
                )
                logger.info(f"Created table {self.processed_table}")
                return True

        except Exception as e:
            logger.error(f"Error creating processed table: {e}")
            return False

    def load_raw_documents(self) -> List[Dict[str, Any]]:
        """Load raw documents from BigQuery."""
        try:
            query = f"""
            SELECT
                document_id,
                source_system,
                document_type,
                raw_content,
                metadata,
                ingestion_timestamp
            FROM `{self.raw_table}`
            WHERE raw_content IS NOT NULL
            AND LENGTH(raw_content) > 100
            ORDER BY ingestion_timestamp DESC
            """

            result = self.bq_client.client.query(query).result()
            documents = []

            for row in result:
                # Handle metadata - it might already be a dict or a JSON string
                metadata = row.metadata
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}
                elif metadata is None:
                    metadata = {}

                doc = {
                    'document_id': row.document_id,
                    'source_system': row.source_system,
                    'document_type': row.document_type,
                    'raw_content': row.raw_content,
                    'metadata': metadata,
                    'ingestion_timestamp': row.ingestion_timestamp.isoformat()
                }
                documents.append(doc)

            logger.info(f"Loaded {len(documents)} raw documents from BigQuery")
            return documents

        except Exception as e:
            logger.error(f"Error loading raw documents: {e}")
            return []

    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process documents using the preprocessing pipeline."""
        logger.info(f"Processing {len(documents)} documents...")

        processed_documents = self.preprocessor.preprocess_batch(documents)

        # Filter by quality score
        high_quality_docs = [
            doc for doc in processed_documents
            if doc['quality_score'] >= 0.5
        ]

        logger.info(f"High quality documents: {len(high_quality_docs)}/{len(processed_documents)}")
        return high_quality_docs

    def upload_processed_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload processed documents to BigQuery."""
        try:
            if not documents:
                logger.warning("No documents to upload")
                return False

            # Convert to BigQuery format
            rows_to_insert = []
            for doc in documents:
                row = {
                    'document_id': doc['document_id'],
                    'source_system': doc['source_system'],
                    'document_type': doc['document_type'],
                    'cleaned_content': doc['cleaned_content'],
                    'extracted_metadata': json.dumps(doc['extracted_metadata']),
                    'quality_score': doc['quality_score'],
                    'processed_timestamp': doc['processed_timestamp'],
                    'original_metadata': json.dumps(doc['original_metadata'])
                }
                rows_to_insert.append(row)

            # Get table reference
            table_ref = self.bq_client.client.get_table(self.processed_table)
            logger.info(f"Using table: {table_ref.full_table_id}")

            # Insert data in batches
            batch_size = 100
            total_inserted = 0

            for i in range(0, len(rows_to_insert), batch_size):
                batch = rows_to_insert[i:i + batch_size]
                errors = self.bq_client.client.insert_rows_json(table_ref, batch)

                if errors:
                    logger.error(f"Errors inserting batch {i//batch_size + 1}: {errors}")
                else:
                    total_inserted += len(batch)
                    logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} documents)")

            logger.info(f"Total documents uploaded: {total_inserted}")
            return total_inserted > 0

        except Exception as e:
            logger.error(f"Error uploading processed documents: {e}")
            return False

    def save_processed_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Save processed documents to local file."""
        try:
            output_file = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'processed_documents.json'
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(documents, f, indent=2)

            logger.info(f"Processed documents saved to: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Error saving processed documents: {e}")
            return ""

    def run_processing_pipeline(self) -> Dict[str, Any]:
        """Run the complete document processing pipeline."""
        logger.info("🚀 Starting Document Processing Pipeline")
        logger.info("=" * 60)

        results = {
            'start_time': datetime.now().isoformat(),
            'raw_documents_loaded': 0,
            'documents_processed': 0,
            'high_quality_documents': 0,
            'documents_uploaded': 0,
            'success': False,
            'errors': []
        }

        try:
            # Step 1: Create processed table
            logger.info("📋 Creating processed data table...")
            if not self.create_processed_table():
                results['errors'].append("Failed to create processed table")
                return results

            # Step 2: Load raw documents
            logger.info("📥 Loading raw documents from BigQuery...")
            raw_documents = self.load_raw_documents()
            results['raw_documents_loaded'] = len(raw_documents)

            if not raw_documents:
                results['errors'].append("No raw documents found")
                return results

            # Step 3: Process documents
            logger.info("🔧 Processing documents...")
            processed_documents = self.process_documents(raw_documents)
            results['documents_processed'] = len(processed_documents)
            results['high_quality_documents'] = len(processed_documents)

            # Step 4: Upload to BigQuery
            logger.info("📤 Uploading processed documents to BigQuery...")
            upload_success = self.upload_processed_documents(processed_documents)
            if upload_success:
                results['documents_uploaded'] = len(processed_documents)

            # Step 5: Save locally
            logger.info("💾 Saving processed documents locally...")
            local_file = self.save_processed_documents(processed_documents)

            results['end_time'] = datetime.now().isoformat()
            results['success'] = upload_success
            results['local_file'] = local_file

        except Exception as e:
            error_msg = f"Pipeline error: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        # Print summary
        self.print_summary(results)
        return results

    def print_summary(self, results: Dict[str, Any]):
        """Print processing summary."""
        print("\n📊 Document Processing Summary")
        print("=" * 50)
        print(f"Raw documents loaded: {results['raw_documents_loaded']}")
        print(f"Documents processed: {results['documents_processed']}")
        print(f"High quality documents: {results['high_quality_documents']}")
        print(f"Documents uploaded: {results['documents_uploaded']}")
        print(f"Success: {'✅' if results['success'] else '❌'}")

        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   - {error}")

        if results.get('local_file'):
            print(f"\n💾 Local file: {results['local_file']}")

def main():
    """Main function to run document processing."""
    print("🔧 Legal Document Processing Pipeline")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize processor
    processor = DocumentProcessor(config)

    # Run processing pipeline
    results = processor.run_processing_pipeline()

    if results['success']:
        print("\n✅ Document processing completed successfully!")
    else:
        print("\n❌ Document processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
