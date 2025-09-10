#!/usr/bin/env python3
"""
Legal Dataset Download Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads and organizes legal document datasets for the BigQuery AI implementation.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from data.ingestion import LegalDataIngestion
from data.validation import LegalDataValidator
import logging

def setup_logging():
    """Setup logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/data_download.log')
        ]
    )

def main():
    """Main function to download and organize legal datasets."""
    print("📊 Legal Dataset Download Script - Phase 2.1")
    print("=" * 60)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize data ingestion system
        logger.info("Initializing legal data ingestion system")
        ingestion = LegalDataIngestion()

        # Load legal datasets
        logger.info("Loading legal datasets")
        datasets = ingestion.load_legal_datasets()

        # Initialize validator
        logger.info("Initializing data validator")
        validator = LegalDataValidator()

        # Validate datasets
        for dataset_name, dataset_info in datasets.items():
            logger.info(f"Validating dataset: {dataset_name}")
            documents = dataset_info['documents']

            # Generate validation report
            validation_report = validator.generate_validation_report(documents)

            # Print validation results
            print(f"\n📋 Dataset: {dataset_name}")
            print(f"  Documents: {validation_report['validation_summary']['total_documents']}")
            print(f"  Valid: {validation_report['validation_summary']['valid_documents']}")
            print(f"  Quality Score: {validation_report['validation_summary']['quality_score']:.2f}")
            print(f"  Completeness Score: {validation_report['validation_summary']['completeness_score']:.2f}")

            # Check if quality meets requirements
            quality_score = validation_report['validation_summary']['quality_score']
            if quality_score >= 0.8:
                print(f"  ✅ Quality requirements met (≥80%)")
            else:
                print(f"  ⚠️  Quality below requirements (<80%)")
                print(f"  Recommendations:")
                for rec in validation_report['recommendations']:
                    print(f"    - {rec}")

        # Print summary
        total_docs = sum(info['count'] for info in datasets.values())
        print(f"\n📊 Summary:")
        print(f"  Total datasets: {len(datasets)}")
        print(f"  Total documents: {total_docs}")
        print(f"  Data directory: {ingestion.data_dir}")

        if total_docs >= 500:
            print(f"  ✅ Minimum document count met (≥500)")
        else:
            print(f"  ⚠️  Below minimum document count (<500)")

        print(f"\n✅ Legal dataset download and validation completed successfully")

    except Exception as e:
        logger.error(f"Error in legal dataset download: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
