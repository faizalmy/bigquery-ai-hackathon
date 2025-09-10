#!/usr/bin/env python3
"""
Legal Data Validation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script validates downloaded legal document datasets for quality assurance.
"""

import sys
import json
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from data.validation import LegalDataValidator
import logging

def setup_logging():
    """Setup logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/data_validation.log')
        ]
    )

def load_dataset_from_file(file_path: str) -> list:
    """
    Load dataset from JSON file.

    Args:
        file_path: Path to the dataset file

    Returns:
        List of documents
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'documents' in data:
            return data['documents']
        else:
            raise ValueError("Invalid dataset format")

    except Exception as e:
        raise Exception(f"Error loading dataset from {file_path}: {e}")

def main():
    """Main function to validate legal datasets."""
    print("🔍 Legal Data Validation Script - Phase 2.1")
    print("=" * 60)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize validator
        logger.info("Initializing data validator")
        validator = LegalDataValidator()

        # Find dataset files
        data_dir = Path("data/raw")
        dataset_files = list(data_dir.glob("*.json"))

        if not dataset_files:
            print("❌ No dataset files found in data/raw directory")
            return 1

        print(f"📁 Found {len(dataset_files)} dataset files")

        # Validate each dataset
        total_documents = 0
        total_valid = 0
        overall_quality_score = 0.0

        for dataset_file in dataset_files:
            print(f"\n📋 Validating: {dataset_file.name}")

            try:
                # Load dataset
                documents = load_dataset_from_file(str(dataset_file))

                # Generate validation report
                validation_report = validator.generate_validation_report(documents)

                # Print results
                summary = validation_report['validation_summary']
                print(f"  Documents: {summary['total_documents']}")
                print(f"  Valid: {summary['valid_documents']}")
                print(f"  Quality Score: {summary['quality_score']:.2f}")
                print(f"  Completeness Score: {summary['completeness_score']:.2f}")

                # Document type distribution
                print(f"  Document Types:")
                for doc_type, count in summary['document_type_distribution'].items():
                    print(f"    {doc_type}: {count}")

                # Quality assessment
                if summary['quality_score'] >= 0.8:
                    print(f"  ✅ Quality requirements met (≥80%)")
                else:
                    print(f"  ⚠️  Quality below requirements (<80%)")

                # Recommendations
                if validation_report['recommendations']:
                    print(f"  💡 Recommendations:")
                    for rec in validation_report['recommendations']:
                        print(f"    - {rec}")

                # Update totals
                total_documents += summary['total_documents']
                total_valid += summary['valid_documents']
                overall_quality_score += summary['quality_score']

            except Exception as e:
                logger.error(f"Error validating {dataset_file.name}: {e}")
                print(f"  ❌ Error: {e}")

        # Print overall summary
        print(f"\n📊 Overall Validation Summary:")
        print(f"  Total Datasets: {len(dataset_files)}")
        print(f"  Total Documents: {total_documents}")
        print(f"  Total Valid: {total_valid}")

        if len(dataset_files) > 0:
            avg_quality_score = overall_quality_score / len(dataset_files)
            print(f"  Average Quality Score: {avg_quality_score:.2f}")

            if avg_quality_score >= 0.8:
                print(f"  ✅ Overall quality requirements met (≥80%)")
            else:
                print(f"  ⚠️  Overall quality below requirements (<80%)")

        # Check minimum document count
        if total_documents >= 500:
            print(f"  ✅ Minimum document count met (≥500)")
        else:
            print(f"  ⚠️  Below minimum document count (<500)")

        print(f"\n✅ Legal data validation completed successfully")

    except Exception as e:
        logger.error(f"Error in data validation: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
