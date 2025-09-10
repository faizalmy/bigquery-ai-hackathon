#!/usr/bin/env python3
"""
AI Model Deployment Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script deploys all AI models to BigQuery ML.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient
from ai.model_manager import ModelManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIModelDeployer:
    """AI model deployment orchestrator."""

    def __init__(self, config: dict):
        """Initialize the AI model deployer."""
        self.config = config
        self.bq_client = BigQueryClient(config)
        self.project_id = config['bigquery']['project_id']
        self.model_manager = ModelManager(self.project_id)

    def create_ai_models_dataset(self) -> bool:
        """Create the AI models dataset in BigQuery."""
        try:
            logger.info("Creating AI models dataset...")

            dataset_id = f"{self.project_id}.ai_models"
            try:
                self.bq_client.client.get_dataset(dataset_id)
                logger.info(f"Dataset {dataset_id} already exists")
                return True
            except Exception:
                self.bq_client.client.create_dataset(dataset_id)
                logger.info(f"Created dataset {dataset_id}")
                return True

        except Exception as e:
            logger.error(f"Error creating AI models dataset: {e}")
            return False

    def deploy_all_models(self) -> dict:
        """Deploy all AI models."""
        logger.info("🚀 Starting AI Model Deployment")
        logger.info("=" * 60)

        results = {
            'start_time': None,
            'end_time': None,
            'dataset_creation': False,
            'model_deployment': {},
            'overall_success': False,
            'errors': []
        }

        try:
            results['start_time'] = datetime.now().isoformat()

            # Step 1: Create AI models dataset
            logger.info("📋 Creating AI models dataset...")
            dataset_created = self.create_ai_models_dataset()
            results['dataset_creation'] = dataset_created

            if not dataset_created:
                results['errors'].append("Failed to create AI models dataset")
                return results

            # Step 2: Deploy all models
            logger.info("🤖 Deploying all AI models...")
            deployment_results = self.model_manager.deploy_models(self.bq_client)
            results['model_deployment'] = deployment_results

            # Check overall success
            results['overall_success'] = deployment_results.get('overall_success', False)

            results['end_time'] = datetime.now().isoformat()

        except Exception as e:
            error_msg = f"Deployment error: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['end_time'] = datetime.now().isoformat()

        # Print summary
        self.print_deployment_summary(results)
        return results

    def print_deployment_summary(self, results: dict):
        """Print deployment summary."""
        print("\n📊 AI Model Deployment Summary")
        print("=" * 50)
        print(f"Dataset creation: {'✅' if results['dataset_creation'] else '❌'}")
        print(f"Overall success: {'✅' if results['overall_success'] else '❌'}")

        if 'model_deployment' in results:
            deployment = results['model_deployment']

            if 'initialization' in deployment:
                print(f"\n🔧 Model Initialization:")
                for model, status in deployment['initialization'].items():
                    print(f"   {model}: {'✅' if status else '❌'}")

            if 'creation' in deployment:
                print(f"\n🏗️  Model Creation:")
                for model, status in deployment['creation'].items():
                    print(f"   {model}: {'✅' if status else '❌'}")

            if 'testing' in deployment:
                print(f"\n🧪 Model Testing:")
                for model, test_result in deployment['testing'].items():
                    status = test_result.get('status', 'unknown')
                    print(f"   {model}: {'✅' if status == 'success' else '❌'} {status}")

        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   - {error}")

        if results['start_time'] and results['end_time']:
            start = datetime.fromisoformat(results['start_time'])
            end = datetime.fromisoformat(results['end_time'])
            duration = (end - start).total_seconds()
            print(f"\n⏱️  Deployment duration: {duration:.2f} seconds")

    def test_deployed_models(self) -> dict:
        """Test the deployed models."""
        logger.info("🧪 Testing deployed models...")

        try:
            test_results = self.model_manager.test_all_models(self.bq_client)

            print("\n🧪 Model Test Results")
            print("=" * 30)

            for model_name, result in test_results.items():
                status = result.get('status', 'unknown')
                print(f"{model_name}: {'✅' if status == 'success' else '❌'} {status}")

                if status == 'success' and 'result' in result:
                    # Show a preview of the result
                    result_preview = str(result['result'])[:100] + '...' if len(str(result['result'])) > 100 else str(result['result'])
                    print(f"   Result: {result_preview}")

            return test_results

        except Exception as e:
            logger.error(f"Error testing models: {e}")
            return {'error': str(e)}

    def get_model_status(self) -> dict:
        """Get the status of all models."""
        logger.info("📊 Getting model status...")

        try:
            status = self.model_manager.get_model_status()
            info = self.model_manager.get_model_info(self.bq_client)

            print("\n📊 Model Status and Information")
            print("=" * 40)

            for model_name, model_status in status.items():
                print(f"{model_name}: {model_status}")

                if model_name in info:
                    model_info = info[model_name]
                    if 'error' not in model_info:
                        print(f"   Model Path: {model_info.get('model_path', 'N/A')}")
                        print(f"   Model Type: {model_info.get('model_type', 'N/A')}")
                    else:
                        print(f"   Error: {model_info['error']}")

            return {
                'status': status,
                'info': info
            }

        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return {'error': str(e)}

def main():
    """Main function to deploy AI models."""
    print("🤖 AI Model Deployment")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize deployer
    deployer = AIModelDeployer(config)

    # Deploy all models
    results = deployer.deploy_all_models()

    if results['overall_success']:
        print("\n✅ AI model deployment completed successfully!")

        # Test deployed models
        deployer.test_deployed_models()

        # Show model status
        deployer.get_model_status()

    else:
        print("\n❌ AI model deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    from datetime import datetime
    main()
