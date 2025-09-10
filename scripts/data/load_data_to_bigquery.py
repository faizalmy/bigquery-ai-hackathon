#!/usr/bin/env python3
"""
BigQuery Data Loading Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script loads processed legal documents and AI processing results into BigQuery
with proper schema, partitioning, and indexing for optimal performance.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from data.bigquery_loader import BigQueryDataLoader
from ai.models.bigquery_ai_functions import BigQueryAIFunctions
from data.preprocessing import LegalDocumentPreprocessor
from utils.logging_config import setup_logging

def setup_logging():
    """Setup logging for the script."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'bigquery_data_loading.log')
        ]
    )

def load_processed_documents() -> list:
    """
    Load processed legal documents from the latest preprocessing run.

    Returns:
        List of processed legal documents
    """
    print("📥 Loading processed legal documents...")

    processed_data_dir = Path("data/processed")
    if not processed_data_dir.exists():
        print("❌ No processed data directory found. Please run preprocessing first.")
        return []

    # Find the latest preprocessed documents file
    preprocessed_files = list(processed_data_dir.glob("preprocessed_legal_documents_*.json"))
    if not preprocessed_files:
        print("❌ No preprocessed documents found. Please run preprocessing first.")
        return []

    # Get the most recent file
    latest_file = max(preprocessed_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Loading from: {latest_file}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        print(f"✅ Loaded {len(documents)} processed documents")
        return documents

    except Exception as e:
        print(f"❌ Error loading processed documents: {e}")
        return []

def process_documents_with_ai(documents: list) -> list:
    """
    Process documents with BigQuery AI functions.

    Args:
        documents: List of processed legal documents

    Returns:
        List of AI processing results
    """
    print("🤖 Processing documents with BigQuery AI functions...")

    # Initialize AI functions
    ai_functions = BigQueryAIFunctions("faizal-hackathon")

    # Process documents in batches
    batch_size = 50
    all_ai_results = []

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")

        try:
            batch_results = ai_functions.batch_process_documents(batch)
            all_ai_results.extend(batch_results)

            # Log progress
            successful = sum(1 for r in batch_results if r.get('success', False))
            print(f"    Batch completed: {successful}/{len(batch)} successful")

        except Exception as e:
            print(f"    ❌ Error processing batch: {e}")
            # Add error results for failed batch
            for doc in batch:
                error_result = {
                    'document_id': doc.get('document_id'),
                    'success': False,
                    'error': str(e),
                    'processing_timestamp': datetime.now().isoformat()
                }
                all_ai_results.append(error_result)

    print(f"✅ AI processing completed: {len(all_ai_results)} results")
    return all_ai_results

def load_data_to_bigquery(documents: list, ai_results: list) -> bool:
    """
    Load documents and AI results into BigQuery.

    Args:
        documents: List of processed legal documents
        ai_results: List of AI processing results

    Returns:
        True if loading was successful, False otherwise
    """
    print("📊 Loading data into BigQuery...")

    # Initialize BigQuery data loader
    loader = BigQueryDataLoader("faizal-hackathon")

    # Create dataset and tables
    print("🔧 Setting up BigQuery dataset and tables...")
    if not loader.create_dataset():
        print("❌ Failed to create dataset")
        return False

    # Create all tables
    tables_created = 0
    for table_name in loader.tables.keys():
        if loader.create_table(table_name):
            print(f"✅ Table {table_name} created")
            tables_created += 1
        else:
            print(f"❌ Failed to create table {table_name}")

    if tables_created != len(loader.tables):
        print(f"⚠️ Only {tables_created}/{len(loader.tables)} tables created")

    # Load legal documents
    print("\n📄 Loading legal documents...")
    if loader.load_legal_documents(documents):
        print(f"✅ Loaded {len(documents)} legal documents")
    else:
        print("❌ Failed to load legal documents")
        return False

    # Load document metadata
    print("\n📋 Loading document metadata...")
    if loader.load_document_metadata(documents):
        print(f"✅ Loaded metadata for {len(documents)} documents")
    else:
        print("❌ Failed to load document metadata")
        return False

    # Load AI processing results
    print("\n🤖 Loading AI processing results...")
    if loader.load_ai_processing_results(ai_results):
        print(f"✅ Loaded {len(ai_results)} AI processing results")
    else:
        print("❌ Failed to load AI processing results")
        return False

    # Create performance indexes
    print("\n🔍 Creating performance indexes...")
    if loader.create_indexes():
        print("✅ Performance indexes created")
    else:
        print("⚠️ Index creation failed (may already exist)")

    return True

def generate_data_lineage_report(documents: list, ai_results: list) -> dict:
    """
    Generate data lineage documentation.

    Args:
        documents: List of processed legal documents
        ai_results: List of AI processing results

    Returns:
        Data lineage report dictionary
    """
    print("📋 Generating data lineage report...")

    # Analyze data flow
    total_documents = len(documents)
    successful_ai_results = sum(1 for r in ai_results if r.get('success', False))
    failed_ai_results = total_documents - successful_ai_results

    # Analyze document types
    document_types = {}
    for doc in documents:
        doc_type = doc.get('document_type', 'unknown')
        document_types[doc_type] = document_types.get(doc_type, 0) + 1

    # Analyze AI function usage
    ai_function_usage = {}
    for result in ai_results:
        if result.get('success', False):
            ai_results_data = result.get('ai_results', {})
            for function_name in ai_results_data.keys():
                ai_function_usage[function_name] = ai_function_usage.get(function_name, 0) + 1

    # Generate report
    lineage_report = {
        'report_timestamp': datetime.now().isoformat(),
        'data_flow': {
            'total_documents_processed': total_documents,
            'documents_loaded_to_bigquery': total_documents,
            'ai_processing_successful': successful_ai_results,
            'ai_processing_failed': failed_ai_results,
            'ai_processing_success_rate': (successful_ai_results / total_documents * 100) if total_documents > 0 else 0
        },
        'document_types': document_types,
        'ai_function_usage': ai_function_usage,
        'bigquery_tables': {
            'legal_documents': {
                'description': 'Processed legal documents with metadata and content',
                'partitioning': 'ingestion_date',
                'clustering': ['document_type', 'jurisdiction']
            },
            'document_metadata': {
                'description': 'Extracted metadata from legal documents',
                'partitioning': 'extraction_date',
                'clustering': ['document_type', 'urgency_level']
            },
            'ai_processing_results': {
                'description': 'Results from BigQuery AI functions processing',
                'partitioning': 'processing_date',
                'clustering': ['ai_function', 'document_type']
            }
        },
        'data_quality_metrics': {
            'completeness_score': sum(doc.get('metadata', {}).get('completeness_score', 0) for doc in documents) / total_documents if total_documents > 0 else 0,
            'quality_score': sum(doc.get('metadata', {}).get('quality_score', 0) for doc in documents) / total_documents if total_documents > 0 else 0
        }
    }

    return lineage_report

def save_lineage_report(report: dict):
    """
    Save data lineage report to file.

    Args:
        report: Data lineage report dictionary
    """
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"data_lineage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"💾 Data lineage report saved to: {output_file}")

def main():
    """Main function to run BigQuery data loading."""
    print("📊 BigQuery Data Loading Script - Phase 2.4")
    print("=" * 70)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Step 1: Load processed documents
        documents = load_processed_documents()
        if not documents:
            print("❌ No documents to load. Exiting.")
            return 1

        # Step 2: Process documents with AI functions
        ai_results = process_documents_with_ai(documents)

        # Step 3: Load data into BigQuery
        if not load_data_to_bigquery(documents, ai_results):
            print("❌ Data loading failed. Exiting.")
            return 1

        # Step 4: Generate data lineage report
        lineage_report = generate_data_lineage_report(documents, ai_results)
        save_lineage_report(lineage_report)

        # Print final summary
        print(f"\n📋 Data Loading Summary")
        print("=" * 70)
        print(f"  Documents Processed: {lineage_report['data_flow']['total_documents_processed']}")
        print(f"  Documents Loaded: {lineage_report['data_flow']['documents_loaded_to_bigquery']}")
        print(f"  AI Processing Success Rate: {lineage_report['data_flow']['ai_processing_success_rate']:.1f}%")
        print(f"  Document Types: {len(lineage_report['document_types'])}")
        print(f"  AI Functions Used: {len(lineage_report['ai_function_usage'])}")
        print(f"  BigQuery Tables Created: {len(lineage_report['bigquery_tables'])}")

        print(f"\n📊 Document Type Distribution:")
        for doc_type, count in lineage_report['document_types'].items():
            print(f"    {doc_type}: {count}")

        print(f"\n🤖 AI Function Usage:")
        for function_name, count in lineage_report['ai_function_usage'].items():
            print(f"    {function_name}: {count}")

        print(f"\n✅ BigQuery data loading completed successfully!")
        print(f"🎯 Ready for Phase 2.5: AI Function Integration Testing")

    except Exception as e:
        logger.error(f"Error in BigQuery data loading: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
