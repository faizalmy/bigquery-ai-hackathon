#!/usr/bin/env python3
"""
Master Legal Data Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script orchestrates downloading all types of legal documents from real sources.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Import our downloaders
from download_sec_contracts import SECContractsDownloader
from download_court_cases import CourtCasesDownloader
from download_legal_briefs import LegalBriefsDownloader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalDataIngestionPipeline:
    """Master pipeline for downloading all types of legal documents."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the ingestion pipeline."""
        self.config = config
        self.bq_client = BigQueryClient(config)

        # Initialize downloaders
        self.sec_downloader = SECContractsDownloader(config)
        self.court_downloader = CourtCasesDownloader(config)
        self.briefs_downloader = LegalBriefsDownloader(config)

        # Data collection targets
        self.targets = {
            'sec_contracts': 200,
            'court_cases': 150,
            'legal_briefs': 100
        }

    def remove_duplicate_companies(self, company_ciks: List[str]) -> List[str]:
        """
        Remove duplicate company CIKs from the list.

        Args:
            company_ciks: List of company CIKs (may contain duplicates)

        Returns:
            List of unique company CIKs
        """
        original_count = len(company_ciks)
        unique_ciks = list(dict.fromkeys(company_ciks))  # Preserves order
        duplicates_removed = original_count - len(unique_ciks)

        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate company CIKs")
            logger.info(f"Original count: {original_count}, Unique count: {len(unique_ciks)}")

        return unique_ciks

    def get_company_name(self, cik: str) -> str:
        """
        Get company name from CIK.

        Args:
            cik: Company CIK

        Returns:
            Company name
        """
        company_names = {
            '0000320193': 'Apple Inc.',
            '0000789019': 'Microsoft Corporation',
            '0001018724': 'Amazon.com Inc.',
            '0001652044': 'Google (Alphabet Inc.)',
            '0001318605': 'Tesla Inc.',
            '0001067983': 'Berkshire Hathaway',
        }
        return company_names.get(cik, f'Company {cik}')

    def download_sec_contracts(self, max_contracts: int = 200) -> List[Dict]:
        """Download SEC contracts."""
        logger.info("🏢 Downloading SEC contracts...")

        # Get popular company CIKs
        company_ciks = [
            '0000320193',  # Apple Inc.
            '0000789019',  # Microsoft Corporation
            '0001018724',  # Amazon.com Inc.
            '0001652044',  # Google (Alphabet Inc.)
            '0001318605',  # Tesla Inc.
            '0001067983',  # Berkshire Hathaway
        ]

        # Remove any duplicates (safety check)
        company_ciks = self.remove_duplicate_companies(company_ciks)

        all_contracts = []
        contracts_per_company = max_contracts // len(company_ciks)

        for cik in company_ciks:
            try:
                company_name = self.get_company_name(cik)
                contracts = self.sec_downloader.download_company_contracts(cik, max_contracts=contracts_per_company)
                all_contracts.extend(contracts)
                logger.info(f"Downloaded {len(contracts)} contracts from {company_name} (CIK: {cik})")
            except Exception as e:
                company_name = self.get_company_name(cik)
                logger.error(f"Error downloading contracts for {company_name} (CIK: {cik}): {e}")
                continue

        logger.info(f"✅ Total SEC contracts downloaded: {len(all_contracts)}")
        return all_contracts

    def download_court_cases(self, max_cases: int = 150) -> List[Dict]:
        """Download court cases."""
        logger.info("⚖️  Downloading court cases...")

        try:
            cases = self.court_downloader.download_court_cases(max_cases=max_cases)
            logger.info(f"✅ Total court cases downloaded: {len(cases)}")
            return cases
        except Exception as e:
            logger.error(f"Error downloading court cases: {e}")
            return []

    def download_legal_briefs(self, max_briefs: int = 100) -> List[Dict]:
        """Download legal briefs."""
        logger.info("📋 Downloading legal briefs...")

        try:
            briefs = self.briefs_downloader.download_legal_briefs(max_briefs=max_briefs)
            logger.info(f"✅ Total legal briefs downloaded: {len(briefs)}")
            return briefs
        except Exception as e:
            logger.error(f"Error downloading legal briefs: {e}")
            return []

    def upload_to_bigquery(self, documents: List[Dict], document_type: str) -> bool:
        """Upload documents to BigQuery."""
        try:
            project_id = self.config['bigquery']['project_id']
            table_id = f"{project_id}.raw_data.legal_documents"

            # Convert to BigQuery format
            rows_to_insert = []
            for doc in documents:
                row = {
                    'document_id': doc['document_id'],
                    'source_system': doc['source_system'],
                    'document_type': doc['document_type'],
                    'raw_content': doc['raw_content'],
                    'metadata': json.dumps(doc['metadata']),
                    'ingestion_timestamp': doc['ingestion_timestamp']
                }
                rows_to_insert.append(row)

            # Get table reference
            table_ref = self.bq_client.client.get_table(table_id)

            # Insert data in batches
            batch_size = 100
            for i in range(0, len(rows_to_insert), batch_size):
                batch = rows_to_insert[i:i + batch_size]
                errors = self.bq_client.client.insert_rows_json(table_ref, batch)

                if errors:
                    logger.error(f"Errors inserting {document_type} batch {i//batch_size + 1}: {errors}")
                else:
                    logger.info(f"Successfully inserted {document_type} batch {i//batch_size + 1} ({len(batch)} documents)")

            return True

        except Exception as e:
            logger.error(f"Error uploading {document_type} to BigQuery: {e}")
            return False

    def save_to_local(self, documents: List[Dict], document_type: str) -> str:
        """Save documents to local file."""
        output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / f'{document_type}.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(documents, f, indent=2)

        logger.info(f"💾 {document_type} saved to: {output_file}")
        return str(output_file)

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete data ingestion pipeline."""
        logger.info("🚀 Starting Legal Data Ingestion Pipeline")
        logger.info("=" * 60)

        results = {
            'start_time': datetime.now().isoformat(),
            'documents_downloaded': {},
            'upload_success': {},
            'files_saved': {},
            'errors': []
        }

        # Download SEC contracts
        try:
            contracts = self.download_sec_contracts(self.targets['sec_contracts'])
            results['documents_downloaded']['sec_contracts'] = len(contracts)

            if contracts:
                # Upload to BigQuery
                upload_success = self.upload_to_bigquery(contracts, 'SEC Contracts')
                results['upload_success']['sec_contracts'] = upload_success

                # Save to local file
                file_path = self.save_to_local(contracts, 'sec_contracts')
                results['files_saved']['sec_contracts'] = file_path
        except Exception as e:
            error_msg = f"Error processing SEC contracts: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        # Download court cases
        try:
            cases = self.download_court_cases(self.targets['court_cases'])
            results['documents_downloaded']['court_cases'] = len(cases)

            if cases:
                # Upload to BigQuery
                upload_success = self.upload_to_bigquery(cases, 'Court Cases')
                results['upload_success']['court_cases'] = upload_success

                # Save to local file
                file_path = self.save_to_local(cases, 'court_cases')
                results['files_saved']['court_cases'] = file_path
        except Exception as e:
            error_msg = f"Error processing court cases: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        # Download legal briefs
        try:
            briefs = self.download_legal_briefs(self.targets['legal_briefs'])
            results['documents_downloaded']['legal_briefs'] = len(briefs)

            if briefs:
                # Upload to BigQuery
                upload_success = self.upload_to_bigquery(briefs, 'Legal Briefs')
                results['upload_success']['legal_briefs'] = upload_success

                # Save to local file
                file_path = self.save_to_local(briefs, 'legal_briefs')
                results['files_saved']['legal_briefs'] = file_path
        except Exception as e:
            error_msg = f"Error processing legal briefs: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        results['end_time'] = datetime.now().isoformat()

        # Print summary
        self.print_summary(results)

        return results

    def print_summary(self, results: Dict[str, Any]):
        """Print pipeline execution summary."""
        print("\n" + "=" * 60)
        print("📊 LEGAL DATA INGESTION PIPELINE SUMMARY")
        print("=" * 60)

        total_documents = sum(results['documents_downloaded'].values())
        successful_uploads = sum(1 for success in results['upload_success'].values() if success)

        print(f"⏱️  Start Time: {results['start_time']}")
        print(f"⏱️  End Time: {results['end_time']}")
        print(f"📄 Total Documents Downloaded: {total_documents}")
        print(f"✅ Successful Uploads: {successful_uploads}/{len(results['upload_success'])}")

        print(f"\n📋 Document Breakdown:")
        for doc_type, count in results['documents_downloaded'].items():
            upload_status = "✅" if results['upload_success'].get(doc_type, False) else "❌"
            print(f"   {doc_type.replace('_', ' ').title()}: {count} documents {upload_status}")

        if results['errors']:
            print(f"\n❌ Errors Encountered:")
            for error in results['errors']:
                print(f"   - {error}")

        print(f"\n💾 Files Saved:")
        for doc_type, file_path in results['files_saved'].items():
            print(f"   {doc_type.replace('_', ' ').title()}: {file_path}")

        print(f"\n🎯 Next Steps:")
        print(f"   1. Verify data in BigQuery console")
        print(f"   2. Run data quality checks")
        print(f"   3. Process documents with AI models")
        print(f"   4. Create document embeddings")
        print(f"   5. Build analytics dashboards")

def main():
    """Main function to run the legal data ingestion pipeline."""
    print("🚀 Legal Document Intelligence Platform - Data Ingestion")
    print("=" * 70)

    # Load configuration
    config = load_config()

    # Initialize pipeline
    pipeline = LegalDataIngestionPipeline(config)

    # Run the complete pipeline
    results = pipeline.run_full_pipeline()

    # Save results summary
    results_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'ingestion_results.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Pipeline results saved to: {results_file}")

    # Return success status
    total_documents = sum(results['documents_downloaded'].values())
    return total_documents > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
