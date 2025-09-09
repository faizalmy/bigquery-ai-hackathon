#!/usr/bin/env python3
"""
Legal Information Institute (LII) Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads real legal documents from Cornell Law School's LII.
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LIIDownloader:
    """Downloader for legal documents from Legal Information Institute (LII)."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the LII downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })

        # LII base URL
        self.base_url = "https://www.law.cornell.edu"

        # Rate limiting
        self.request_delay = 1.0  # 1 second between requests

    def get_supreme_court_cases(self, max_cases: int = 100) -> List[Dict]:
        """
        Get Supreme Court cases from LII.

        Args:
            max_cases: Maximum number of cases to download

        Returns:
            List of case documents
        """
        logger.info(f"🏛️  Downloading Supreme Court cases from LII...")

        all_cases = []

        # LII Supreme Court cases URL
        scotus_url = f"{self.base_url}/supct"

        try:
            time.sleep(self.request_delay)
            response = self.session.get(scotus_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find case links
            case_links = []

            # Look for case links in various formats
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and ('supct' in href or 'cases' in href):
                    if href.startswith('/'):
                        href = self.base_url + href
                    case_links.append(href)

            # Remove duplicates and limit
            case_links = list(set(case_links))[:max_cases]

            logger.info(f"Found {len(case_links)} case links")

            # Download each case
            for i, case_url in enumerate(case_links):
                if len(all_cases) >= max_cases:
                    break

                logger.info(f"Downloading case {i+1}/{len(case_links)}: {case_url}")

                case_doc = self.download_case_document(case_url)
                if case_doc:
                    all_cases.append(case_doc)

                time.sleep(self.request_delay)

        except Exception as e:
            logger.error(f"Error downloading Supreme Court cases: {e}")

        logger.info(f"✅ Downloaded {len(all_cases)} Supreme Court cases")
        return all_cases

    def download_case_document(self, case_url: str) -> Optional[Dict]:
        """
        Download a single case document.

        Args:
            case_url: URL of the case document

        Returns:
            Case document dictionary
        """
        try:
            time.sleep(self.request_delay)
            response = self.session.get(case_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract case title
            title_elem = soup.find('h1') or soup.find('title')
            case_name = title_elem.get_text().strip() if title_elem else "Unknown Case"

            # Extract case content
            content_elem = soup.find('div', class_='case-content') or soup.find('div', class_='content')
            if not content_elem:
                content_elem = soup.find('main') or soup.find('article')

            case_content = content_elem.get_text().strip() if content_elem else ""

            # Extract metadata
            metadata = self.extract_case_metadata(soup, case_url)

            # Extract legal issues
            legal_issues = self.extract_legal_issues(case_content)

            # Generate document ID
            case_id = case_url.split('/')[-1] or 'unknown'
            document_id = f"LII_SCOTUS_{case_id}"

            case_doc = {
                'document_id': document_id,
                'source_system': 'LII',
                'document_type': 'supreme_court_case',
                'raw_content': case_content,
                'metadata': {
                    'case_name': case_name,
                    'case_url': case_url,
                    'court': 'Supreme Court of the United States',
                    'jurisdiction': 'Federal',
                    'legal_issues': legal_issues,
                    'content_length': len(case_content),
                    'word_count': len(case_content.split()) if case_content else 0,
                    'source': 'Legal Information Institute (Cornell Law School)'
                },
                'ingestion_timestamp': datetime.now().isoformat()
            }

            return case_doc

        except Exception as e:
            logger.error(f"Error downloading case document from {case_url}: {e}")
            return None

    def extract_case_metadata(self, soup: BeautifulSoup, case_url: str) -> Dict[str, Any]:
        """Extract metadata from case page."""
        metadata = {}

        # Look for case information
        case_info = soup.find('div', class_='case-info') or soup.find('div', class_='metadata')
        if case_info:
            # Extract date
            date_elem = case_info.find(text=re.compile(r'\d{4}'))
            if date_elem:
                metadata['date'] = date_elem.strip()

            # Extract case number
            case_num_elem = case_info.find(text=re.compile(r'No\.|Case No\.'))
            if case_num_elem:
                metadata['case_number'] = case_num_elem.strip()

        return metadata

    def extract_legal_issues(self, content: str) -> List[str]:
        """Extract legal issues from case content."""
        legal_issues = []

        # Common legal issue patterns
        issue_patterns = [
            'constitutional',
            'first amendment',
            'fourteenth amendment',
            'due process',
            'equal protection',
            'freedom of speech',
            'freedom of religion',
            'search and seizure',
            'jury trial',
            'criminal procedure',
            'civil rights',
            'employment',
            'contract',
            'tort',
            'administrative law'
        ]

        content_lower = content.lower()
        for pattern in issue_patterns:
            if pattern in content_lower:
                legal_issues.append(pattern.replace('_', ' ').title())

        return legal_issues[:5]  # Limit to top 5 issues

    def get_federal_regulations(self, max_regulations: int = 50) -> List[Dict]:
        """
        Get federal regulations from LII.

        Args:
            max_regulations: Maximum number of regulations to download

        Returns:
            List of regulation documents
        """
        logger.info(f"📋 Downloading federal regulations from LII...")

        all_regulations = []

        # LII Code of Federal Regulations URL
        cfr_url = f"{self.base_url}/cfr"

        try:
            time.sleep(self.request_delay)
            response = self.session.get(cfr_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find regulation links
            regulation_links = []

            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and 'cfr' in href:
                    if href.startswith('/'):
                        href = self.base_url + href
                    regulation_links.append(href)

            # Remove duplicates and limit
            regulation_links = list(set(regulation_links))[:max_regulations]

            logger.info(f"Found {len(regulation_links)} regulation links")

            # Download each regulation
            for i, reg_url in enumerate(regulation_links):
                if len(all_regulations) >= max_regulations:
                    break

                logger.info(f"Downloading regulation {i+1}/{len(regulation_links)}: {reg_url}")

                reg_doc = self.download_regulation_document(reg_url)
                if reg_doc:
                    all_regulations.append(reg_doc)

                time.sleep(self.request_delay)

        except Exception as e:
            logger.error(f"Error downloading federal regulations: {e}")

        logger.info(f"✅ Downloaded {len(all_regulations)} federal regulations")
        return all_regulations

    def download_regulation_document(self, reg_url: str) -> Optional[Dict]:
        """
        Download a single regulation document.

        Args:
            reg_url: URL of the regulation document

        Returns:
            Regulation document dictionary
        """
        try:
            time.sleep(self.request_delay)
            response = self.session.get(reg_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract regulation title
            title_elem = soup.find('h1') or soup.find('title')
            reg_title = title_elem.get_text().strip() if title_elem else "Unknown Regulation"

            # Extract regulation content
            content_elem = soup.find('div', class_='regulation-content') or soup.find('div', class_='content')
            if not content_elem:
                content_elem = soup.find('main') or soup.find('article')

            reg_content = content_elem.get_text().strip() if content_elem else ""

            # Extract metadata
            metadata = self.extract_regulation_metadata(soup, reg_url)

            # Extract legal concepts
            legal_concepts = self.extract_legal_concepts(reg_content)

            # Generate document ID
            reg_id = reg_url.split('/')[-1] or 'unknown'
            document_id = f"LII_CFR_{reg_id}"

            reg_doc = {
                'document_id': document_id,
                'source_system': 'LII',
                'document_type': 'federal_regulation',
                'raw_content': reg_content,
                'metadata': {
                    'regulation_title': reg_title,
                    'regulation_url': reg_url,
                    'jurisdiction': 'Federal',
                    'legal_concepts': legal_concepts,
                    'content_length': len(reg_content),
                    'word_count': len(reg_content.split()) if reg_content else 0,
                    'source': 'Legal Information Institute (Cornell Law School)'
                },
                'ingestion_timestamp': datetime.now().isoformat()
            }

            return reg_doc

        except Exception as e:
            logger.error(f"Error downloading regulation document from {reg_url}: {e}")
            return None

    def extract_regulation_metadata(self, soup: BeautifulSoup, reg_url: str) -> Dict[str, Any]:
        """Extract metadata from regulation page."""
        metadata = {}

        # Look for regulation information
        reg_info = soup.find('div', class_='regulation-info') or soup.find('div', class_='metadata')
        if reg_info:
            # Extract CFR title
            title_elem = reg_info.find(text=re.compile(r'Title \d+'))
            if title_elem:
                metadata['cfr_title'] = title_elem.strip()

            # Extract section number
            section_elem = reg_info.find(text=re.compile(r'§ \d+'))
            if section_elem:
                metadata['section_number'] = section_elem.strip()

        return metadata

    def extract_legal_concepts(self, content: str) -> List[str]:
        """Extract legal concepts from regulation content."""
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
            'burden of proof',
            'precedent',
            'jurisdiction',
            'venue',
            'standing',
            'administrative procedure',
            'regulatory compliance',
            'enforcement'
        ]

        content_lower = content.lower()
        for pattern in concept_patterns:
            if pattern in content_lower:
                legal_concepts.append(pattern.replace('_', ' ').title())

        return legal_concepts[:5]  # Limit to top 5 concepts

    def download_lii_documents(self, max_documents: int = 200) -> List[Dict]:
        """
        Download legal documents from LII.

        Args:
            max_documents: Maximum number of documents to download

        Returns:
            List of processed documents
        """
        logger.info(f"🚀 Starting LII document download (target: {max_documents} documents)")

        all_documents = []

        # Download Supreme Court cases (70% of documents)
        scotus_count = int(max_documents * 0.7)
        scotus_cases = self.get_supreme_court_cases(scotus_count)
        all_documents.extend(scotus_cases)

        # Download federal regulations (30% of documents)
        cfr_count = max_documents - len(all_documents)
        if cfr_count > 0:
            cfr_regulations = self.get_federal_regulations(cfr_count)
            all_documents.extend(cfr_regulations)

        logger.info(f"✅ Total LII documents processed: {len(all_documents)}")
        return all_documents

def upload_to_bigquery(documents: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload LII documents to BigQuery."""
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
    """Main function to download LII documents."""
    print("🏛️  Legal Information Institute (LII) Downloader")
    print("=" * 60)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = LIIDownloader(config)

    # Download documents
    documents = downloader.download_lii_documents(max_documents=100)

    print(f"\n📊 Download Summary:")
    print(f"   Total documents downloaded: {len(documents)}")

    if documents:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(documents, config)

        if success:
            print("✅ Successfully uploaded LII documents to BigQuery!")
        else:
            print("❌ Failed to upload LII documents to BigQuery")

        # Save to local file as backup
        output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'lii_documents.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(documents, f, indent=2)

        print(f"💾 LII documents saved to: {output_file}")

        # Print sample document info
        print(f"\n📋 Sample Documents:")
        for i, doc in enumerate(documents[:3]):
            metadata = doc['metadata']
            print(f"   {i+1}. Type: {doc['document_type']}")
            print(f"      Title: {metadata.get('case_name', metadata.get('regulation_title', 'Unknown'))}")
            print(f"      Content Length: {metadata.get('content_length', 0)} chars")
            print(f"      Source: {metadata.get('source', 'Unknown')}")
            print()
    else:
        print("❌ No LII documents were downloaded")

if __name__ == "__main__":
    main()
