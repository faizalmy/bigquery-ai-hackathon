"""
Document Summarization Model
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the document summarization model using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentSummarizer:
    """Document summarization model using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "legal_summarizer"):
        """
        Initialize the document summarizer model.

        Args:
            project_id: BigQuery project ID
            model_name: Name of the BigQuery ML model
        """
        self.project_id = project_id
        self.model_name = model_name
        self.model_path = f"{project_id}.ai_models.{model_name}"
        self.is_trained = False

    def create_model(self, bq_client) -> bool:
        """
        Create the document summarizer model in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating document summarizer model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Document summarizer model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating document summarizer model: {e}")
            return False

    def summarize_document(self, bq_client, document_content: str, max_length: int = 200) -> Dict[str, Any]:
        """
        Summarize a legal document.

        Args:
            bq_client: BigQuery client instance
            document_content: Raw document content
            max_length: Maximum length of summary in words

        Returns:
            Summary dictionary with text and metadata
        """
        try:
            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.document_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{document_content}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use the model to summarize the document
            summary_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Summarize this legal document in 2-3 sentences (max {max_length} words). Focus on: the main legal issue, key parties involved, and the outcome or decision. Document: ', content)
            ) as summary
            FROM `{temp_table}`
            """

            result = bq_client.client.query(summary_query).result()
            summary_text = list(result)[0].summary

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'summary': summary_text,
                'original_length': len(document_content.split()),
                'summary_length': len(summary_text.split()),
                'compression_ratio': len(summary_text.split()) / len(document_content.split()) if document_content else 0,
                'summarization_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path
            }

        except Exception as e:
            logger.error(f"Error summarizing document: {e}")
            return {
                'error': str(e),
                'summarization_timestamp': datetime.now().isoformat()
            }

    def batch_summarize(self, bq_client, documents: List[Dict[str, Any]], max_length: int = 200) -> List[Dict[str, Any]]:
        """
        Summarize multiple documents.

        Args:
            bq_client: BigQuery client instance
            documents: List of documents with content
            max_length: Maximum length of summary in words

        Returns:
            List of document summaries
        """
        results = []

        for doc in documents:
            try:
                summary = self.summarize_document(bq_client, doc.get('content', ''), max_length)
                summary['document_id'] = doc.get('document_id', '')
                results.append(summary)
            except Exception as e:
                logger.error(f"Error summarizing document {doc.get('document_id', 'unknown')}: {e}")
                results.append({
                    'document_id': doc.get('document_id', ''),
                    'error': str(e),
                    'summarization_timestamp': datetime.now().isoformat()
                })

        return results

    def extractive_summarize(self, bq_client, document_content: str, num_sentences: int = 3) -> Dict[str, Any]:
        """
        Create an extractive summary by selecting key sentences.

        Args:
            bq_client: BigQuery client instance
            document_content: Raw document content
            num_sentences: Number of sentences to extract

        Returns:
            Extractive summary dictionary
        """
        try:
            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.extractive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{document_content}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use the model to extract key sentences
            extractive_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Extract the {num_sentences} most important sentences from this legal document. Return only the sentences, one per line. Document: ', content)
            ) as extracted_sentences
            FROM `{temp_table}`
            """

            result = bq_client.client.query(extractive_query).result()
            extracted_sentences = list(result)[0].extracted_sentences

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'extractive_summary': extracted_sentences,
                'num_sentences_requested': num_sentences,
                'extraction_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path
            }

        except Exception as e:
            logger.error(f"Error creating extractive summary: {e}")
            return {
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the document summarizer model.

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
                'model_path': self.model_path
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

def main():
    """Test the document summarizer model."""
    print("📝 Document Summarization Model")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Document summarizer model class created successfully")

if __name__ == "__main__":
    main()
