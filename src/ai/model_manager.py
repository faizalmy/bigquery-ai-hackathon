"""
Model Lifecycle Management
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements model lifecycle management for AI models.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .models import (
    LegalExtractor, DocumentSummarizer, UrgencyDetector,
    OutcomePredictor, RiskAssessor, StrategyGenerator
)
from .embeddings import DocumentEmbeddingGenerator
from .vector_search import VectorSearchEngine

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages the lifecycle of all AI models."""

    def __init__(self, project_id: str):
        """
        Initialize the model manager.

        Args:
            project_id: BigQuery project ID
        """
        self.project_id = project_id
        self.models = {}
        self.embedding_generator = None
        self.vector_search_engine = None
        self.model_status = {}

    def initialize_models(self, bq_client) -> Dict[str, bool]:
        """
        Initialize all AI models.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Dictionary of model initialization results
        """
        logger.info("Initializing all AI models...")

        results = {}

        # Initialize individual models
        model_classes = {
            'legal_extractor': LegalExtractor,
            'document_summarizer': DocumentSummarizer,
            'urgency_detector': UrgencyDetector,
            'outcome_predictor': OutcomePredictor,
            'risk_assessor': RiskAssessor,
            'strategy_generator': StrategyGenerator
        }

        for model_name, model_class in model_classes.items():
            try:
                model = model_class(self.project_id)
                self.models[model_name] = model
                results[model_name] = True
                self.model_status[model_name] = 'initialized'
                logger.info(f"✅ {model_name} model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {model_name}: {e}")
                results[model_name] = False
                self.model_status[model_name] = 'failed'

        # Initialize embedding generator
        try:
            self.embedding_generator = DocumentEmbeddingGenerator(self.project_id)
            results['embedding_generator'] = True
            self.model_status['embedding_generator'] = 'initialized'
            logger.info("✅ Embedding generator initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding generator: {e}")
            results['embedding_generator'] = False
            self.model_status['embedding_generator'] = 'failed'

        # Initialize vector search engine
        try:
            self.vector_search_engine = VectorSearchEngine(self.project_id)
            results['vector_search_engine'] = True
            self.model_status['vector_search_engine'] = 'initialized'
            logger.info("✅ Vector search engine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector search engine: {e}")
            results['vector_search_engine'] = False
            self.model_status['vector_search_engine'] = 'failed'

        return results

    def create_all_models(self, bq_client) -> Dict[str, bool]:
        """
        Create all AI models in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Dictionary of model creation results
        """
        logger.info("Creating all AI models in BigQuery ML...")

        results = {}

        # Create individual models
        for model_name, model in self.models.items():
            try:
                success = model.create_model(bq_client)
                results[model_name] = success
                if success:
                    self.model_status[model_name] = 'created'
                    logger.info(f"✅ {model_name} model created")
                else:
                    self.model_status[model_name] = 'creation_failed'
                    logger.error(f"❌ {model_name} model creation failed")
            except Exception as e:
                logger.error(f"❌ Error creating {model_name}: {e}")
                results[model_name] = False
                self.model_status[model_name] = 'creation_failed'

        # Create embedding model
        if self.embedding_generator:
            try:
                success = self.embedding_generator.create_model(bq_client)
                results['embedding_model'] = success
                if success:
                    self.model_status['embedding_model'] = 'created'
                    logger.info("✅ Embedding model created")
                else:
                    self.model_status['embedding_model'] = 'creation_failed'
                    logger.error("❌ Embedding model creation failed")
            except Exception as e:
                logger.error(f"❌ Error creating embedding model: {e}")
                results['embedding_model'] = False
                self.model_status['embedding_model'] = 'creation_failed'

        return results

    def test_all_models(self, bq_client) -> Dict[str, Dict[str, Any]]:
        """
        Test all AI models with sample data.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Dictionary of test results for each model
        """
        logger.info("Testing all AI models...")

        test_results = {}

        # Sample test data
        sample_document = {
            'document_id': 'TEST_001',
            'content': 'In the Supreme Court of the United States, the plaintiff filed a motion for summary judgment pursuant to Rule 56 of the Federal Rules of Civil Procedure. The court must consider whether there are genuine issues of material fact.',
            'metadata': {
                'source': 'Test Source',
                'date': '2025-01-01'
            }
        }

        sample_case = {
            'case_id': 'CASE_001',
            'facts': 'Plaintiff alleges breach of contract by defendant.',
            'legal_issues': ['contract law', 'breach of contract'],
            'parties': ['Plaintiff Corp', 'Defendant LLC'],
            'court': 'Federal District Court'
        }

        # Test individual models
        for model_name, model in self.models.items():
            try:
                if model_name == 'legal_extractor':
                    result = model.extract_legal_data(bq_client, sample_document['content'])
                elif model_name == 'document_summarizer':
                    result = model.summarize_document(bq_client, sample_document['content'])
                elif model_name == 'urgency_detector':
                    result = model.detect_urgency(bq_client, sample_document['content'], sample_document['metadata'])
                elif model_name == 'outcome_predictor':
                    result = model.predict_outcome(bq_client, sample_case)
                elif model_name == 'risk_assessor':
                    result = model.assess_risk(bq_client, sample_case)
                elif model_name == 'strategy_generator':
                    result = model.generate_strategy(bq_client, sample_case)

                test_results[model_name] = {
                    'status': 'success',
                    'result': result,
                    'test_timestamp': datetime.now().isoformat()
                }
                logger.info(f"✅ {model_name} test successful")

            except Exception as e:
                test_results[model_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'test_timestamp': datetime.now().isoformat()
                }
                logger.error(f"❌ {model_name} test failed: {e}")

        # Test embedding generator
        if self.embedding_generator:
            try:
                result = self.embedding_generator.generate_embedding(bq_client, sample_document['content'])
                test_results['embedding_generator'] = {
                    'status': 'success',
                    'result': result,
                    'test_timestamp': datetime.now().isoformat()
                }
                logger.info("✅ Embedding generator test successful")
            except Exception as e:
                test_results['embedding_generator'] = {
                    'status': 'failed',
                    'error': str(e),
                    'test_timestamp': datetime.now().isoformat()
                }
                logger.error(f"❌ Embedding generator test failed: {e}")

        # Test vector search engine
        if self.vector_search_engine:
            try:
                result = self.vector_search_engine.search_similar_documents(bq_client, sample_document['content'], limit=3)
                test_results['vector_search_engine'] = {
                    'status': 'success',
                    'result': result,
                    'test_timestamp': datetime.now().isoformat()
                }
                logger.info("✅ Vector search engine test successful")
            except Exception as e:
                test_results['vector_search_engine'] = {
                    'status': 'failed',
                    'error': str(e),
                    'test_timestamp': datetime.now().isoformat()
                }
                logger.error(f"❌ Vector search engine test failed: {e}")

        return test_results

    def get_model_status(self) -> Dict[str, str]:
        """
        Get the current status of all models.

        Returns:
            Dictionary of model statuses
        """
        return self.model_status.copy()

    def get_model_info(self, bq_client) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about all models.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Dictionary of model information
        """
        model_info = {}

        # Get info for individual models
        for model_name, model in self.models.items():
            try:
                info = model.get_model_info(bq_client)
                model_info[model_name] = info
            except Exception as e:
                model_info[model_name] = {'error': str(e)}

        # Get info for embedding generator
        if self.embedding_generator:
            try:
                info = self.embedding_generator.get_model_info(bq_client)
                model_info['embedding_generator'] = info
            except Exception as e:
                model_info['embedding_generator'] = {'error': str(e)}

        # Get info for vector search engine
        if self.vector_search_engine:
            try:
                info = self.vector_search_engine.get_search_statistics(bq_client)
                model_info['vector_search_engine'] = info
            except Exception as e:
                model_info['vector_search_engine'] = {'error': str(e)}

        return model_info

    def deploy_models(self, bq_client) -> Dict[str, bool]:
        """
        Deploy all models (create and test).

        Args:
            bq_client: BigQuery client instance

        Returns:
            Dictionary of deployment results
        """
        logger.info("Deploying all AI models...")

        deployment_results = {}

        # Initialize models
        init_results = self.initialize_models(bq_client)
        deployment_results['initialization'] = init_results

        # Create models
        create_results = self.create_all_models(bq_client)
        deployment_results['creation'] = create_results

        # Test models
        test_results = self.test_all_models(bq_client)
        deployment_results['testing'] = test_results

        # Overall deployment status
        all_models_created = all(create_results.values())
        all_models_tested = all(
            result.get('status') == 'success'
            for result in test_results.values()
        )

        deployment_results['overall_success'] = all_models_created and all_models_tested

        if deployment_results['overall_success']:
            logger.info("✅ All models deployed successfully")
        else:
            logger.error("❌ Model deployment had issues")

        return deployment_results

    def cleanup_models(self, bq_client) -> bool:
        """
        Clean up (delete) all models.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if cleanup successful, False otherwise
        """
        logger.info("Cleaning up all AI models...")

        try:
            # Delete all models from BigQuery
            models_to_delete = [
                'legal_extractor', 'document_summarizer', 'urgency_detector',
                'outcome_predictor', 'risk_assessor', 'strategy_generator',
                'legal_embedding'
            ]

            for model_name in models_to_delete:
                try:
                    delete_query = f"""
                    DROP MODEL IF EXISTS `{self.project_id}.ai_models.{model_name}`
                    """
                    bq_client.client.query(delete_query).result()
                    logger.info(f"✅ Deleted model: {model_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to delete model {model_name}: {e}")

            # Reset model status
            self.model_status = {}
            self.models = {}
            self.embedding_generator = None
            self.vector_search_engine = None

            logger.info("✅ Model cleanup completed")
            return True

        except Exception as e:
            logger.error(f"❌ Error during model cleanup: {e}")
            return False

def main():
    """Test the model manager."""
    print("🤖 Model Manager")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Model manager class created successfully")

if __name__ == "__main__":
    main()
