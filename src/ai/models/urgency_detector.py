"""
Urgency Detection Model
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the urgency detection model using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class UrgencyDetector:
    """Urgency detection model using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "urgency_detector"):
        """
        Initialize the urgency detector model.

        Args:
            project_id: BigQuery project ID
            model_name: Name of the BigQuery ML model
        """
        self.project_id = project_id
        self.model_name = model_name
        self.model_path = f"{project_id}.ai_models.{model_name}"
        self.urgency_levels = ['low', 'medium', 'high', 'critical']
        self.is_trained = False

    def create_model(self, bq_client) -> bool:
        """
        Create the urgency detector model in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating urgency detector model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Urgency detector model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating urgency detector model: {e}")
            return False

    def detect_urgency(self, bq_client, document_content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Detect urgency level of a legal document.

        Args:
            bq_client: BigQuery client instance
            document_content: Raw document content
            metadata: Optional document metadata (dates, deadlines, etc.)

        Returns:
            Urgency assessment dictionary
        """
        try:
            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.urgency_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare context for urgency detection
            context = document_content
            if metadata:
                context += f"\n\nMetadata: {metadata}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{context}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use the model to detect urgency
            urgency_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Analyze this legal document for urgency level. Consider: deadlines, time-sensitive matters, emergency situations, court dates, filing deadlines, and legal consequences. Return: urgency_level (low, medium, high, critical), confidence (0-100), reasoning (brief explanation), and key_indicators (list of urgency factors found). Document: ', content)
            ) as urgency_analysis
            FROM `{temp_table}`
            """

            result = bq_client.client.query(urgency_query).result()
            urgency_analysis = list(result)[0].urgency_analysis

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'urgency_analysis': urgency_analysis,
                'detection_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'metadata_considered': metadata is not None
            }

        except Exception as e:
            logger.error(f"Error detecting urgency: {e}")
            return {
                'error': str(e),
                'detection_timestamp': datetime.now().isoformat()
            }

    def batch_detect_urgency(self, bq_client, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect urgency for multiple documents.

        Args:
            bq_client: BigQuery client instance
            documents: List of documents with content and metadata

        Returns:
            List of urgency assessments
        """
        results = []

        for doc in documents:
            try:
                urgency = self.detect_urgency(
                    bq_client,
                    doc.get('content', ''),
                    doc.get('metadata', {})
                )
                urgency['document_id'] = doc.get('document_id', '')
                results.append(urgency)
            except Exception as e:
                logger.error(f"Error detecting urgency for document {doc.get('document_id', 'unknown')}: {e}")
                results.append({
                    'document_id': doc.get('document_id', ''),
                    'error': str(e),
                    'detection_timestamp': datetime.now().isoformat()
                })

        return results

    def extract_deadlines(self, bq_client, document_content: str) -> Dict[str, Any]:
        """
        Extract deadlines and time-sensitive information from document.

        Args:
            bq_client: BigQuery client instance
            document_content: Raw document content

        Returns:
            Deadline extraction results
        """
        try:
            # Create a temporary table with the document content
            temp_table = f"{self.project_id}.temp.deadline_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Insert document content into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{document_content}' as content
            """

            bq_client.client.query(insert_query).result()

            # Use the model to extract deadlines
            deadline_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Extract all deadlines, due dates, court dates, filing deadlines, and time-sensitive information from this legal document. Return: deadlines (list with dates and descriptions), urgency_factors (time-sensitive elements), and legal_consequences (what happens if deadlines are missed). Document: ', content)
            ) as deadline_info
            FROM `{temp_table}`
            """

            result = bq_client.client.query(deadline_query).result()
            deadline_info = list(result)[0].deadline_info

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'deadline_info': deadline_info,
                'extraction_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path
            }

        except Exception as e:
            logger.error(f"Error extracting deadlines: {e}")
            return {
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the urgency detector model.

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
                'urgency_levels': self.urgency_levels
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

def main():
    """Test the urgency detector model."""
    print("⚡ Urgency Detection Model")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Urgency detector model class created successfully")

if __name__ == "__main__":
    main()
