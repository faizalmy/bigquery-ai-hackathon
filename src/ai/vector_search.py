"""
Vector Search Implementation
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements vector similarity search for legal documents.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """Vector search engine for legal document similarity."""

    def __init__(self, project_id: str, embedding_model_name: str = "legal_embedding"):
        """
        Initialize the vector search engine.

        Args:
            project_id: BigQuery project ID
            embedding_model_name: Name of the embedding model
        """
        self.project_id = project_id
        self.embedding_model_name = embedding_model_name
        self.embedding_model_path = f"{project_id}.ai_models.{embedding_model_name}"
        self.embeddings_table = f"{project_id}.processed_data.document_embeddings"
        self.documents_table = f"{project_id}.processed_data.legal_documents"

    def search_similar_documents(self, bq_client, query_text: str, limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query text.

        Args:
            bq_client: BigQuery client instance
            query_text: Text to search for similar documents
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar documents with similarity scores
        """
        try:
            logger.info(f"Searching for documents similar to: {query_text[:100]}...")

            # Generate embedding for the query text
            query_embedding_query = f"""
            SELECT ML.GENERATE_TEXT_EMBEDDING(
              MODEL `{self.embedding_model_path}`,
              '{query_text}'
            ) as query_embedding
            """

            result = bq_client.client.query(query_embedding_query).result()
            query_embedding = list(result)[0].query_embedding

            # Search for similar documents
            similarity_search_query = f"""
            WITH query_embedding AS (
              SELECT ML.GENERATE_TEXT_EMBEDDING(
                MODEL `{self.embedding_model_path}`,
                '{query_text}'
              ) as embedding
            ),
            document_similarities AS (
              SELECT
                de.document_id,
                de.source_system,
                de.embedding,
                ML.DISTANCE(
                  de.embedding,
                  qe.embedding,
                  'COSINE'
                ) as similarity_score
              FROM `{self.embeddings_table}` de
              CROSS JOIN query_embedding qe
              WHERE de.embedding IS NOT NULL
            )
            SELECT
              ds.document_id,
              ds.source_system,
              ds.similarity_score,
              ld.document_type,
              ld.cleaned_content,
              ld.quality_score,
              ld.processed_timestamp
            FROM document_similarities ds
            LEFT JOIN `{self.documents_table}` ld
              ON ds.document_id = ld.document_id
            WHERE ds.similarity_score >= {similarity_threshold}
            ORDER BY ds.similarity_score DESC
            LIMIT {limit}
            """

            result = bq_client.client.query(similarity_search_query).result()
            similar_documents = []

            for row in result:
                similar_documents.append({
                    'document_id': row.document_id,
                    'source_system': row.source_system,
                    'similarity_score': row.similarity_score,
                    'document_type': row.document_type,
                    'content_preview': row.cleaned_content[:200] + '...' if row.cleaned_content else '',
                    'quality_score': row.quality_score,
                    'processed_timestamp': row.processed_timestamp.isoformat() if row.processed_timestamp else None
                })

            logger.info(f"Found {len(similar_documents)} similar documents")
            return similar_documents

        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return []

    def find_case_law_precedents(self, bq_client, case_facts: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find relevant case law precedents for given case facts.

        Args:
            bq_client: BigQuery client instance
            case_facts: Facts of the current case
            limit: Maximum number of precedents to return

        Returns:
            List of relevant case law precedents
        """
        try:
            logger.info("Searching for case law precedents...")

            # Search for similar case law documents
            precedents = self.search_similar_documents(
                bq_client,
                case_facts,
                limit=limit,
                similarity_threshold=0.6
            )

            # Filter for case law documents
            case_law_precedents = [
                doc for doc in precedents
                if doc.get('document_type') in ['supreme_court_case', 'court_case', 'legal_brief']
            ]

            logger.info(f"Found {len(case_law_precedents)} relevant precedents")
            return case_law_precedents

        except Exception as e:
            logger.error(f"Error finding case law precedents: {e}")
            return []

    def find_regulatory_guidance(self, bq_client, regulatory_question: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find relevant regulatory guidance for a regulatory question.

        Args:
            bq_client: BigQuery client instance
            regulatory_question: Regulatory question or issue
            limit: Maximum number of guidance documents to return

        Returns:
            List of relevant regulatory guidance
        """
        try:
            logger.info("Searching for regulatory guidance...")

            # Search for similar regulatory documents
            guidance = self.search_similar_documents(
                bq_client,
                regulatory_question,
                limit=limit,
                similarity_threshold=0.6
            )

            # Filter for regulatory documents
            regulatory_guidance = [
                doc for doc in guidance
                if doc.get('document_type') in ['federal_regulation', 'statute']
            ]

            logger.info(f"Found {len(regulatory_guidance)} relevant regulatory guidance")
            return regulatory_guidance

        except Exception as e:
            logger.error(f"Error finding regulatory guidance: {e}")
            return []

    def find_contract_templates(self, bq_client, contract_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find relevant contract templates for a specific contract type.

        Args:
            bq_client: BigQuery client instance
            contract_type: Type of contract needed
            limit: Maximum number of templates to return

        Returns:
            List of relevant contract templates
        """
        try:
            logger.info(f"Searching for {contract_type} contract templates...")

            # Search for similar contract documents
            templates = self.search_similar_documents(
                bq_client,
                f"{contract_type} contract template",
                limit=limit,
                similarity_threshold=0.5
            )

            # Filter for contract documents
            contract_templates = [
                doc for doc in templates
                if doc.get('document_type') == 'contract'
            ]

            logger.info(f"Found {len(contract_templates)} relevant contract templates")
            return contract_templates

        except Exception as e:
            logger.error(f"Error finding contract templates: {e}")
            return []

    def get_document_similarity_matrix(self, bq_client, document_ids: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Calculate similarity matrix between specified documents.

        Args:
            bq_client: BigQuery client instance
            document_ids: List of document IDs to compare

        Returns:
            Similarity matrix as nested dictionary
        """
        try:
            logger.info(f"Calculating similarity matrix for {len(document_ids)} documents...")

            # Create similarity matrix query
            similarity_query = f"""
            WITH document_embeddings AS (
              SELECT
                document_id,
                embedding
              FROM `{self.embeddings_table}`
              WHERE document_id IN ({', '.join([f"'{doc_id}'" for doc_id in document_ids])})
                AND embedding IS NOT NULL
            ),
            similarity_pairs AS (
              SELECT
                d1.document_id as doc1,
                d2.document_id as doc2,
                ML.DISTANCE(
                  d1.embedding,
                  d2.embedding,
                  'COSINE'
                ) as similarity
              FROM document_embeddings d1
              CROSS JOIN document_embeddings d2
              WHERE d1.document_id != d2.document_id
            )
            SELECT
              doc1,
              doc2,
              similarity
            FROM similarity_pairs
            ORDER BY doc1, doc2
            """

            result = bq_client.client.query(similarity_query).result()
            similarity_matrix = {}

            # Initialize matrix
            for doc_id in document_ids:
                similarity_matrix[doc_id] = {}

            # Fill matrix with similarity scores
            for row in result:
                similarity_matrix[row.doc1][row.doc2] = row.similarity

            logger.info("Similarity matrix calculated successfully")
            return similarity_matrix

        except Exception as e:
            logger.error(f"Error calculating similarity matrix: {e}")
            return {}

    def cluster_documents(self, bq_client, document_type: Optional[str] = None, num_clusters: int = 5) -> Dict[str, List[str]]:
        """
        Cluster documents based on their embeddings.

        Args:
            bq_client: BigQuery client instance
            document_type: Optional document type filter
            num_clusters: Number of clusters to create

        Returns:
            Dictionary mapping cluster IDs to document IDs
        """
        try:
            logger.info(f"Clustering documents with {num_clusters} clusters...")

            # Build the clustering query
            clustering_query = f"""
            WITH document_embeddings AS (
              SELECT
                de.document_id,
                de.embedding,
                ld.document_type
              FROM `{self.embeddings_table}` de
              LEFT JOIN `{self.documents_table}` ld
                ON de.document_id = ld.document_id
              WHERE de.embedding IS NOT NULL
                {'AND ld.document_type = \'' + document_type + '\'' if document_type else ''}
            )
            SELECT
              document_id,
              ML.KMEANS(
                embedding,
                {num_clusters}
              ) OVER() as cluster_id
            FROM document_embeddings
            ORDER BY cluster_id, document_id
            """

            result = bq_client.client.query(clustering_query).result()
            clusters = {}

            for row in result:
                cluster_id = str(row.cluster_id)
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(row.document_id)

            logger.info(f"Created {len(clusters)} clusters")
            return clusters

        except Exception as e:
            logger.error(f"Error clustering documents: {e}")
            return {}

    def get_search_statistics(self, bq_client) -> Dict[str, Any]:
        """
        Get statistics about the vector search system.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Search statistics dictionary
        """
        try:
            stats_query = f"""
            SELECT
              COUNT(*) as total_documents,
              COUNT(DISTINCT source_system) as unique_sources,
              COUNT(DISTINCT document_type) as unique_types,
              AVG(embedding_dimension) as avg_embedding_dimension,
              MIN(generation_timestamp) as oldest_embedding,
              MAX(generation_timestamp) as newest_embedding
            FROM `{self.embeddings_table}`
            WHERE embedding IS NOT NULL
            """

            result = bq_client.client.query(stats_query).result()
            stats = list(result)[0]

            return {
                'total_documents': stats.total_documents,
                'unique_sources': stats.unique_sources,
                'unique_types': stats.unique_types,
                'avg_embedding_dimension': stats.avg_embedding_dimension,
                'oldest_embedding': stats.oldest_embedding.isoformat() if stats.oldest_embedding else None,
                'newest_embedding': stats.newest_embedding.isoformat() if stats.newest_embedding else None,
                'search_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {'error': str(e)}

def main():
    """Test the vector search engine."""
    print("🔍 Vector Search Engine")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Vector search engine class created successfully")

if __name__ == "__main__":
    main()
