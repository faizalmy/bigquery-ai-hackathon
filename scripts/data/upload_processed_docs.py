#!/usr/bin/env python3
"""
Upload Processed Documents to BigQuery
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_processed_documents():
    """Upload processed documents to BigQuery."""
    # Load configuration
    config = load_config()
    bq_client = BigQueryClient(config)

    # Load processed documents
    processed_file = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'processed_documents.json'

    if not processed_file.exists():
        logger.error(f"Processed documents file not found: {processed_file}")
        return False

    with open(processed_file, 'r') as f:
        documents = json.load(f)

    logger.info(f"Loaded {len(documents)} processed documents")

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

    # Upload to BigQuery
    project_id = config['bigquery']['project_id']
    table_id = f"{project_id}.processed_data.legal_documents"

    try:
        # Use dataset reference approach
        dataset_ref = bq_client.client.dataset('processed_data')
        table_ref = dataset_ref.table('legal_documents')
        table = bq_client.client.get_table(table_ref)
        logger.info(f"Uploading to table: {table.full_table_id}")

        # Insert data in batches
        batch_size = 50
        total_inserted = 0

        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i + batch_size]
            errors = bq_client.client.insert_rows_json(table, batch)

            if errors:
                logger.error(f"Errors inserting batch {i//batch_size + 1}: {errors}")
            else:
                total_inserted += len(batch)
                logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} documents)")

        logger.info(f"Total documents uploaded: {total_inserted}")
        return total_inserted > 0

    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        return False

if __name__ == "__main__":
    print("📤 Uploading Processed Documents to BigQuery")
    print("=" * 50)

    success = upload_processed_documents()

    if success:
        print("✅ Documents uploaded successfully!")
    else:
        print("❌ Failed to upload documents!")
        sys.exit(1)
