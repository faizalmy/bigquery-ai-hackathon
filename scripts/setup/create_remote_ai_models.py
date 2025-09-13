#!/usr/bin/env python3
"""
Remote AI Models Creation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script creates remote AI models that connect to Vertex AI for Track 1 functions.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_client import BigQueryClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemoteAIModelsCreator:
    """Creates remote AI models that connect to Vertex AI."""

    def __init__(self):
        """Initialize remote AI models creator."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']

    def create_remote_ai_models(self) -> bool:
        """
        Create all required remote AI models.

        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            logger.info("Starting remote AI models creation...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                logger.error("Failed to connect to BigQuery")
                return False

            # Create models
            models_created = []

            # Create Gemini Pro remote model
            if self._create_gemini_pro_remote_model():
                models_created.append("gemini_pro")
                logger.info("✅ Gemini Pro remote model created")
            else:
                logger.error("❌ Failed to create Gemini Pro remote model")
                return False

            # Create Text Embedding remote model
            if self._create_text_embedding_remote_model():
                models_created.append("text_embedding")
                logger.info("✅ Text Embedding remote model created")
            else:
                logger.error("❌ Failed to create Text Embedding remote model")
                return False

            # Create TimesFM remote model
            if self._create_timesfm_remote_model():
                models_created.append("timesfm")
                logger.info("✅ TimesFM remote model created")
            else:
                logger.error("❌ Failed to create TimesFM remote model")
                return False

            logger.info(f"Successfully created {len(models_created)} remote AI models: {', '.join(models_created)}")
            return True

        except Exception as e:
            logger.error(f"Failed to create remote AI models: {e}")
            return False

    def _create_gemini_pro_remote_model(self) -> bool:
        """Create Gemini Pro remote model for text generation."""
        try:
            model_id = f"{self.project_id}.ai_models.gemini_pro"

            # Create remote model using CREATE MODEL statement
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            REMOTE WITH CONNECTION `{self.project_id}.us-central1.vertex-ai-connection`
            OPTIONS (
                remote_service_type = 'CLOUD_AI_LARGE_LANGUAGE_MODEL_V1',
                endpoint = 'https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/gemini-pro:generateContent'
            )
            """

            logger.info("Creating Gemini Pro remote model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(10)

            return True

        except Exception as e:
            logger.error(f"Failed to create Gemini Pro remote model: {e}")
            return False

    def _create_text_embedding_remote_model(self) -> bool:
        """Create Text Embedding remote model for vector search."""
        try:
            model_id = f"{self.project_id}.ai_models.text_embedding"

            # Create remote model using CREATE MODEL statement
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            REMOTE WITH CONNECTION `{self.project_id}.us-central1.vertex-ai-connection`
            OPTIONS (
                remote_service_type = 'CLOUD_AI_LARGE_LANGUAGE_MODEL_V1',
                endpoint = 'https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/text-embedding-004:embedContent'
            )
            """

            logger.info("Creating Text Embedding remote model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(10)

            return True

        except Exception as e:
            logger.error(f"Failed to create Text Embedding remote model: {e}")
            return False

    def _create_timesfm_remote_model(self) -> bool:
        """Create TimesFM remote model for forecasting."""
        try:
            model_id = f"{self.project_id}.ai_models.timesfm"

            # Create remote model using CREATE MODEL statement
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            REMOTE WITH CONNECTION `{self.project_id}.us-central1.vertex-ai-connection`
            OPTIONS (
                remote_service_type = 'CLOUD_AI_LARGE_LANGUAGE_MODEL_V1',
                endpoint = 'https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/timesfm:predict'
            )
            """

            logger.info("Creating TimesFM remote model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(10)

            return True

        except Exception as e:
            logger.error(f"Failed to create TimesFM remote model: {e}")
            return False

    def validate_models(self) -> bool:
        """Validate that all remote models were created successfully."""
        try:
            logger.info("Validating remote AI models...")

            # Check if models exist
            models_to_check = [
                f"{self.project_id}.ai_models.gemini_pro",
                f"{self.project_id}.ai_models.text_embedding",
                f"{self.project_id}.ai_models.timesfm"
            ]

            for model_id in models_to_check:
                try:
                    model = self.bigquery_client.client.get_model(model_id)
                    logger.info(f"✅ Remote model exists: {model_id}")
                except Exception as e:
                    logger.error(f"❌ Remote model not found: {model_id} - {e}")
                    return False

            logger.info("✅ All remote AI models validated successfully")
            return True

        except Exception as e:
            logger.error(f"Remote model validation failed: {e}")
            return False


def main():
    """Main execution function."""
    try:
        print("🤖 Remote AI Models Creator")
        print("=" * 40)
        print("Creating BigQuery remote AI models connected to Vertex AI...")

        # Initialize creator
        creator = RemoteAIModelsCreator()

        # Create models
        if creator.create_remote_ai_models():
            print("✅ Remote AI models created successfully!")

            # Validate models
            if creator.validate_models():
                print("✅ Remote AI models validated successfully!")
                print("\n🎯 Ready for Track 1 AI functions!")
                return 0
            else:
                print("❌ Remote AI models validation failed")
                return 1
        else:
            print("❌ Failed to create remote AI models")
            return 1

    except Exception as e:
        logger.error(f"Remote AI models creation failed: {e}")
        print(f"\n❌ Remote AI models creation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
