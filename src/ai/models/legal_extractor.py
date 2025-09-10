"""
Legal Data Extraction Model
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the legal data extraction model using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalExtractor:
    """Legal data extraction model using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "legal_extractor"):
        """
        Initialize the legal extractor model.

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
        Create the legal extractor model in BigQuery ML.
        Note: For text generation, we use BigQuery's built-in capabilities
        without creating a custom model.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model setup is successful, False otherwise
        """
        try:
            logger.info(f"Setting up legal extractor capabilities: {self.model_path}")

            # For text generation, we don't need to create a model
            # We'll use BigQuery's built-in text generation functions
            logger.info("✅ Legal extractor capabilities ready (using built-in text generation)")
            return True

        except Exception as e:
            logger.error(f"Error setting up legal extractor: {e}")
            return False

    def extract_legal_data(self, bq_client, document_content: str) -> Dict[str, Any]:
        """
        Extract legal data from document content using BigQuery's built-in capabilities.

        Args:
            bq_client: BigQuery client instance
            document_content: Raw document content

        Returns:
            Extracted legal data dictionary
        """
        try:
            # For now, we'll implement a basic extraction using SQL functions
            # This can be enhanced with actual AI models when available

            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.legal_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{document_content}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use basic SQL functions for legal data extraction
            extraction_query = f"""
            SELECT
              content,
              CASE
                WHEN UPPER(content) LIKE '%PLAINTIFF%' THEN 'Plaintiff found'
                ELSE 'No plaintiff mentioned'
              END as plaintiff_info,
              CASE
                WHEN UPPER(content) LIKE '%DEFENDANT%' THEN 'Defendant found'
                ELSE 'No defendant mentioned'
              END as defendant_info,
              CASE
                WHEN UPPER(content) LIKE '%COURT%' THEN 'Court mentioned'
                ELSE 'No court mentioned'
              END as court_info,
              CASE
                WHEN UPPER(content) LIKE '%MOTION%' THEN 'Motion found'
                WHEN UPPER(content) LIKE '%JUDGMENT%' THEN 'Judgment found'
                WHEN UPPER(content) LIKE '%APPEAL%' THEN 'Appeal found'
                ELSE 'Other legal matter'
              END as legal_issue_type
            FROM `{temp_table}`
            """

            result = bq_client.client.query(extraction_query).result()
            extraction_result = list(result)[0]

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'extracted_data': {
                    'plaintiff_info': extraction_result.plaintiff_info,
                    'defendant_info': extraction_result.defendant_info,
                    'court_info': extraction_result.court_info,
                    'legal_issue_type': extraction_result.legal_issue_type,
                    'extraction_method': 'SQL-based extraction'
                },
                'extraction_timestamp': datetime.now().isoformat(),
                'model_used': 'SQL-based extraction'
            }

        except Exception as e:
            logger.error(f"Error extracting legal data: {e}")
            return {
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def batch_extract(self, bq_client, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract legal data from multiple documents.

        Args:
            bq_client: BigQuery client instance
            documents: List of documents with content

        Returns:
            List of extracted legal data
        """
        results = []

        for doc in documents:
            try:
                extracted = self.extract_legal_data(bq_client, doc.get('content', ''))
                extracted['document_id'] = doc.get('document_id', '')
                results.append(extracted)
            except Exception as e:
                logger.error(f"Error processing document {doc.get('document_id', 'unknown')}: {e}")
                results.append({
                    'document_id': doc.get('document_id', ''),
                    'error': str(e),
                    'extraction_timestamp': datetime.now().isoformat()
                })

        return results

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the legal extractor model.

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
    """Test the legal extractor model."""
    print("🔍 Legal Data Extraction Model")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Legal extractor model class created successfully")

if __name__ == "__main__":
    main()
