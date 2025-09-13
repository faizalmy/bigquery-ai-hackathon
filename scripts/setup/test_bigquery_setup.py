#!/usr/bin/env python3
"""
BigQuery Setup Validation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script validates the complete BigQuery setup including datasets, tables, and AI model access.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
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

class BigQueryValidator:
    """Validates BigQuery setup and configuration."""

    def __init__(self, config_path: str = "config/bigquery_config.yaml"):
        """Initialize BigQuery validator."""
        self.config_path = config_path
        self.client = BigQueryClient(config_path)
        self.config = self.client.get_config()
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'project_id': self.config['project']['id'],
            'tests': {},
            'overall_status': 'PENDING'
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests."""
        try:
            logger.info("🧪 Starting BigQuery setup validation...")

            # Test 1: Connection
            self._test_connection()

            # Test 2: Datasets
            self._test_datasets()

            # Test 3: Tables
            self._test_tables()

            # Test 4: AI Models
            self._test_ai_models()

            # Test 5: Permissions
            self._test_permissions()

            # Test 6: Sample Queries
            self._test_sample_queries()

            # Determine overall status
            self._determine_overall_status()

            # Generate report
            self._generate_report()

            return self.validation_results

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.validation_results['overall_status'] = 'FAILED'
            self.validation_results['error'] = str(e)
            return self.validation_results

    def _test_connection(self):
        """Test BigQuery connection."""
        try:
            logger.info("Testing BigQuery connection...")

            if self.client.connect():
                self.validation_results['tests']['connection'] = {
                    'status': 'PASS',
                    'message': 'Successfully connected to BigQuery'
                }
                logger.info("✅ Connection test passed")
            else:
                self.validation_results['tests']['connection'] = {
                    'status': 'FAIL',
                    'message': 'Failed to connect to BigQuery'
                }
                logger.error("❌ Connection test failed")

        except Exception as e:
            self.validation_results['tests']['connection'] = {
                'status': 'FAIL',
                'message': f'Connection test error: {e}'
            }
            logger.error(f"❌ Connection test error: {e}")

    def _test_datasets(self):
        """Test dataset existence and accessibility."""
        try:
            logger.info("Testing datasets...")

            project_id = self.config['project']['id']
            main_dataset_name = list(self.config['datasets'].keys())[0]
            main_dataset_config = self.config['datasets'][main_dataset_name]

            datasets_to_test = [main_dataset_name]

            # Add subdatasets
            if 'subdatasets' in main_dataset_config:
                for subdataset_name in main_dataset_config['subdatasets'].keys():
                    datasets_to_test.append(f"{main_dataset_name}_{subdataset_name}")

            dataset_results = {}
            all_passed = True

            for dataset_name in datasets_to_test:
                dataset_id = f"{project_id}.{dataset_name}"

                if self.client._dataset_exists(dataset_id):
                    dataset_results[dataset_name] = {
                        'status': 'PASS',
                        'message': f'Dataset {dataset_id} exists and is accessible'
                    }
                    logger.info(f"✅ Dataset {dataset_name} test passed")
                else:
                    dataset_results[dataset_name] = {
                        'status': 'FAIL',
                        'message': f'Dataset {dataset_id} not found'
                    }
                    logger.error(f"❌ Dataset {dataset_name} test failed")
                    all_passed = False

            self.validation_results['tests']['datasets'] = {
                'status': 'PASS' if all_passed else 'FAIL',
                'results': dataset_results,
                'message': f'Tested {len(datasets_to_test)} datasets'
            }

        except Exception as e:
            self.validation_results['tests']['datasets'] = {
                'status': 'FAIL',
                'message': f'Dataset test error: {e}'
            }
            logger.error(f"❌ Dataset test error: {e}")

    def _test_tables(self):
        """Test table existence and schema."""
        try:
            logger.info("Testing tables...")

            project_id = self.config['project']['id']
            table_results = {}
            all_passed = True

            for table_name, table_config in self.config['tables'].items():
                table_id = f"{project_id}.{table_config['dataset']}.{table_name}"

                if self.client._table_exists(table_id):
                    table_results[table_name] = {
                        'status': 'PASS',
                        'message': f'Table {table_id} exists and is accessible'
                    }
                    logger.info(f"✅ Table {table_name} test passed")
                else:
                    table_results[table_name] = {
                        'status': 'FAIL',
                        'message': f'Table {table_id} not found'
                    }
                    logger.error(f"❌ Table {table_name} test failed")
                    all_passed = False

            self.validation_results['tests']['tables'] = {
                'status': 'PASS' if all_passed else 'FAIL',
                'results': table_results,
                'message': f'Tested {len(self.config["tables"])} tables'
            }

        except Exception as e:
            self.validation_results['tests']['tables'] = {
                'status': 'FAIL',
                'message': f'Table test error: {e}'
            }
            logger.error(f"❌ Table test error: {e}")

    def _test_ai_models(self):
        """Test AI model access."""
        try:
            logger.info("Testing AI models...")

            # Test Gemini Pro model
            gemini_test = self._test_gemini_model()

            # Test text embedding model
            embedding_test = self._test_embedding_model()

            ai_model_results = {
                'gemini_pro': gemini_test,
                'text_embedding': embedding_test
            }

            all_passed = all(result['status'] == 'PASS' for result in ai_model_results.values())

            self.validation_results['tests']['ai_models'] = {
                'status': 'PASS' if all_passed else 'FAIL',
                'results': ai_model_results,
                'message': 'Tested AI model access'
            }

        except Exception as e:
            self.validation_results['tests']['ai_models'] = {
                'status': 'FAIL',
                'message': f'AI model test error: {e}'
            }
            logger.error(f"❌ AI model test error: {e}")

    def _test_gemini_model(self) -> Dict[str, Any]:
        """Test Gemini Pro model access."""
        try:
            test_query = """
            SELECT ML.GENERATE_TEXT(
                MODEL `gemini-pro`,
                'Test query for model validation'
            ) as test_result
            """

            query_job = self.client.execute_ai_query(test_query)
            results = query_job.result()

            return {
                'status': 'PASS',
                'message': 'Gemini Pro model accessible and working'
            }

        except Exception as e:
            return {
                'status': 'FAIL',
                'message': f'Gemini Pro model test failed: {e}'
            }

    def _test_embedding_model(self) -> Dict[str, Any]:
        """Test text embedding model access."""
        try:
            test_query = """
            SELECT ML.GENERATE_EMBEDDING(
                MODEL `text-embedding-preview-0409`,
                'Test text for embedding validation'
            ) as test_embedding
            """

            query_job = self.client.execute_ai_query(test_query)
            results = query_job.result()

            return {
                'status': 'PASS',
                'message': 'Text embedding model accessible and working'
            }

        except Exception as e:
            return {
                'status': 'FAIL',
                'message': f'Text embedding model test failed: {e}'
            }

    def _test_permissions(self):
        """Test service account permissions."""
        try:
            logger.info("Testing permissions...")

            # Test basic query execution
            test_query = "SELECT 1 as test_value"
            query_job = self.client.execute_query(test_query)
            results = query_job.result()

            self.validation_results['tests']['permissions'] = {
                'status': 'PASS',
                'message': 'Service account has proper BigQuery permissions'
            }
            logger.info("✅ Permissions test passed")

        except Exception as e:
            self.validation_results['tests']['permissions'] = {
                'status': 'FAIL',
                'message': f'Permissions test failed: {e}'
            }
            logger.error(f"❌ Permissions test failed: {e}")

    def _test_sample_queries(self):
        """Test sample BigQuery AI queries."""
        try:
            logger.info("Testing sample queries...")

            # Test 1: Basic AI query
            ai_query = """
            SELECT ML.GENERATE_TEXT(
                MODEL `gemini-pro`,
                'What is the capital of France?'
            ) as answer
            """

            query_job = self.client.execute_ai_query(ai_query)
            results = query_job.result()

            self.validation_results['tests']['sample_queries'] = {
                'status': 'PASS',
                'message': 'Sample AI queries executed successfully'
            }
            logger.info("✅ Sample queries test passed")

        except Exception as e:
            self.validation_results['tests']['sample_queries'] = {
                'status': 'FAIL',
                'message': f'Sample queries test failed: {e}'
            }
            logger.error(f"❌ Sample queries test failed: {e}")

    def _determine_overall_status(self):
        """Determine overall validation status."""
        test_results = self.validation_results['tests']

        if all(test['status'] == 'PASS' for test in test_results.values()):
            self.validation_results['overall_status'] = 'SUCCESS'
        else:
            self.validation_results['overall_status'] = 'FAILED'

    def _generate_report(self):
        """Generate validation report."""
        try:
            # Save detailed report
            report_file = f"data/processed/bigquery_setup_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)

            with open(report_file, 'w') as f:
                json.dump(self.validation_results, f, indent=2)

            logger.info(f"Validation report saved to: {report_file}")

            # Print summary
            self._print_summary()

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")

    def _print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("🔍 BIGQUERY SETUP VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Project ID: {self.validation_results['project_id']}")
        print(f"Timestamp: {self.validation_results['timestamp']}")
        print(f"Overall Status: {self.validation_results['overall_status']}")
        print("\nTest Results:")

        for test_name, test_result in self.validation_results['tests'].items():
            status_icon = "✅" if test_result['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {test_name.upper()}: {test_result['status']}")
            print(f"     {test_result['message']}")

        print("\n" + "=" * 60)

        if self.validation_results['overall_status'] == 'SUCCESS':
            print("🎉 All tests passed! BigQuery setup is ready.")
        else:
            print("⚠️ Some tests failed. Please check the issues above.")


def main():
    """Main execution function."""
    try:
        print("🧪 BigQuery Setup Validation")
        print("=" * 40)

        # Initialize validator
        validator = BigQueryValidator()

        # Run all tests
        results = validator.run_all_tests()

        # Return appropriate exit code
        if results['overall_status'] == 'SUCCESS':
            return 0
        else:
            return 1

    except Exception as e:
        logger.error(f"Validation script failed: {e}")
        print(f"\n❌ Validation script failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
