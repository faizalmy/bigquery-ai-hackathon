#!/usr/bin/env python3
"""
Legal Data Preprocessing Pipeline Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script runs the complete preprocessing pipeline for legal documents.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from data.ingestion import LegalDataIngestion
from data.preprocessing import LegalDocumentPreprocessor
from data.quality_assessment import LegalDataQualityAssessment
from data.validation import LegalDataValidator

def setup_logging():
    """Setup logging for the script."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'preprocessing_pipeline.log')
        ]
    )

def load_raw_data(data_dir: str = "data/raw") -> list:
    """
    Load raw legal documents from data directory.

    Args:
        data_dir: Directory containing raw data files

    Returns:
        List of raw legal documents
    """
    data_path = Path(data_dir)
    dataset_files = list(data_path.glob("*.json"))

    if not dataset_files:
        raise FileNotFoundError(f"No dataset files found in {data_dir}")

    all_documents = []
    for dataset_file in dataset_files:
        print(f"📁 Loading dataset: {dataset_file.name}")

        with open(dataset_file, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            documents = data
        elif isinstance(data, dict) and 'documents' in data:
            documents = data['documents']
        else:
            raise ValueError(f"Invalid dataset format in {dataset_file.name}")

        all_documents.extend(documents)
        print(f"  Loaded {len(documents)} documents")

    print(f"📊 Total documents loaded: {len(all_documents)}")
    return all_documents

def save_preprocessed_data(documents: list, output_dir: str = "data/processed"):
    """
    Save preprocessed documents to output directory.

    Args:
        documents: List of preprocessed documents
        output_dir: Output directory for processed data
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save preprocessed documents
    output_file = output_path / f"preprocessed_legal_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(documents, f, indent=2)

    print(f"💾 Saved {len(documents)} preprocessed documents to {output_file}")

    # Save summary report
    summary_file = output_path / f"preprocessing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    summary = {
        'total_documents': len(documents),
        'preprocessing_timestamp': datetime.now().isoformat(),
        'document_types': {},
        'quality_grades': {},
        'processing_errors': 0
    }

    # Calculate summary statistics
    for doc in documents:
        # Document type distribution
        doc_type = doc.get('document_type', 'unknown')
        summary['document_types'][doc_type] = summary['document_types'].get(doc_type, 0) + 1

        # Quality grade distribution
        if 'classification' in doc and 'quality_grade' in doc['classification']:
            grade = doc['classification']['quality_grade']
            summary['quality_grades'][grade] = summary['quality_grades'].get(grade, 0) + 1

        # Count processing errors
        if 'preprocessing_error' in doc:
            summary['processing_errors'] += 1

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"📋 Saved preprocessing summary to {summary_file}")
    return str(output_file), str(summary_file)

def main():
    """Main function to run the preprocessing pipeline."""
    print("🔧 Legal Data Preprocessing Pipeline - Phase 2.2")
    print("=" * 70)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Step 1: Load raw data
        print("\n📥 Step 1: Loading Raw Data")
        print("-" * 40)
        raw_documents = load_raw_data()

        # Step 2: Initialize processing components
        print("\n🔧 Step 2: Initializing Processing Components")
        print("-" * 40)
        preprocessor = LegalDocumentPreprocessor()
        quality_assessor = LegalDataQualityAssessment()
        validator = LegalDataValidator()

        print("✅ Preprocessor initialized")
        print("✅ Quality assessor initialized")
        print("✅ Validator initialized")

        # Step 3: Preprocess documents
        print(f"\n🔄 Step 3: Preprocessing {len(raw_documents)} Documents")
        print("-" * 40)

        preprocessed_documents = []
        processing_stats = {
            'total': len(raw_documents),
            'processed': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

        for i, document in enumerate(raw_documents):
            try:
                # Preprocess document
                preprocessed_doc = preprocessor.preprocess_document(document)

                # Assess quality
                quality_assessment = quality_assessor.assess_document_quality(preprocessed_doc)
                preprocessed_doc['quality_assessment'] = quality_assessment

                preprocessed_documents.append(preprocessed_doc)
                processing_stats['processed'] += 1

                # Progress update
                if (i + 1) % 50 == 0 or (i + 1) == len(raw_documents):
                    elapsed = datetime.now() - processing_stats['start_time']
                    rate = (i + 1) / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
                    print(f"  Processed {i + 1}/{len(raw_documents)} documents ({rate:.1f} docs/sec)")

            except Exception as e:
                logger.error(f"Error processing document {document.get('document_id', 'unknown')}: {e}")
                processing_stats['errors'] += 1

                # Add error document
                error_doc = document.copy()
                error_doc['preprocessing_error'] = str(e)
                error_doc['preprocessing_timestamp'] = datetime.now().isoformat()
                preprocessed_documents.append(error_doc)

        # Step 4: Validate preprocessed data
        print(f"\n🔍 Step 4: Validating Preprocessed Data")
        print("-" * 40)

        validation_report = validator.generate_validation_report(preprocessed_documents)
        print(f"  Total Documents: {validation_report['validation_summary']['total_documents']}")
        print(f"  Valid Documents: {validation_report['validation_summary']['valid_documents']}")
        print(f"  Quality Score: {validation_report['validation_summary']['quality_score']:.2f}")
        print(f"  Completeness Score: {validation_report['validation_summary']['completeness_score']:.2f}")

        # Step 5: Batch quality assessment
        print(f"\n📊 Step 5: Batch Quality Assessment")
        print("-" * 40)

        batch_assessment = quality_assessor.assess_batch_quality(preprocessed_documents)
        batch_stats = batch_assessment['batch_statistics']

        print(f"  Mean Quality Score: {batch_stats['overall_quality']['mean']:.2f}")
        print(f"  Documents Above 80%: {batch_stats['documents_above_threshold']}")
        print(f"  Quality Grade Distribution:")
        for grade, count in batch_stats['grade_distribution'].items():
            print(f"    {grade}: {count}")

        # Step 6: Save processed data
        print(f"\n💾 Step 6: Saving Processed Data")
        print("-" * 40)

        output_file, summary_file = save_preprocessed_data(preprocessed_documents)

        # Step 7: Final summary
        print(f"\n📋 Final Summary")
        print("-" * 40)

        processing_time = datetime.now() - processing_stats['start_time']

        print(f"✅ Preprocessing Pipeline Completed Successfully!")
        print(f"  Total Documents: {processing_stats['total']}")
        print(f"  Successfully Processed: {processing_stats['processed']}")
        print(f"  Processing Errors: {processing_stats['errors']}")
        print(f"  Processing Time: {processing_time.total_seconds():.1f} seconds")
        print(f"  Processing Rate: {processing_stats['processed'] / processing_time.total_seconds():.1f} docs/sec")
        print(f"  Output File: {output_file}")
        print(f"  Summary File: {summary_file}")

        # Quality assessment summary
        if batch_stats['overall_quality']['mean'] >= 0.8:
            print(f"  ✅ Overall quality requirements met (≥80%)")
        else:
            print(f"  ⚠️  Overall quality below requirements (<80%)")

        print(f"\n🎯 Ready for Phase 2.3: BigQuery AI Functions Implementation")

    except Exception as e:
        logger.error(f"Error in preprocessing pipeline: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
