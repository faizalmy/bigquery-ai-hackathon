#!/usr/bin/env python3
"""
AI Models Creation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script creates the required AI models for Track 1 BigQuery AI functions.
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

class AIModelsCreator:
    """Creates AI models for BigQuery AI functions."""

    def __init__(self):
        """Initialize AI models creator."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']

    def create_ai_models(self) -> bool:
        """
        Create all required AI models.

        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            logger.info("Starting AI models creation...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                logger.error("Failed to connect to BigQuery")
                return False

            # Create models
            models_created = []

            # Create Gemini Pro model
            if self._create_gemini_pro_model():
                models_created.append("gemini_pro")
                logger.info("✅ Gemini Pro model created")
            else:
                logger.error("❌ Failed to create Gemini Pro model")
                return False

            # Create Text Embedding model
            if self._create_text_embedding_model():
                models_created.append("text_embedding")
                logger.info("✅ Text Embedding model created")
            else:
                logger.error("❌ Failed to create Text Embedding model")
                return False

            # Create TimesFM model
            if self._create_timesfm_model():
                models_created.append("timesfm")
                logger.info("✅ TimesFM model created")
            else:
                logger.error("❌ Failed to create TimesFM model")
                return False

            logger.info(f"Successfully created {len(models_created)} AI models: {', '.join(models_created)}")
            return True

        except Exception as e:
            logger.error(f"Failed to create AI models: {e}")
            return False

    def _create_gemini_pro_model(self) -> bool:
        """Create Gemini Pro model for text generation."""
        try:
            model_id = f"{self.project_id}.ai_models.gemini_pro"

            # Create model using CREATE MODEL statement
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

            logger.info("Creating Gemini Pro model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(10)  # Give model time to be created

            return True

        except Exception as e:
            logger.error(f"Failed to create Gemini Pro model: {e}")
            return False

    def _create_text_embedding_model(self) -> bool:
        """Create Text Embedding model for vector search."""
        try:
            model_id = f"{self.project_id}.ai_models.text_embedding"

            # Create model using CREATE MODEL statement
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            OPTIONS (
                model_type = 'TEXT_EMBEDDING',
                max_output_tokens = 768
            )
            """

            logger.info("Creating Text Embedding model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(10)

            return True

        except Exception as e:
            logger.error(f"Failed to create Text Embedding model: {e}")
            return False

    def _create_timesfm_model(self) -> bool:
        """Create TimesFM model for forecasting."""
        try:
            model_id = f"{self.project_id}.ai_models.timesfm"

            # Create model using CREATE MODEL statement
            create_model_sql = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            OPTIONS (
                model_type = 'TIMESFM',
                horizon = 7,
                frequency = 'DAILY'
            )
            """

            logger.info("Creating TimesFM model...")
            result = self.bigquery_client.execute_query(create_model_sql)

            # Wait for model creation to complete
            import time
            time.sleep(10)

            return True

        except Exception as e:
            logger.error(f"Failed to create TimesFM model: {e}")
            return False

    def validate_models(self) -> bool:
        """Validate that all models were created successfully."""
        try:
            logger.info("Validating AI models...")

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
                except Exception as e:
                    logger.error(f"❌ Model not found: {model_id} - {e}")
                    return False

            logger.info("✅ All AI models validated successfully")
            return True

        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False


def main():
    """Main execution function."""
    try:
        print("🤖 AI Models Creator")
        print("=" * 40)
        print("Creating BigQuery AI models for Track 1 functions...")

        # Initialize creator
        creator = AIModelsCreator()

        # Create models
        if creator.create_ai_models():
            print("✅ AI models created successfully!")

            # Validate models
            if creator.validate_models():
                print("✅ AI models validated successfully!")
                print("\n🎯 Ready for Track 1 AI functions!")
                return 0
            else:
                print("❌ AI models validation failed")
                return 1
        else:
            print("❌ Failed to create AI models")
            return 1

    except Exception as e:
        logger.error(f"AI models creation failed: {e}")
        print(f"\n❌ AI models creation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
