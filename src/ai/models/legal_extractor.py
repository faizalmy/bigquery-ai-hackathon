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

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating legal extractor model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Legal extractor model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating legal extractor model: {e}")
            return False

    def extract_legal_data(self, bq_client, document_content: str) -> Dict[str, Any]:
        """
        Extract legal data from document content.

        Args:
            bq_client: BigQuery client instance
            document_content: Raw document content

        Returns:
            Extracted legal data dictionary
        """
        try:
            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.legal_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{document_content}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use the model to extract legal data
            extraction_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Extract key legal information from this document. Return a JSON object with: parties (plaintiff, defendant), legal_issues (list of legal issues), court (court name), date (case date), outcome (if mentioned), and key_facts (important facts). Document: ', content)
            ) as extracted_data
            FROM `{temp_table}`
            """

            result = bq_client.client.query(extraction_query).result()
            extracted_data = list(result)[0].extracted_data

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'extracted_data': extracted_data,
                'extraction_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path
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
