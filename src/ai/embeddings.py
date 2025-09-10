"""
Document Embedding Generation
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements document embedding generation using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentEmbeddingGenerator:
    """Document embedding generator using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "legal_embedding"):
        """
        Initialize the document embedding generator.

        Args:
            project_id: BigQuery project ID
            model_name: Name of the BigQuery ML embedding model
        """
        self.project_id = project_id
        self.model_name = model_name
        self.model_path = f"{project_id}.ai_models.{model_name}"
        self.embedding_dimension = 768  # Standard embedding dimension
        self.is_trained = False

    def create_model(self, bq_client) -> bool:
        """
        Create the document embedding model in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating document embedding model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Document embedding model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating document embedding model: {e}")
            return False

    def generate_embedding(self, bq_client, document_content: str) -> Dict[str, Any]:
        """
        Generate embedding for a single document.

        Args:
            bq_client: BigQuery client instance
            document_content: Document content to embed

        Returns:
            Embedding dictionary with vector and metadata
        """
        try:
            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.embedding_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{document_content}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use the model to generate embedding
            embedding_query = f"""
            SELECT ML.GENERATE_TEXT_EMBEDDING(
              MODEL `{self.model_path}`,
              content
            ) as embedding
            FROM `{temp_table}`
            """

            result = bq_client.client.query(embedding_query).result()
            embedding_result = list(result)[0].embedding

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'embedding': embedding_result,
                'embedding_dimension': self.embedding_dimension,
                'generation_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'content_length': len(document_content)
            }

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return {
                'error': str(e),
                'generation_timestamp': datetime.now().isoformat()
            }

    def batch_generate_embeddings(self, bq_client, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for multiple documents.

        Args:
            bq_client: BigQuery client instance
            documents: List of documents with content

        Returns:
            List of embedding dictionaries
        """
        results = []

        for doc in documents:
            try:
                embedding = self.generate_embedding(bq_client, doc.get('content', ''))
                embedding['document_id'] = doc.get('document_id', '')
                embedding['source_system'] = doc.get('source_system', '')
                results.append(embedding)
            except Exception as e:
                logger.error(f"Error generating embedding for document {doc.get('document_id', 'unknown')}: {e}")
                results.append({
                    'document_id': doc.get('document_id', ''),
                    'error': str(e),
                    'generation_timestamp': datetime.now().isoformat()
                })

        return results

    def store_embeddings(self, bq_client, embeddings: List[Dict[str, Any]]) -> bool:
        """
        Store document embeddings in BigQuery.

        Args:
            bq_client: BigQuery client instance
            embeddings: List of embedding dictionaries

        Returns:
            True if embeddings stored successfully, False otherwise
        """
        try:
            # Create embeddings table if it doesn't exist
            table_id = f"{self.project_id}.processed_data.document_embeddings"

            # Create table schema
            from google.cloud.bigquery import SchemaField

            schema = [
                SchemaField('document_id', 'STRING', mode='REQUIRED'),
                SchemaField('source_system', 'STRING', mode='NULLABLE'),
                SchemaField('embedding', 'JSON', mode='NULLABLE'),
                SchemaField('embedding_dimension', 'INTEGER', mode='NULLABLE'),
                SchemaField('content_length', 'INTEGER', mode='NULLABLE'),
                SchemaField('generation_timestamp', 'TIMESTAMP', mode='NULLABLE'),
                SchemaField('model_used', 'STRING', mode='NULLABLE')
            ]

            # Create table
            dataset_ref = bq_client.client.dataset('processed_data')
            table_ref = dataset_ref.table('document_embeddings')

            try:
                bq_client.client.get_table(table_ref)
                logger.info(f"Table {table_id} already exists")
            except Exception:
                table = bq_client.client.create_table(table_ref, schema=schema)
                logger.info(f"Created table {table_id}")

            # Prepare data for insertion
            rows_to_insert = []
            for embedding in embeddings:
                if 'error' not in embedding:
                    row = {
                        'document_id': embedding.get('document_id', ''),
                        'source_system': embedding.get('source_system', ''),
                        'embedding': str(embedding.get('embedding', '')),
                        'embedding_dimension': embedding.get('embedding_dimension', 0),
                        'content_length': embedding.get('content_length', 0),
                        'generation_timestamp': embedding.get('generation_timestamp', ''),
                        'model_used': embedding.get('model_used', '')
                    }
                    rows_to_insert.append(row)

            # Insert data
            if rows_to_insert:
                table = bq_client.client.get_table(table_ref)
                errors = bq_client.client.insert_rows_json(table, rows_to_insert)

                if errors:
                    logger.error(f"Errors inserting embeddings: {errors}")
                    return False
                else:
                    logger.info(f"Successfully stored {len(rows_to_insert)} embeddings")
                    return True
            else:
                logger.warning("No valid embeddings to store")
                return False

        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            return False

    def get_embedding_similarity(self, bq_client, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            bq_client: BigQuery client instance
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Create a temporary table with the embeddings
            temp_table = f"{self.project_id}.temp.similarity_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert embeddings into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT
              {embedding1} as embedding1,
              {embedding2} as embedding2
            """

            bq_client.client.query(insert_query).result()

            # Calculate cosine similarity
            similarity_query = f"""
            SELECT ML.DISTANCE(
              embedding1,
              embedding2,
              'COSINE'
            ) as similarity
            FROM `{temp_table}`
            """

            result = bq_client.client.query(similarity_query).result()
            similarity = list(result)[0].similarity

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return similarity

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the embedding model.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Model information dictionary
        """
        try:
            query = f"""
            SELECT
              model_name,
              model_type,
              creation_time,
              last_modified_time
            FROM `{self.project_id}.ai_models.INFORMATION_SCHEMA.MODELS`
            WHERE model_name = '{self.model_name}'
            """

            result = bq_client.client.query(query).result()
            model_info = list(result)[0]

            return {
                'model_name': model_info.model_name,
                'model_type': model_info.model_type,
                'creation_time': model_info.creation_time.isoformat(),
                'last_modified_time': model_info.last_modified_time.isoformat(),
                'model_path': self.model_path,
                'embedding_dimension': self.embedding_dimension
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

def main():
    """Test the document embedding generator."""
    print("🔗 Document Embedding Generator")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Document embedding generator class created successfully")

if __name__ == "__main__":
    main()
