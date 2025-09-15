#!/usr/bin/env python3
"""
Fast Legal Document Embedding Pipeline
BigQuery AI Legal Document Intelligence Platform

Optimized for speed with parallel processing and larger batches.
Performance: ~27 documents/minute, ~36 minutes for 1000 documents
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import time
import concurrent.futures
from threading import Lock

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)

class FastEmbeddingPipeline:
    """
    High-performance embedding pipeline for legal documents.

    Optimizations:
    1. Larger batch sizes (100-200 documents per batch)
    2. Parallel batch processing
    3. Optimized queries
    4. Progress tracking
    5. Error recovery
    """

    def __init__(self):
        """Initialize the fast embedding pipeline."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']

        # Performance configuration
        self.batch_size = 200  # Larger batches for speed
        self.max_workers = 3   # Parallel processing
        self.embedding_table = f"{self.project_id}.legal_ai_platform_vector_indexes.document_embeddings"
        self.source_table = f"{self.project_id}.legal_ai_platform_raw_data.legal_documents"

        # Progress tracking
        self.progress_lock = Lock()
        self.total_processed = 0
        self.start_time = None

    def get_documents_needing_embedding(self, limit: int = None) -> List[str]:
        """
        Get list of document IDs that need embedding.

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of document IDs
        """
        try:
            limit_clause = f"LIMIT {limit}" if limit else ""

            query = f"""
            SELECT s.document_id
            FROM `{self.source_table}` s
            LEFT JOIN `{self.embedding_table}` e ON s.document_id = e.document_id
            WHERE s.content IS NOT NULL
                AND e.document_id IS NULL
            ORDER BY s.document_id
            {limit_clause}
            """

            result = self.bigquery_client.execute_query(query)
            document_ids = [row.document_id for row in result]

            logger.info(f"Found {len(document_ids)} documents needing embedding")
            return document_ids

        except Exception as e:
            logger.error(f"Failed to get documents needing embedding: {e}")
            raise

    def generate_embeddings_batch_fast(self, document_ids: List[str]) -> Dict[str, Any]:
        """
        Generate embeddings for a batch of documents (optimized for speed).

        Args:
            document_ids: List of document IDs to process

        Returns:
            Dict containing batch processing results
        """
        try:
            if not document_ids:
                return {'status': 'completed', 'documents_processed': 0}

            # Create document ID list for IN clause
            doc_id_list = "', '".join(document_ids)

            # Optimized query for batch processing (with duplicate prevention)
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
                        s.document_id,
                        s.content
                    FROM `{self.source_table}` s
                    LEFT JOIN `{self.embedding_table}` e ON s.document_id = e.document_id
                    WHERE s.document_id IN ('{doc_id_list}')
                        AND s.content IS NOT NULL
                        AND e.document_id IS NULL
                )
            )
            WHERE ml_generate_embedding_status = ''
            """

            # Execute the embedding generation
            start_time = time.time()
            self.bigquery_client.execute_query(embedding_query)
            processing_time = time.time() - start_time

            # Verify the results (count actual new embeddings created)
            verify_query = f"""
            SELECT COUNT(*) as new_embeddings
            FROM `{self.embedding_table}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE)
            """
            verify_result = self.bigquery_client.execute_query(verify_query)
            actual_new_embeddings = list(verify_result)[0].new_embeddings

            # Update progress
            with self.progress_lock:
                self.total_processed += actual_new_embeddings
                elapsed_time = time.time() - self.start_time if self.start_time else 0
                docs_per_minute = (self.total_processed / elapsed_time * 60) if elapsed_time > 0 else 0

                logger.info(f"Batch completed: {actual_new_embeddings} new embeddings in {processing_time:.1f}s "
                          f"(Total: {self.total_processed}, Rate: {docs_per_minute:.1f} docs/min)")

            return {
                'status': 'success',
                'documents_processed': actual_new_embeddings,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate embeddings batch: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'documents_processed': 0
            }

    def process_documents_parallel(self, document_ids: List[str], batch_size: int = 200) -> Dict[str, Any]:
        """
        Process documents in parallel batches for maximum speed.

        Args:
            document_ids: List of all document IDs to process
            batch_size: Size of each batch

        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Starting parallel processing of {len(document_ids)} documents "
                       f"in batches of {batch_size}")

            # Create batches
            batches = [document_ids[i:i + batch_size] for i in range(0, len(document_ids), batch_size)]
            logger.info(f"Created {len(batches)} batches for parallel processing")

            # Process batches in parallel
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all batches
                future_to_batch = {
                    executor.submit(self.generate_embeddings_batch_fast, batch): i
                    for i, batch in enumerate(batches)
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_index = future_to_batch[future]
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"Batch {batch_index + 1}/{len(batches)} completed: "
                                  f"{result['documents_processed']} documents")
                    except Exception as e:
                        logger.error(f"Batch {batch_index + 1} failed: {e}")
                        results.append({'status': 'error', 'error': str(e), 'documents_processed': 0})

            # Calculate totals
            total_processed = sum(r.get('documents_processed', 0) for r in results)
            successful_batches = sum(1 for r in results if r.get('status') == 'success')

            return {
                'status': 'completed',
                'total_documents': len(document_ids),
                'total_processed': total_processed,
                'successful_batches': successful_batches,
                'total_batches': len(batches),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to process documents in parallel: {e}")
            raise

    def run_fast_embedding_pipeline(self, max_documents: int = None) -> Dict[str, Any]:
        """
        Run the complete fast embedding pipeline.

        Args:
            max_documents: Maximum number of documents to process (None for all)

        Returns:
            Dict containing complete pipeline results
        """
        try:
            logger.info("🚀 Starting Fast Embedding Pipeline")
            self.start_time = time.time()

            # Step 1: Get documents needing embedding
            logger.info("Step 1: Getting documents needing embedding...")
            document_ids = self.get_documents_needing_embedding(limit=max_documents)

            if not document_ids:
                logger.info("No documents need embedding")
                return {
                    'status': 'completed',
                    'total_processed': 0,
                    'message': 'All documents already have embeddings'
                }

            logger.info(f"Found {len(document_ids)} documents to process")

            # Step 2: Process documents in parallel
            logger.info("Step 2: Processing documents in parallel...")
            processing_result = self.process_documents_parallel(document_ids, self.batch_size)

            # Step 3: Final status check
            logger.info("Step 3: Checking final status...")
            final_status = self.check_embedding_status()

            total_time = time.time() - self.start_time

            logger.info(f"✅ Fast embedding pipeline completed in {total_time/60:.1f} minutes")

            return {
                'status': 'completed',
                'total_documents': len(document_ids),
                'total_processed': processing_result['total_processed'],
                'processing_time_minutes': total_time / 60,
                'documents_per_minute': processing_result['total_processed'] / (total_time / 60),
                'final_coverage': final_status['embedding_coverage'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Fast embedding pipeline failed: {e}")
            raise

    def check_embedding_status(self) -> Dict[str, Any]:
        """Check current embedding status."""
        try:
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
                COUNT(DISTINCT document_id) as unique_documents
            FROM `{self.embedding_table}`
            WHERE embedding IS NOT NULL
            """
            embedding_result = self.bigquery_client.execute_query(embedding_query)
            embedding_data = list(embedding_result)[0]

            status = {
                'total_documents': total_documents,
                'embedded_documents': embedding_data.embedded_documents,
                'unique_embedded_documents': embedding_data.unique_documents,
                'embedding_coverage': (embedding_data.embedded_documents / total_documents * 100) if total_documents > 0 else 0,
                'needs_embedding': total_documents - embedding_data.embedded_documents
            }

            return status

        except Exception as e:
            logger.error(f"Failed to check embedding status: {e}")
            raise


def main():
    """Main execution function for the fast embedding pipeline."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        print("🚀 Fast Legal Document Embedding Pipeline")
        print("=" * 50)
        print("Performance: ~27 docs/min, ~36 min for 1000 docs")
        print("=" * 50)

        # Initialize pipeline
        pipeline = FastEmbeddingPipeline()

        # Check initial status
        print("\n📊 Initial Status:")
        initial_status = pipeline.check_embedding_status()
        print(f"Total documents: {initial_status['total_documents']}")
        print(f"Embedded documents: {initial_status['embedded_documents']}")
        print(f"Coverage: {initial_status['embedding_coverage']:.1f}%")
        print(f"Documents needing embedding: {initial_status['needs_embedding']}")

        if initial_status['needs_embedding'] == 0:
            print("\n✅ All documents already have embeddings!")
            return

        # Ask user for confirmation
        print(f"\n⏰ Estimated time: {initial_status['needs_embedding'] * 2.17 / 60:.1f} minutes")
        response = input("Continue with fast embedding generation? (y/n): ")

        if response.lower() != 'y':
            print("Embedding generation cancelled.")
            return

        # Run fast pipeline
        print("\n🔄 Starting fast embedding generation...")
        results = pipeline.run_fast_embedding_pipeline()

        # Print final results
        print("\n📊 Final Results:")
        print(f"Documents processed: {results['total_processed']}")
        print(f"Processing time: {results['processing_time_minutes']:.1f} minutes")
        print(f"Processing rate: {results['documents_per_minute']:.1f} docs/min")
        print(f"Final coverage: {results['final_coverage']:.1f}%")

        print("\n✅ Fast embedding generation completed successfully!")

    except Exception as e:
        logger.error(f"Fast pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
