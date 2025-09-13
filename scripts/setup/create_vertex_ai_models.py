#!/usr/bin/env python3
"""
Vertex AI Pre-trained Models Setup Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script creates BigQuery models using Google's pre-trained Vertex AI models.
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

class VertexAIModelsCreator:
    """Creates BigQuery models using Google's pre-trained Vertex AI models."""

    def __init__(self):
        """Initialize Vertex AI models creator."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']

    def create_vertex_ai_models(self) -> bool:
        """
        Create BigQuery models using Google's pre-trained Vertex AI models.

        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            logger.info("Starting Vertex AI pre-trained models setup...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                logger.error("Failed to connect to BigQuery")
                return False

            # Create models using Google's pre-trained models
            models_created = []

            # Create Gemini Pro model using Google's pre-trained model
            if self._create_gemini_pro_model():
                models_created.append("gemini_pro")
                logger.info("✅ Gemini Pro model created")
            else:
                logger.error("❌ Failed to create Gemini Pro model")
                return False

            # Create Text Embedding model using Google's pre-trained model
            if self._create_text_embedding_model():
                models_created.append("text_embedding")
                logger.info("✅ Text Embedding model created")
            else:
                logger.error("❌ Failed to create Text Embedding model")
                return False

            # Create TimesFM model using Google's pre-trained model
            if self._create_timesfm_model():
                models_created.append("timesfm")
                logger.info("✅ TimesFM model created")
            else:
                logger.error("❌ Failed to create TimesFM model")
                return False

            logger.info(f"Successfully created {len(models_created)} Vertex AI models: {', '.join(models_created)}")
            return True

        except Exception as e:
            logger.error(f"Failed to create Vertex AI models: {e}")
            return False

    def _create_gemini_pro_model(self) -> bool:
        """Create Gemini Pro model using Google's pre-trained model."""
        try:
            model_id = f"{self.project_id}.ai_models.gemini_pro"

            # Create model using Google's pre-trained Gemini Pro
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            OPTIONS (
                model_type = 'GEMINI_PRO',
                max_output_tokens = 2048,
                temperature = 0.1,
                top_p = 0.8,
                top_k = 40
            )
            """

            logger.info("Creating Gemini Pro model using Google's pre-trained model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(15)  # Give more time for model creation

            return True

        except Exception as e:
            logger.error(f"Failed to create Gemini Pro model: {e}")
            return False

    def _create_text_embedding_model(self) -> bool:
        """Create Text Embedding model using Google's pre-trained model."""
        try:
            model_id = f"{self.project_id}.ai_models.text_embedding"

            # Create model using Google's pre-trained Text Embedding
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            OPTIONS (
                model_type = 'TEXT_EMBEDDING',
                max_output_tokens = 768
            )
            """

            logger.info("Creating Text Embedding model using Google's pre-trained model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(15)

            return True

        except Exception as e:
            logger.error(f"Failed to create Text Embedding model: {e}")
            return False

    def _create_timesfm_model(self) -> bool:
        """Create TimesFM model using Google's pre-trained model."""
        try:
            model_id = f"{self.project_id}.ai_models.timesfm"

            # Create model using Google's pre-trained TimesFM
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            OPTIONS (
                model_type = 'TIMESFM',
                horizon = 7,
                frequency = 'DAILY'
            )
            """

            logger.info("Creating TimesFM model using Google's pre-trained model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(15)

            return True

        except Exception as e:
            logger.error(f"Failed to create TimesFM model: {e}")
            return False

    def validate_models(self) -> bool:
        """Validate that all models were created successfully."""
        try:
            logger.info("Validating Vertex AI models...")

            # Check if models exist
            models_to_check = [
                f"{self.project_id}.ai_models.gemini_pro",
                f"{self.project_id}.ai_models.text_embedding",
                f"{self.project_id}.ai_models.timesfm"
            ]

            for model_id in models_to_check:
                try:
                    model = self.bigquery_client.client.get_model(model_id)
                    logger.info(f"✅ Model exists: {model_id}")
                    logger.info(f"   Created: {model.created}")
                    logger.info(f"   Model Type: {model.model_type}")
                except Exception as e:
                    logger.error(f"❌ Model not found: {model_id} - {e}")
                    return False

            logger.info("✅ All Vertex AI models validated successfully")
            return True

        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False

    def test_ai_functions(self) -> bool:
        """Test AI functions with the created models."""
        try:
            logger.info("Testing AI functions with Vertex AI models...")

            # Test ML.GENERATE_TEXT
            test_query = f"""
            SELECT
                ML.GENERATE_TEXT(
                    MODEL `{self.project_id}.ai_models.gemini_pro`,
                    'Summarize this legal case: The plaintiff filed a lawsuit against the defendant for breach of contract.',
                    STRUCT(
                        0.1 AS temperature,
                        100 AS max_output_tokens
                    )
                ) AS summary
            """

            logger.info("Testing ML.GENERATE_TEXT...")
            result = self.bigquery_client.execute_query(test_query)

            for row in result:
                logger.info(f"✅ ML.GENERATE_TEXT test successful: {row.summary}")
                break

            return True

        except Exception as e:
            logger.error(f"AI functions test failed: {e}")
            return False


def main():
    """Main execution function."""
    try:
        print("🤖 Vertex AI Pre-trained Models Creator")
        print("=" * 50)
        print("Creating BigQuery models using Google's pre-trained Vertex AI models...")

        # Initialize creator
        creator = VertexAIModelsCreator()

        # Create models
        if creator.create_vertex_ai_models():
            print("✅ Vertex AI models created successfully!")

            # Validate models
            if creator.validate_models():
                print("✅ Vertex AI models validated successfully!")

                # Test AI functions
                if creator.test_ai_functions():
                    print("✅ AI functions test passed!")
                    print("\n🎯 Ready for Track 1 AI functions!")
                    return 0
                else:
                    print("❌ AI functions test failed")
                    return 1
            else:
                print("❌ Vertex AI models validation failed")
                return 1
        else:
            print("❌ Failed to create Vertex AI models")
            return 1

    except Exception as e:
        logger.error(f"Vertex AI models creation failed: {e}")
        print(f"\n❌ Vertex AI models creation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
