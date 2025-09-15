#!/usr/bin/env python3
"""
Legal Document Embedding Pipeline
BigQuery AI Legal Document Intelligence Platform

This module provides comprehensive embedding preparation for all legal documents
using BigQuery AI functions (ML.GENERATE_EMBEDDING and VECTOR_SEARCH).
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bigquery_client import BigQueryClient
from bigquery_ai_functions import BigQueryAIFunctions

logger = logging.getLogger(__name__)

class LegalDocumentEmbeddingPipeline:
    """
    Comprehensive embedding pipeline for legal documents using BigQuery AI.

    This class handles:
    1. Batch embedding generation for all documents
    2. Embedding storage and management
    3. Vector search preparation
    4. Performance optimization
    """

    def __init__(self):
        """Initialize the embedding pipeline."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']
        self.ai_functions = BigQueryAIFunctions()

        # Pipeline configuration
        self.batch_size = 100  # Process documents in batches
        self.embedding_table = f"{self.project_id}.legal_ai_platform_vector_indexes.document_embeddings"
        self.source_table = f"{self.project_id}.legal_ai_platform_raw_data.legal_documents"

    def check_embedding_status(self) -> Dict[str, Any]:
        """
        Check current status of embeddings in the database.

        Returns:
            Dict containing embedding status information
        """
        try:
            logger.info("Checking embedding status...")

            # Check total documents
            total_query = f"""
            SELECT COUNT(*) as total_documents
            FROM `{self.source_table}`
            WHERE content IS NOT NULL
            """
            total_result = self.bigquery_client.execute_query(total_query)
            total_documents = list(total_result)[0].total_documents

            # Check existing embeddings
            embedding_query = f"""
            SELECT
                COUNT(*) as embedded_documents,
                COUNT(DISTINCT document_id) as unique_documents,
                MIN(created_at) as first_embedding,
                MAX(created_at) as last_embedding
            FROM `{self.embedding_table}`
            WHERE embedding IS NOT NULL
            """
            embedding_result = self.bigquery_client.execute_query(embedding_query)
            embedding_data = list(embedding_result)[0]

            # Check document types
            type_query = f"""
            SELECT
                document_type,
                COUNT(*) as count
            FROM `{self.source_table}`
            WHERE content IS NOT NULL
            GROUP BY document_type
            ORDER BY count DESC
            """
            type_result = self.bigquery_client.execute_query(type_query)
            document_types = {row.document_type: row.count for row in type_result}

            status = {
                'total_documents': total_documents,
                'embedded_documents': embedding_data.embedded_documents,
                'unique_embedded_documents': embedding_data.unique_documents,
                'embedding_coverage': (embedding_data.embedded_documents / total_documents * 100) if total_documents > 0 else 0,
                'document_types': document_types,
                'first_embedding': embedding_data.first_embedding.isoformat() if embedding_data.first_embedding else None,
                'last_embedding': embedding_data.last_embedding.isoformat() if embedding_data.last_embedding else None,
                'needs_embedding': total_documents - embedding_data.embedded_documents
            }

            logger.info(f"Embedding status: {status['embedded_documents']}/{status['total_documents']} documents embedded ({status['embedding_coverage']:.1f}%)")

            return status

        except Exception as e:
            logger.error(f"Failed to check embedding status: {e}")
            raise

    def generate_embeddings_batch(self, batch_size: int = 100, document_type: str = None) -> Dict[str, Any]:
        """
        Generate embeddings for a batch of documents.

        Args:
            batch_size: Number of documents to process in this batch
            document_type: Filter by document type (optional)

        Returns:
            Dict containing batch processing results
        """
        try:
            logger.info(f"Generating embeddings for batch of {batch_size} documents...")

            # Build WHERE clause
            where_clause = "WHERE content IS NOT NULL"
            if document_type:
                where_clause += f" AND document_type = '{document_type}'"

            # Check how many documents need embedding
            check_query = f"""
            SELECT COUNT(*) as documents_to_process
            FROM `{self.source_table}` s
            LEFT JOIN `{self.embedding_table}` e ON s.document_id = e.document_id
            {where_clause}
            AND e.document_id IS NULL
            """
            check_result = self.bigquery_client.execute_query(check_query)
            documents_to_process = list(check_result)[0].documents_to_process

            if documents_to_process == 0:
                logger.info("No documents need embedding in this batch")
                return {
                    'status': 'completed',
                    'documents_processed': 0,
                    'message': 'All documents already have embeddings'
                }

            # Limit batch size to available documents
            actual_batch_size = min(batch_size, documents_to_process)
            logger.info(f"Processing {actual_batch_size} documents (out of {documents_to_process} available)")

            # Generate embeddings for documents that don't have them
            embedding_query = f"""
            INSERT INTO `{self.embedding_table}` (
                document_id,
                embedding,
                model_name,
                model_version,
                created_at
            )
            SELECT
                document_id,
                ml_generate_embedding_result AS embedding,
                'text-embedding-005' AS model_name,
                '1.0' AS model_version,
                CURRENT_TIMESTAMP() AS created_at
            FROM ML.GENERATE_EMBEDDING(
                MODEL `{self.project_id}.ai_models.text_embedding`,
                (
                    SELECT
                        document_id,
                        content
                    FROM `{self.source_table}` s
                    LEFT JOIN `{self.embedding_table}` e ON s.document_id = e.document_id
                    {where_clause}
                    AND e.document_id IS NULL
                    LIMIT {actual_batch_size}
                )
            )
            WHERE ml_generate_embedding_status = ''
            """

            # Execute the embedding generation
            self.bigquery_client.execute_query(embedding_query)

            # Verify the results
            verify_query = f"""
            SELECT COUNT(*) as new_embeddings
            FROM `{self.embedding_table}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE)
            """
            verify_result = self.bigquery_client.execute_query(verify_query)
            new_embeddings = list(verify_result)[0].new_embeddings

            logger.info(f"Successfully generated {new_embeddings} new embeddings")

            return {
                'status': 'success',
                'documents_processed': new_embeddings,
                'batch_size': actual_batch_size,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate embeddings batch: {e}")
            raise

    def generate_all_embeddings(self, batch_size: int = 100, document_type: str = None) -> Dict[str, Any]:
        """
        Generate embeddings for all documents that don't have them.

        Args:
            batch_size: Number of documents to process per batch
            document_type: Filter by document type (optional)

        Returns:
            Dict containing complete processing results
        """
        try:
            logger.info("Starting complete embedding generation process...")

            # Check initial status
            initial_status = self.check_embedding_status()
            total_needed = initial_status['needs_embedding']

            if total_needed == 0:
                logger.info("All documents already have embeddings")
                return {
                    'status': 'completed',
                    'total_processed': 0,
                    'message': 'All documents already have embeddings'
                }

            logger.info(f"Need to generate embeddings for {total_needed} documents")

            # Process in batches
            total_processed = 0
            batch_count = 0

            while total_processed < total_needed:
                batch_count += 1
                logger.info(f"Processing batch {batch_count}...")

                batch_result = self.generate_embeddings_batch(batch_size, document_type)

                if batch_result['status'] == 'completed':
                    break

                total_processed += batch_result['documents_processed']
                logger.info(f"Batch {batch_count} completed: {batch_result['documents_processed']} documents processed")

                # Check if we're done
                current_status = self.check_embedding_status()
                if current_status['needs_embedding'] == 0:
                    break

            # Final status check
            final_status = self.check_embedding_status()

            logger.info(f"Embedding generation completed: {total_processed} documents processed")

            return {
                'status': 'completed',
                'total_processed': total_processed,
                'batches_processed': batch_count,
                'final_coverage': final_status['embedding_coverage'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate all embeddings: {e}")
            raise

    def optimize_embeddings_table(self) -> Dict[str, Any]:
        """
        Optimize the embeddings table for better performance.

        Returns:
            Dict containing optimization results
        """
        try:
            logger.info("Optimizing embeddings table...")

            # Check table size and performance
            stats_query = f"""
            SELECT
                COUNT(*) as total_rows,
                COUNT(DISTINCT document_id) as unique_documents,
                AVG(ARRAY_LENGTH(embedding)) as avg_embedding_length,
                MIN(created_at) as oldest_embedding,
                MAX(created_at) as newest_embedding
            FROM `{self.embedding_table}`
            """
            stats_result = self.bigquery_client.execute_query(stats_query)
            stats = list(stats_result)[0]

            # Check for duplicates
            duplicate_query = f"""
            SELECT
                document_id,
                COUNT(*) as duplicate_count
            FROM `{self.embedding_table}`
            GROUP BY document_id
            HAVING COUNT(*) > 1
            """
            duplicate_result = self.bigquery_client.execute_query(duplicate_query)
            duplicates = list(duplicate_result)

            # Remove duplicates if any
            if duplicates:
                logger.info(f"Found {len(duplicates)} duplicate document IDs, removing...")
                dedupe_query = f"""
                CREATE OR REPLACE TABLE `{self.embedding_table}_deduped` AS
                SELECT
                    document_id,
                    embedding,
                    model_name,
                    model_version,
                    MAX(created_at) as created_at
                FROM `{self.embedding_table}`
                GROUP BY document_id, embedding, model_name, model_version
                """
                self.bigquery_client.execute_query(dedupe_query)

                # Replace original table
                replace_query = f"""
                DROP TABLE `{self.embedding_table}`
                """
                self.bigquery_client.execute_query(replace_query)

                rename_query = f"""
                ALTER TABLE `{self.embedding_table}_deduped`
                RENAME TO `{self.embedding_table.split('.')[-1]}`
                """
                self.bigquery_client.execute_query(rename_query)

            optimization_result = {
                'status': 'completed',
                'total_rows': stats.total_rows,
                'unique_documents': stats.unique_documents,
                'avg_embedding_length': stats.avg_embedding_length,
                'duplicates_removed': len(duplicates),
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"Table optimization completed: {stats.total_rows} rows, {stats.unique_documents} unique documents")

            return optimization_result

        except Exception as e:
            logger.error(f"Failed to optimize embeddings table: {e}")
            raise

    def test_vector_search(self, test_queries: List[str] = None) -> Dict[str, Any]:
        """
        Test vector search functionality with sample queries.

        Args:
            test_queries: List of test queries (optional)

        Returns:
            Dict containing test results
        """
        try:
            logger.info("Testing vector search functionality...")

            if test_queries is None:
                test_queries = [
                    "legal contract dispute",
                    "court case settlement",
                    "criminal law violation",
                    "civil rights violation",
                    "property law dispute"
                ]

            test_results = []

            for query in test_queries:
                logger.info(f"Testing query: '{query}'")

                # Use the AI functions vector search
                search_result = self.ai_functions.vector_search(query, limit=5)

                test_results.append({
                    'query': query,
                    'results_found': search_result['total_results'],
                    'top_results': [
                        {
                            'document_id': result['document_id'],
                            'similarity_distance': result['similarity_distance']
                        }
                        for result in search_result['results'][:3]
                    ]
                })

            logger.info("Vector search testing completed")

            return {
                'status': 'completed',
                'test_queries': len(test_queries),
                'results': test_results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to test vector search: {e}")
            raise

    def run_complete_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete embedding preparation pipeline.

        Returns:
            Dict containing complete pipeline results
        """
        try:
            logger.info("Starting complete embedding preparation pipeline...")

            pipeline_results = {
                'start_time': datetime.now().isoformat(),
                'steps': []
            }

            # Step 1: Check initial status
            logger.info("Step 1: Checking initial embedding status...")
            initial_status = self.check_embedding_status()
            pipeline_results['steps'].append({
                'step': 'initial_status',
                'result': initial_status
            })

            # Step 2: Generate all embeddings
            logger.info("Step 2: Generating embeddings for all documents...")
            embedding_result = self.generate_all_embeddings(batch_size=100)
            pipeline_results['steps'].append({
                'step': 'embedding_generation',
                'result': embedding_result
            })

            # Step 3: Optimize table
            logger.info("Step 3: Optimizing embeddings table...")
            optimization_result = self.optimize_embeddings_table()
            pipeline_results['steps'].append({
                'step': 'table_optimization',
                'result': optimization_result
            })

            # Step 4: Test vector search
            logger.info("Step 4: Testing vector search functionality...")
            test_result = self.test_vector_search()
            pipeline_results['steps'].append({
                'step': 'vector_search_test',
                'result': test_result
            })

            # Final status check
            final_status = self.check_embedding_status()
            pipeline_results['final_status'] = final_status
            pipeline_results['end_time'] = datetime.now().isoformat()

            logger.info("Complete embedding preparation pipeline finished successfully")

            return pipeline_results

        except Exception as e:
            logger.error(f"Failed to run complete pipeline: {e}")
            raise


def main():
    """Main execution function for the embedding pipeline."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        print("🚀 Legal Document Embedding Pipeline")
        print("=" * 50)

        # Initialize pipeline
        pipeline = LegalDocumentEmbeddingPipeline()

        # Run complete pipeline
        results = pipeline.run_complete_pipeline()

        # Print summary
        print("\n📊 Pipeline Results Summary:")
        print(f"Final Coverage: {results['final_status']['embedding_coverage']:.1f}%")
        print(f"Total Documents: {results['final_status']['total_documents']}")
        print(f"Embedded Documents: {results['final_status']['embedded_documents']}")
        print(f"Processing Time: {results['start_time']} to {results['end_time']}")

        print("\n✅ Embedding preparation completed successfully!")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
