#!/usr/bin/env python3
"""
Working AI Model Deployment Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script deploys working AI models using BigQuery's current capabilities.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.bigquery_client import BigQueryClient
from config import load_config
from ai.models.bigquery_ai_models import BigQueryAIModels

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def deploy_ai_models():
    """Deploy working AI models using BigQuery's current capabilities."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        logger.info(f"🚀 Starting AI model deployment for project: {project_id}")

        # Initialize BigQuery AI models
        ai_models = BigQueryAIModels(project_id)

        # Create temp dataset for model operations
        logger.info("📦 Setting up BigQuery AI models...")
        success = ai_models.create_temp_dataset(bq_client)

        if success:
            logger.info("✅ BigQuery AI models setup completed successfully")
            return True
        else:
            logger.error("❌ BigQuery AI models setup failed")
            return False

    except Exception as e:
        logger.error(f"❌ Fatal error during AI model setup: {e}")
        return False

def test_ai_models():
    """Test the working AI models with sample data."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize AI models
        ai_models = BigQueryAIModels(project_id)

        logger.info("🧪 Testing BigQuery AI models...")

        # Sample legal document for testing
        sample_document = """
        IN THE SUPREME COURT OF THE UNITED STATES
        No. 22-1234

        JOHN DOE, Petitioner,
        v.
        JANE SMITH, Respondent.

        On Writ of Certiorari to the United States Court of Appeals for the Ninth Circuit

        BRIEF FOR PETITIONER

        This case presents a question of constitutional law regarding the First Amendment rights of public employees. The petitioner, John Doe, was terminated from his position as a public school teacher after expressing his political views on social media. The district court granted summary judgment in favor of the respondent, and the court of appeals affirmed. We respectfully request that this Court reverse the decision below.

        The central issue is whether a public employee's speech on matters of public concern is protected under the First Amendment when made through social media platforms. This Court has long recognized that public employees do not forfeit their First Amendment rights by virtue of their employment.
        """

        test_results = {}

        # Test 1: Legal Data Extraction
        try:
            logger.info("🧪 Testing Legal Data Extraction...")
            extraction_result = ai_models.extract_legal_data(bq_client, sample_document)
            test_results['legal_extraction'] = extraction_result

            if 'error' not in extraction_result:
                logger.info("✅ Legal Data Extraction: SUCCESS")
                logger.info(f"   📊 Extracted: {extraction_result['extracted_data']['legal_issue']}")
                logger.info(f"   🏛️  Court: {extraction_result['extracted_data']['court']}")
            else:
                logger.error(f"❌ Legal Data Extraction: {extraction_result['error']}")

        except Exception as e:
            logger.error(f"❌ Legal Data Extraction failed: {e}")
            test_results['legal_extraction'] = {'error': str(e)}

        # Test 2: Document Summarization
        try:
            logger.info("🧪 Testing Document Summarization...")
            summary_result = ai_models.summarize_document(bq_client, sample_document)
            test_results['document_summarization'] = summary_result

            if 'error' not in summary_result:
                logger.info("✅ Document Summarization: SUCCESS")
                logger.info(f"   📄 Type: {summary_result['summary']['document_type']}")
                logger.info(f"   🎯 Topic: {summary_result['summary']['primary_topic']}")
                logger.info(f"   ⚡ Urgency: {summary_result['summary']['urgency_level']}")
            else:
                logger.error(f"❌ Document Summarization: {summary_result['error']}")

        except Exception as e:
            logger.error(f"❌ Document Summarization failed: {e}")
            test_results['document_summarization'] = {'error': str(e)}

        # Test 3: Document Classification
        try:
            logger.info("🧪 Testing Document Classification...")
            classification_result = ai_models.classify_document(bq_client, sample_document)
            test_results['document_classification'] = classification_result

            if 'error' not in classification_result:
                logger.info("✅ Document Classification: SUCCESS")
                logger.info(f"   📋 Type: {classification_result['classification']['document_type']}")
                logger.info(f"   🎯 Domain: {classification_result['classification']['legal_domain']}")
                logger.info(f"   📊 Confidence: {classification_result['classification']['confidence_score']}")
            else:
                logger.error(f"❌ Document Classification: {classification_result['error']}")

        except Exception as e:
            logger.error(f"❌ Document Classification failed: {e}")
            test_results['document_classification'] = {'error': str(e)}

        # Print test results summary
        logger.info("📊 Test Results Summary:")
        successful_tests = 0
        for test_name, result in test_results.items():
            if 'error' not in result:
                logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                successful_tests += 1
            else:
                logger.error(f"❌ {test_name.replace('_', ' ').title()}: FAILED")

        logger.info(f"🎯 Overall: {successful_tests}/{len(test_results)} tests passed")

        return test_results

    except Exception as e:
        logger.error(f"❌ Fatal error during AI model testing: {e}")
        return {}

def main():
    """Main deployment function."""
    print("🤖 BigQuery AI Models - Working Implementation")
    print("=" * 60)

    # Deploy AI models
    deployment_success = deploy_ai_models()

    if deployment_success:
        print("\n🧪 Testing AI models...")
        test_results = test_ai_models()

        if test_results:
            successful_tests = sum(1 for result in test_results.values() if 'error' not in result)
            total_tests = len(test_results)

            if successful_tests == total_tests:
                print("\n🎉 All AI models working successfully!")
                print("✅ Phase 2 AI models are ready for production use")
            else:
                print(f"\n⚠️  {successful_tests}/{total_tests} AI models working")
                print("🔧 Some models need further development")
        else:
            print("\n❌ AI model testing failed")
    else:
        print("\n❌ AI model deployment failed")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
