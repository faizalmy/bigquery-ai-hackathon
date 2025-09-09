#!/usr/bin/env python3
"""
OpenLegalData Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads structured legal documents from OpenLegalData.org.
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenLegalDataDownloader:
    """Downloader for structured legal documents from OpenLegalData."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the OpenLegalData downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        # OpenLegalData API endpoints
        self.base_url = "https://www.openlegaldata.org"
        self.api_url = f"{self.base_url}/api"

        # Available endpoints
        self.endpoints = {
            'cases': f"{self.api_url}/cases/",
            'courts': f"{self.api_url}/courts/",
            'laws': f"{self.api_url}/laws/",
            'references': f"{self.api_url}/references/",
            'citations': f"{self.api_url}/citations/"
        }

        # Rate limiting
        self.request_delay = 0.5  # 500ms between requests

    def search_legal_documents(self, endpoint: str, max_results: int = 100) -> List[Dict]:
        """
        Search for legal documents from OpenLegalData API.

        Args:
            endpoint: API endpoint to search
            max_results: Maximum number of results

        Returns:
            List of document metadata
        """
        logger.info(f"🔍 Searching {endpoint} on OpenLegalData...")

        all_documents = []
        page = 1
        page_size = 50

        while len(all_documents) < max_results:
            try:
                params = {
                    'page': page,
                    'page_size': min(page_size, max_results - len(all_documents)),
                    'format': 'json'
                }

                time.sleep(self.request_delay)
                response = self.session.get(endpoint, params=params)
                response.raise_for_status()

                data = response.json()
                results = data.get('results', [])

                if not results:
                    break

                for result in results:
                    if len(all_documents) >= max_results:
                        break

                    # Process document based on endpoint type
                    if 'cases' in endpoint:
                        document = self.process_case_document(result)
                    elif 'laws' in endpoint:
                        document = self.process_law_document(result)
                    elif 'references' in endpoint:
                        document = self.process_reference_document(result)
                    else:
                        document = self.process_generic_document(result, endpoint)

                    if document:
                        all_documents.append(document)

                page += 1

                # Check if we have more pages
                if not data.get('next'):
                    break

            except Exception as e:
                logger.error(f"Error searching {endpoint}: {e}")
                break

        logger.info(f"✅ Found {len(all_documents)} documents from {endpoint}")
        return all_documents

    def process_case_document(self, case_data: Dict) -> Optional[Dict]:
        """Process a case document from OpenLegalData."""
        try:
            # Extract case information
            case_id = case_data.get('id', 'unknown')
            case_name = case_data.get('name', 'Unknown Case')
            case_text = case_data.get('text', '')

            # Extract metadata
            metadata = {
                'case_name': case_name,
                'case_id': case_id,
                'court': case_data.get('court', {}).get('name', '') if case_data.get('court') else '',
                'date': case_data.get('date', ''),
                'file_number': case_data.get('file_number', ''),
                'ecli': case_data.get('ecli', ''),
                'jurisdiction': case_data.get('jurisdiction', ''),
                'content_length': len(case_text),
                'word_count': len(case_text.split()) if case_text else 0,
                'source': 'OpenLegalData'
            }

            # Extract legal issues
            legal_issues = self.extract_legal_issues(case_text)
            metadata['legal_issues'] = legal_issues

            document = {
                'document_id': f"OPENLEGAL_CASE_{case_id}",
                'source_system': 'OPENLEGAL_DATA',
                'document_type': 'court_case',
                'raw_content': case_text,
                'metadata': metadata,
                'ingestion_timestamp': datetime.now().isoformat()
            }

            return document

        except Exception as e:
            logger.error(f"Error processing case document: {e}")
            return None

    def process_law_document(self, law_data: Dict) -> Optional[Dict]:
        """Process a law document from OpenLegalData."""
        try:
            # Extract law information
            law_id = law_data.get('id', 'unknown')
            law_title = law_data.get('title', 'Unknown Law')
            law_text = law_data.get('text', '')

            # Extract metadata
            metadata = {
                'law_title': law_title,
                'law_id': law_id,
                'law_type': law_data.get('law_type', ''),
                'date': law_data.get('date', ''),
                'jurisdiction': law_data.get('jurisdiction', ''),
                'content_length': len(law_text),
                'word_count': len(law_text.split()) if law_text else 0,
                'source': 'OpenLegalData'
            }

            # Extract legal concepts
            legal_concepts = self.extract_legal_concepts(law_text)
            metadata['legal_concepts'] = legal_concepts

            document = {
                'document_id': f"OPENLEGAL_LAW_{law_id}",
                'source_system': 'OPENLEGAL_DATA',
                'document_type': 'legal_law',
                'raw_content': law_text,
                'metadata': metadata,
                'ingestion_timestamp': datetime.now().isoformat()
            }

            return document

        except Exception as e:
            logger.error(f"Error processing law document: {e}")
            return None

    def process_reference_document(self, ref_data: Dict) -> Optional[Dict]:
        """Process a reference document from OpenLegalData."""
        try:
            # Extract reference information
            ref_id = ref_data.get('id', 'unknown')
            ref_text = ref_data.get('text', '')

            # Extract metadata
            metadata = {
                'reference_id': ref_id,
                'reference_type': ref_data.get('reference_type', ''),
                'date': ref_data.get('date', ''),
                'content_length': len(ref_text),
                'word_count': len(ref_text.split()) if ref_text else 0,
                'source': 'OpenLegalData'
            }

            document = {
                'document_id': f"OPENLEGAL_REF_{ref_id}",
                'source_system': 'OPENLEGAL_DATA',
                'document_type': 'legal_reference',
                'raw_content': ref_text,
                'metadata': metadata,
                'ingestion_timestamp': datetime.now().isoformat()
            }

            return document

        except Exception as e:
            logger.error(f"Error processing reference document: {e}")
            return None

    def process_generic_document(self, data: Dict, endpoint: str) -> Optional[Dict]:
        """Process a generic document from OpenLegalData."""
        try:
            doc_id = data.get('id', 'unknown')
            doc_text = data.get('text', data.get('content', ''))

            # Extract metadata
            metadata = {
                'document_id': doc_id,
                'endpoint': endpoint,
                'content_length': len(doc_text),
                'word_count': len(doc_text.split()) if doc_text else 0,
                'source': 'OpenLegalData'
            }

            document = {
                'document_id': f"OPENLEGAL_GEN_{doc_id}",
                'source_system': 'OPENLEGAL_DATA',
                'document_type': 'legal_document',
                'raw_content': doc_text,
                'metadata': metadata,
                'ingestion_timestamp': datetime.now().isoformat()
            }

            return document

        except Exception as e:
            logger.error(f"Error processing generic document: {e}")
            return None

    def extract_legal_issues(self, content: str) -> List[str]:
        """Extract legal issues from content."""
        legal_issues = []

        # Common legal issue patterns
        issue_patterns = [
            'constitutional',
            'contract',
            'tort',
            'criminal',
            'civil rights',
            'employment',
            'intellectual property',
            'antitrust',
            'securities',
            'bankruptcy',
            'family law',
            'immigration',
            'environmental',
            'administrative',
            'procedural'
        ]

        content_lower = content.lower()
        for pattern in issue_patterns:
            if pattern in content_lower:
                legal_issues.append(pattern.replace('_', ' ').title())

        return legal_issues[:5]  # Limit to top 5 issues

    def extract_legal_concepts(self, content: str) -> List[str]:
        """Extract legal concepts from content."""
        legal_concepts = []

        # Common legal concept patterns
        concept_patterns = [
            'liability',
            'damages',
            'negligence',
            'breach of contract',
            'statute of limitations',
            'due process',
            'equal protection',
            'freedom of speech',
            'search and seizure',
            'jury trial',
            'burden of proof',
            'precedent',
            'jurisdiction',
            'venue',
            'standing'
        ]

        content_lower = content.lower()
        for pattern in concept_patterns:
            if pattern in content_lower:
                legal_concepts.append(pattern.replace('_', ' ').title())

        return legal_concepts[:5]  # Limit to top 5 concepts

    def download_openlegal_data(self, max_documents: int = 1000) -> List[Dict]:
        """
        Download structured legal documents from OpenLegalData.

        Args:
            max_documents: Maximum number of documents to download

        Returns:
            List of processed documents
        """
        logger.info(f"🚀 Starting OpenLegalData download (target: {max_documents} documents)")

        all_documents = []
        documents_per_endpoint = max_documents // len(self.endpoints)

        for endpoint_name, endpoint_url in self.endpoints.items():
            if len(all_documents) >= max_documents:
                break

            logger.info(f"Downloading from {endpoint_name}...")

            try:
                documents = self.search_legal_documents(endpoint_url, documents_per_endpoint)
                all_documents.extend(documents)

                logger.info(f"Downloaded {len(documents)} documents from {endpoint_name}")

            except Exception as e:
                logger.error(f"Error downloading from {endpoint_name}: {e}")
                continue

        logger.info(f"✅ Total OpenLegalData documents processed: {len(all_documents)}")
        return all_documents

def upload_to_bigquery(documents: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload OpenLegalData documents to BigQuery."""
    try:
        bq_client = BigQueryClient(config)
        project_id = config['bigquery']['project_id']
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
        table_ref = bq_client.client.get_table(table_id)

        # Insert data in batches
        batch_size = 100
        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i + batch_size]
            errors = bq_client.client.insert_rows_json(table_ref, batch)

            if errors:
                logger.error(f"Errors inserting batch {i//batch_size + 1}: {errors}")
            else:
                logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} documents)")

        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {e}")
        return False

def main():
    """Main function to download OpenLegalData documents."""
    print("📊 OpenLegalData Downloader")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = OpenLegalDataDownloader(config)

    # Download documents
    documents = downloader.download_openlegal_data(max_documents=200)

    print(f"\n📊 Download Summary:")
    print(f"   Total documents downloaded: {len(documents)}")

    if documents:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(documents, config)

        if success:
            print("✅ Successfully uploaded OpenLegalData documents to BigQuery!")
        else:
            print("❌ Failed to upload OpenLegalData documents to BigQuery")

        # Save to local file as backup in organized folder structure
        output_dir = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'openlegal_data'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'openlegal_data_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(documents, f, indent=2)

        print(f"💾 OpenLegalData documents saved to: {output_file}")

        # Print sample document info
        print(f"\n📋 Sample Documents:")
        for i, doc in enumerate(documents[:3]):
            metadata = doc['metadata']
            print(f"   {i+1}. Type: {doc['document_type']}")
            print(f"      ID: {metadata.get('document_id', 'Unknown')}")
            print(f"      Content Length: {metadata.get('content_length', 0)} chars")
            print(f"      Source: {metadata.get('source', 'Unknown')}")
            print()
    else:
        print("❌ No OpenLegalData documents were downloaded")

if __name__ == "__main__":
    main()
