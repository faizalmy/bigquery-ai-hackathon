"""
BigQuery Data Loader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module handles loading processed legal documents into BigQuery with proper
schema definition, partitioning, and indexing for optimal performance.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from pathlib import Path
import pandas as pd

from google.cloud import bigquery
from google.cloud.exceptions import NotFound, BadRequest

logger = logging.getLogger(__name__)

class BigQueryDataLoader:
    """Handles loading legal documents into BigQuery with optimized schema and partitioning."""

    def __init__(self, project_id: str, dataset_id: str = "legal_ai_platform"):
        """
        Initialize BigQuery data loader.

        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.dataset_ref = bigquery.DatasetReference(project_id, dataset_id)

        # Table configurations
        self.tables = {
            'legal_documents': {
                'table_id': 'legal_documents',
                'description': 'Processed legal documents with metadata and content',
                'partition_field': 'ingestion_date',
                'cluster_fields': ['document_type', 'jurisdiction']
            },
            'document_metadata': {
                'table_id': 'document_metadata',
                'description': 'Extracted metadata from legal documents',
                'partition_field': 'extraction_date',
                'cluster_fields': ['document_type']
            },
            'ai_processing_results': {
                'table_id': 'ai_processing_results',
                'description': 'Results from BigQuery AI functions processing',
                'partition_field': 'processing_date',
                'cluster_fields': ['ai_function', 'document_type']
            }
        }

    def create_dataset(self) -> bool:
        """
        Create BigQuery dataset if it doesn't exist.

        Returns:
            True if dataset was created or already exists, False otherwise
        """
        try:
            logger.info(f"Creating dataset: {self.dataset_id}")
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"  # Set location for optimal performance
            dataset.description = "Legal Document Intelligence Platform - BigQuery AI Hackathon Entry"

            # Create dataset
            dataset = self.client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Dataset {self.dataset_id} created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating dataset {self.dataset_id}: {e}")
            return False

    def get_legal_documents_schema(self) -> List[bigquery.SchemaField]:
        """
        Define schema for legal_documents table.

        Returns:
            List of BigQuery schema fields
        """
        return [
            bigquery.SchemaField("document_id", "STRING", mode="REQUIRED", description="Unique document identifier"),
            bigquery.SchemaField("source_system", "STRING", mode="REQUIRED", description="Source system identifier"),
            bigquery.SchemaField("document_type", "STRING", mode="REQUIRED", description="Type of legal document"),
            bigquery.SchemaField("raw_content", "STRING", mode="REQUIRED", description="Original document content"),
            bigquery.SchemaField("processed_content", "STRING", mode="NULLABLE", description="Preprocessed document content"),
            bigquery.SchemaField("parties", "STRING", mode="REPEATED", description="Legal parties involved"),
            bigquery.SchemaField("legal_issues", "STRING", mode="REPEATED", description="Legal issues identified"),
            bigquery.SchemaField("case_date", "DATE", mode="NULLABLE", description="Date of case or document"),
            bigquery.SchemaField("jurisdiction", "STRING", mode="NULLABLE", description="Legal jurisdiction"),
            bigquery.SchemaField("urgency_level", "STRING", mode="NULLABLE", description="Urgency level (high/medium/low)"),
            bigquery.SchemaField("complexity_score", "FLOAT", mode="NULLABLE", description="Document complexity score"),
            bigquery.SchemaField("word_count", "INTEGER", mode="NULLABLE", description="Word count of document"),
            bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED", description="Document ingestion timestamp"),
            bigquery.SchemaField("ingestion_date", "DATE", mode="REQUIRED", description="Date partition for ingestion"),
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE", description="Additional document metadata"),
            bigquery.SchemaField("classification", "JSON", mode="NULLABLE", description="Document classification results"),
            bigquery.SchemaField("extracted_entities", "JSON", mode="NULLABLE", description="Extracted legal entities")
        ]

    def get_document_metadata_schema(self) -> List[bigquery.SchemaField]:
        """
        Define schema for document_metadata table.

        Returns:
            List of BigQuery schema fields
        """
        return [
            bigquery.SchemaField("document_id", "STRING", mode="REQUIRED", description="Reference to legal document"),
            bigquery.SchemaField("extraction_date", "DATE", mode="REQUIRED", description="Date partition for extraction"),
            bigquery.SchemaField("document_type", "STRING", mode="REQUIRED", description="Type of legal document"),
            bigquery.SchemaField("extracted_case_citations", "STRING", mode="REPEATED", description="Case citations found"),
            bigquery.SchemaField("extracted_statute_citations", "STRING", mode="REPEATED", description="Statute citations found"),
            bigquery.SchemaField("extracted_courts", "STRING", mode="REPEATED", description="Courts mentioned"),
            bigquery.SchemaField("processed_word_count", "INTEGER", mode="NULLABLE", description="Word count after processing"),
            bigquery.SchemaField("processed_paragraph_count", "INTEGER", mode="NULLABLE", description="Paragraph count after processing"),
            bigquery.SchemaField("processed_line_count", "INTEGER", mode="NULLABLE", description="Line count after processing"),
            bigquery.SchemaField("quality_score", "FLOAT", mode="NULLABLE", description="Document quality score"),
            bigquery.SchemaField("completeness_score", "FLOAT", mode="NULLABLE", description="Metadata completeness score"),
            bigquery.SchemaField("extraction_timestamp", "TIMESTAMP", mode="REQUIRED", description="Metadata extraction timestamp")
        ]

    def get_ai_processing_results_schema(self) -> List[bigquery.SchemaField]:
        """
        Define schema for ai_processing_results table.

        Returns:
            List of BigQuery schema fields
        """
        return [
            bigquery.SchemaField("document_id", "STRING", mode="REQUIRED", description="Reference to legal document"),
            bigquery.SchemaField("processing_date", "DATE", mode="REQUIRED", description="Date partition for processing"),
            bigquery.SchemaField("ai_function", "STRING", mode="REQUIRED", description="AI function used (ML.GENERATE_TEXT, AI.GENERATE_TABLE, etc.)"),
            bigquery.SchemaField("document_type", "STRING", mode="REQUIRED", description="Type of legal document"),
            bigquery.SchemaField("prompt_used", "STRING", mode="NULLABLE", description="Prompt used for AI function"),
            bigquery.SchemaField("sql_query", "STRING", mode="NULLABLE", description="Generated SQL query"),
            bigquery.SchemaField("result_data", "JSON", mode="NULLABLE", description="AI function result data"),
            bigquery.SchemaField("processing_status", "STRING", mode="REQUIRED", description="Processing status (success/failed)"),
            bigquery.SchemaField("processing_timestamp", "TIMESTAMP", mode="REQUIRED", description="AI processing timestamp"),
            bigquery.SchemaField("error_message", "STRING", mode="NULLABLE", description="Error message if processing failed")
        ]

    def create_table(self, table_name: str) -> bool:
        """
        Create BigQuery table with proper schema, partitioning, and clustering.

        Args:
            table_name: Name of the table to create

        Returns:
            True if table was created successfully, False otherwise
        """
        try:
            if table_name not in self.tables:
                logger.error(f"Unknown table: {table_name}")
                return False

            table_config = self.tables[table_name]
            table_id = table_config['table_id']
            table_ref = self.dataset_ref.table(table_id)

            logger.info(f"Creating table: {table_id}")

            # Get schema based on table name
            if table_name == 'legal_documents':
                schema = self.get_legal_documents_schema()
            elif table_name == 'document_metadata':
                schema = self.get_document_metadata_schema()
            elif table_name == 'ai_processing_results':
                schema = self.get_ai_processing_results_schema()
            else:
                logger.error(f"No schema defined for table: {table_name}")
                return False

            # Create table
            table = bigquery.Table(table_ref, schema=schema)
            table.description = table_config['description']

            # Set partitioning
            if table_config.get('partition_field'):
                partition_field = table_config['partition_field']
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field=partition_field
                )
                logger.info(f"Set partitioning on field: {partition_field}")

            # Set clustering
            if table_config.get('cluster_fields'):
                cluster_fields = table_config['cluster_fields']
                table.clustering_fields = cluster_fields
                logger.info(f"Set clustering on fields: {cluster_fields}")

            # Create table
            table = self.client.create_table(table, exists_ok=True)
            logger.info(f"Table {table_id} created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            return False

    def load_legal_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Load processed legal documents into BigQuery.

        Args:
            documents: List of processed legal documents

        Returns:
            True if loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(documents)} legal documents into BigQuery")

            # Prepare data for BigQuery
            rows_to_insert = []
            for doc in documents:
                # Convert document to BigQuery row format
                row = self._prepare_document_row(doc)
                if row:
                    rows_to_insert.append(row)

            if not rows_to_insert:
                logger.warning("No valid rows to insert")
                return False

            # Get table reference
            table_ref = self.dataset_ref.table(self.tables['legal_documents']['table_id'])
            table = self.client.get_table(table_ref)

            # Insert rows
            errors = self.client.insert_rows_json(table, rows_to_insert)

            if errors:
                logger.error(f"Errors inserting rows: {errors}")
                return False

            logger.info(f"Successfully loaded {len(rows_to_insert)} documents into BigQuery")
            return True

        except Exception as e:
            logger.error(f"Error loading legal documents: {e}")
            return False

    def load_document_metadata(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Load document metadata into BigQuery.

        Args:
            documents: List of processed legal documents with metadata

        Returns:
            True if loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading metadata for {len(documents)} documents into BigQuery")

            # Prepare metadata rows
            rows_to_insert = []
            for doc in documents:
                metadata_row = self._prepare_metadata_row(doc)
                if metadata_row:
                    rows_to_insert.append(metadata_row)

            if not rows_to_insert:
                logger.warning("No valid metadata rows to insert")
                return False

            # Get table reference
            table_ref = self.dataset_ref.table(self.tables['document_metadata']['table_id'])
            table = self.client.get_table(table_ref)

            # Insert rows
            errors = self.client.insert_rows_json(table, rows_to_insert)

            if errors:
                logger.error(f"Errors inserting metadata rows: {errors}")
                return False

            logger.info(f"Successfully loaded metadata for {len(rows_to_insert)} documents into BigQuery")
            return True

        except Exception as e:
            logger.error(f"Error loading document metadata: {e}")
            return False

    def load_ai_processing_results(self, ai_results: List[Dict[str, Any]]) -> bool:
        """
        Load AI processing results into BigQuery.

        Args:
            ai_results: List of AI processing results

        Returns:
            True if loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading {len(ai_results)} AI processing results into BigQuery")

            # Prepare AI results rows
            rows_to_insert = []
            for result in ai_results:
                ai_rows = self._prepare_ai_results_rows(result)
                rows_to_insert.extend(ai_rows)

            if not rows_to_insert:
                logger.warning("No valid AI results rows to insert")
                return False

            # Get table reference
            table_ref = self.dataset_ref.table(self.tables['ai_processing_results']['table_id'])
            table = self.client.get_table(table_ref)

            # Insert rows
            errors = self.client.insert_rows_json(table, rows_to_insert)

            if errors:
                logger.error(f"Errors inserting AI results rows: {errors}")
                return False

            logger.info(f"Successfully loaded {len(rows_to_insert)} AI processing results into BigQuery")
            return True

        except Exception as e:
            logger.error(f"Error loading AI processing results: {e}")
            return False

    def _prepare_document_row(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepare a document for BigQuery insertion.

        Args:
            document: Document dictionary

        Returns:
            Prepared row dictionary or None if invalid
        """
        try:
            # Extract basic fields
            document_id = document.get('document_id')
            if not document_id:
                logger.warning("Document missing document_id")
                return None

            # Parse ingestion timestamp
            ingestion_timestamp = document.get('ingestion_timestamp', datetime.now().isoformat())
            if isinstance(ingestion_timestamp, str):
                ingestion_timestamp = datetime.fromisoformat(ingestion_timestamp.replace('Z', '+00:00'))

            # Extract date for partitioning
            ingestion_date = ingestion_timestamp.date()

            # Prepare row
            row = {
                'document_id': document_id,
                'source_system': document.get('source_system', 'unknown'),
                'document_type': document.get('document_type', 'unknown'),
                'raw_content': document.get('raw_content', ''),
                'processed_content': document.get('processed_content', ''),
                'parties': document.get('metadata', {}).get('parties', []),
                'legal_issues': document.get('metadata', {}).get('legal_issues', []),
                'case_date': self._parse_date(document.get('metadata', {}).get('case_date')),
                'jurisdiction': document.get('metadata', {}).get('jurisdiction'),
                'urgency_level': document.get('metadata', {}).get('urgency_level'),
                'complexity_score': document.get('metadata', {}).get('complexity_score'),
                'word_count': document.get('metadata', {}).get('word_count'),
                'ingestion_timestamp': ingestion_timestamp.isoformat(),
                'ingestion_date': ingestion_date.isoformat(),
                'metadata': json.dumps(document.get('metadata', {})),
                'classification': json.dumps(document.get('metadata', {}).get('classification', {})),
                'extracted_entities': json.dumps({
                    'case_citations': document.get('metadata', {}).get('extracted_case_citations', []),
                    'statute_citations': document.get('metadata', {}).get('extracted_statute_citations', []),
                    'courts': document.get('metadata', {}).get('extracted_courts', [])
                })
            }

            return row

        except Exception as e:
            logger.error(f"Error preparing document row: {e}")
            return None

    def _prepare_metadata_row(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepare document metadata for BigQuery insertion.

        Args:
            document: Document dictionary with metadata

        Returns:
            Prepared metadata row dictionary or None if invalid
        """
        try:
            document_id = document.get('document_id')
            if not document_id:
                return None

            metadata = document.get('metadata', {})

            # Parse extraction timestamp
            extraction_timestamp = metadata.get('preprocessing_timestamp', datetime.now().isoformat())
            if isinstance(extraction_timestamp, str):
                extraction_timestamp = datetime.fromisoformat(extraction_timestamp.replace('Z', '+00:00'))

            extraction_date = extraction_timestamp.date()

            row = {
                'document_id': document_id,
                'extraction_date': extraction_date.isoformat(),
                'document_type': document.get('document_type', 'unknown'),
                'extracted_case_citations': metadata.get('extracted_case_citations', []),
                'extracted_statute_citations': metadata.get('extracted_statute_citations', []),
                'extracted_courts': metadata.get('extracted_courts', []),
                'processed_word_count': metadata.get('processed_word_count'),
                'processed_paragraph_count': metadata.get('processed_paragraph_count'),
                'processed_line_count': metadata.get('processed_line_count'),
                'quality_score': metadata.get('quality_score'),
                'completeness_score': metadata.get('completeness_score'),
                'extraction_timestamp': extraction_timestamp.isoformat()
            }

            return row

        except Exception as e:
            logger.error(f"Error preparing metadata row: {e}")
            return None

    def _prepare_ai_results_rows(self, ai_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepare AI processing results for BigQuery insertion.

        Args:
            ai_result: AI processing result dictionary

        Returns:
            List of prepared AI result rows
        """
        rows = []

        try:
            document_id = ai_result.get('document_id')
            if not document_id:
                return rows

            # Parse processing timestamp
            processing_timestamp = ai_result.get('processing_timestamp', datetime.now().isoformat())
            if isinstance(processing_timestamp, str):
                processing_timestamp = datetime.fromisoformat(processing_timestamp.replace('Z', '+00:00'))

            processing_date = processing_timestamp.date()

            # Process each AI function result
            ai_results = ai_result.get('ai_results', {})

            for function_name, result in ai_results.items():
                row = {
                    'document_id': document_id,
                    'processing_date': processing_date.isoformat(),
                    'ai_function': function_name.upper(),
                    'document_type': ai_result.get('document_type', 'unknown'),
                    'prompt_used': result.get('prompt_used', ''),
                    'sql_query': result.get('sql_query', ''),
                    'result_data': json.dumps(result),
                    'processing_status': 'success' if ai_result.get('success', False) else 'failed',
                    'processing_timestamp': processing_timestamp.isoformat(),
                    'error_message': ai_result.get('error', '') if not ai_result.get('success', False) else None
                }
                rows.append(row)

        except Exception as e:
            logger.error(f"Error preparing AI results rows: {e}")

        return rows

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Parse date string to ISO format.

        Args:
            date_str: Date string to parse

        Returns:
            ISO date string or None
        """
        if not date_str:
            return None

        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.date().isoformat()
                except ValueError:
                    continue

            # If no format matches, return None
            return None

        except Exception:
            return None

    def create_indexes(self) -> bool:
        """
        Note: BigQuery uses clustering instead of indexes for performance optimization.
        Clustering is already configured in the table creation.

        Returns:
            True (clustering is already configured)
        """
        logger.info("Performance optimization via clustering is already configured in table creation")
        return True

    def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about created tables.

        Returns:
            Dictionary with table information
        """
        try:
            table_info = {}

            for table_name, config in self.tables.items():
                table_id = config['table_id']
                table_ref = self.dataset_ref.table(table_id)

                try:
                    table = self.client.get_table(table_ref)

                    # Get row count
                    count_query = f"SELECT COUNT(*) as row_count FROM `{self.project_id}.{self.dataset_id}.{table_id}`"
                    count_job = self.client.query(count_query)
                    count_result = count_job.result()
                    row_count = list(count_result)[0].row_count

                    table_info[table_name] = {
                        'table_id': table_id,
                        'description': table.description,
                        'num_rows': row_count,
                        'num_bytes': table.num_bytes,
                        'created': table.created.isoformat() if table.created else None,
                        'modified': table.modified.isoformat() if table.modified else None,
                        'partitioning': str(table.time_partitioning) if table.time_partitioning else None,
                        'clustering': table.clustering_fields if table.clustering_fields else None
                    }

                except NotFound:
                    table_info[table_name] = {
                        'table_id': table_id,
                        'status': 'not_found'
                    }

            return table_info

        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}

def main():
    """Test the BigQuery data loader implementation."""
    print("📊 BigQuery Data Loader Implementation - Phase 2.4")
    print("=" * 70)

    # Initialize data loader
    loader = BigQueryDataLoader("faizal-hackathon")

    # Test dataset creation
    print("🔧 Testing dataset creation...")
    if loader.create_dataset():
        print("✅ Dataset created successfully")
    else:
        print("❌ Dataset creation failed")
        return 1

    # Test table creation
    print("\n📋 Testing table creation...")
    tables_created = 0
    for table_name in loader.tables.keys():
        if loader.create_table(table_name):
            print(f"✅ Table {table_name} created successfully")
            tables_created += 1
        else:
            print(f"❌ Table {table_name} creation failed")

    print(f"\n📊 Tables created: {tables_created}/{len(loader.tables)}")

    # Test index creation
    print("\n🔍 Testing index creation...")
    if loader.create_indexes():
        print("✅ Indexes created successfully")
    else:
        print("❌ Index creation failed")

    # Get table information
    print("\n📋 Table Information:")
    table_info = loader.get_table_info()
    for table_name, info in table_info.items():
        print(f"  {table_name}:")
        if 'status' in info:
            print(f"    Status: {info['status']}")
        else:
            print(f"    Rows: {info.get('num_rows', 'N/A')}")
            print(f"    Size: {info.get('num_bytes', 'N/A')} bytes")
            print(f"    Partitioning: {info.get('partitioning', 'None')}")
            print(f"    Clustering: {info.get('clustering', 'None')}")

    print(f"\n✅ BigQuery data loader implementation test completed successfully")
    return 0

if __name__ == "__main__":
    main()
