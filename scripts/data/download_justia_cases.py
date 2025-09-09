#!/usr/bin/env python3
"""
Justia Legal Database Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads recent court cases from Justia.com legal database.
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
from bs4 import BeautifulSoup
import re

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JustiaDownloader:
    """Downloader for court cases from Justia.com."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Justia downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })

        # Justia.com endpoints
        self.base_url = "https://www.justia.com"
        self.search_url = f"{self.base_url}/search"
        self.cases_url = f"{self.base_url}/cases"

        # Rate limiting
        self.request_delay = 1.0  # 1 second between requests

    def search_recent_cases(self, max_results: int = 500) -> List[Dict]:
        """
        Search for recent court cases on Justia.

        Args:
            max_results: Maximum number of cases to find

        Returns:
            List of case metadata
        """
        logger.info(f"🔍 Searching for recent cases on Justia...")

        all_cases = []

        # Search for recent cases by date
        search_queries = [
            "recent court decisions",
            "federal court opinions",
            "appellate court decisions",
            "supreme court cases",
            "district court opinions"
        ]

        for query in search_queries:
            if len(all_cases) >= max_results:
                break

            logger.info(f"Searching for: {query}")

            try:
                # Search parameters
                params = {
                    'q': query,
                    'type': 'cases',
                    'sort': 'date',
                    'date_range': '1y'  # Last year
                }

                time.sleep(self.request_delay)
                response = self.session.get(self.search_url, params=params)
                response.raise_for_status()

                # Parse search results
                soup = BeautifulSoup(response.content, 'html.parser')
                case_links = self.extract_case_links(soup)

                for link in case_links:
                    if len(all_cases) >= max_results:
                        break

                    case_info = self.extract_case_info(link)
                    if case_info:
                        all_cases.append(case_info)

                logger.info(f"Found {len(case_links)} cases for query: {query}")

            except Exception as e:
                logger.error(f"Error searching for '{query}': {e}")
                continue

        logger.info(f"✅ Total cases found: {len(all_cases)}")
        return all_cases

    def extract_case_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract case links from search results page."""
        links = []

        # Look for case result links
        result_links = soup.find_all('a', href=re.compile(r'/cases/'))

        for link in result_links:
            href = link.get('href')
            if href and '/cases/' in href:
                if href.startswith('/'):
                    href = self.base_url + href
                links.append(href)

        return list(set(links))  # Remove duplicates

    def extract_case_info(self, case_url: str) -> Optional[Dict]:
        """
        Extract case information from a case page.

        Args:
            case_url: URL of the case page

        Returns:
            Case information dictionary
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
            metadata = self.extract_case_metadata(soup)

            # Extract legal issues
            legal_issues = self.extract_legal_issues(case_content)

            case_info = {
                'case_url': case_url,
                'case_name': case_name,
                'case_content': case_content,
                'metadata': metadata,
                'legal_issues': legal_issues,
                'content_length': len(case_content),
                'word_count': len(case_content.split()) if case_content else 0
            }

            return case_info

        except Exception as e:
            logger.error(f"Error extracting case info from {case_url}: {e}")
            return None

    def extract_case_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from case page."""
        metadata = {}

        # Look for court information
        court_elem = soup.find(text=re.compile(r'Court|District|Circuit'))
        if court_elem:
            metadata['court'] = court_elem.strip()

        # Look for date information
        date_elem = soup.find(text=re.compile(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}'))
        if date_elem:
            metadata['date'] = date_elem.strip()

        # Look for case number
        case_num_elem = soup.find(text=re.compile(r'Case No\.|Docket No\.|No\.'))
        if case_num_elem:
            metadata['case_number'] = case_num_elem.strip()

        # Look for jurisdiction
        jurisdiction_elem = soup.find(text=re.compile(r'Federal|State|District|Circuit'))
        if jurisdiction_elem:
            metadata['jurisdiction'] = jurisdiction_elem.strip()

        return metadata

    def extract_legal_issues(self, content: str) -> List[str]:
        """Extract legal issues from case content."""
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
            'procedural',
            'due process',
            'equal protection',
            'freedom of speech',
            'search and seizure',
            'jury trial'
        ]

        content_lower = content.lower()
        for pattern in issue_patterns:
            if pattern in content_lower:
                legal_issues.append(pattern.replace('_', ' ').title())

        return legal_issues[:5]  # Limit to top 5 issues

    def process_case_data(self, case_info: Dict) -> Dict:
        """
        Process case data into our standard format.

        Args:
            case_info: Raw case information

        Returns:
            Processed case document
        """
        # Generate document ID from URL
        case_id = case_info['case_url'].split('/')[-1] or 'unknown'
        document_id = f"JUSTIA_{case_id}"

        processed_case = {
            'document_id': document_id,
            'source_system': 'JUSTIA',
            'document_type': 'court_case',
            'raw_content': case_info['case_content'],
            'metadata': {
                'case_name': case_info['case_name'],
                'case_url': case_info['case_url'],
                'court': case_info['metadata'].get('court', ''),
                'date': case_info['metadata'].get('date', ''),
                'case_number': case_info['metadata'].get('case_number', ''),
                'jurisdiction': case_info['metadata'].get('jurisdiction', ''),
                'legal_issues': case_info['legal_issues'],
                'content_length': case_info['content_length'],
                'word_count': case_info['word_count'],
                'source': 'Justia Legal Database'
            },
            'ingestion_timestamp': datetime.now().isoformat()
        }

        return processed_case

    def download_justia_cases(self, max_cases: int = 500) -> List[Dict]:
        """
        Download court cases from Justia.

        Args:
            max_cases: Maximum number of cases to download

        Returns:
            List of case documents
        """
        logger.info(f"🚀 Starting Justia case download (target: {max_cases} cases)")

        # Search for recent cases
        case_infos = self.search_recent_cases(max_cases)

        all_cases = []

        for i, case_info in enumerate(case_infos):
            if len(all_cases) >= max_cases:
                break

            logger.info(f"Processing case {i+1}/{len(case_infos)}: {case_info.get('case_name', 'Unknown')}")

            # Process case data
            processed_case = self.process_case_data(case_info)

            # Only include cases with sufficient content
            if processed_case['raw_content'] and len(processed_case['raw_content']) > 500:
                all_cases.append(processed_case)
                logger.info(f"Added case: {processed_case['document_id']}")
            else:
                logger.warning(f"Skipping case with insufficient content: {case_info.get('case_name', 'Unknown')}")

        logger.info(f"✅ Total Justia cases processed: {len(all_cases)}")
        return all_cases

def upload_to_bigquery(cases: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload Justia cases to BigQuery."""
    try:
        bq_client = BigQueryClient(config)
        project_id = config['bigquery']['project_id']
        table_id = f"{project_id}.raw_data.legal_documents"

        # Convert to BigQuery format
        rows_to_insert = []
        for case in cases:
            row = {
                'document_id': case['document_id'],
                'source_system': case['source_system'],
                'document_type': case['document_type'],
                'raw_content': case['raw_content'],
                'metadata': json.dumps(case['metadata']),
                'ingestion_timestamp': case['ingestion_timestamp']
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
                logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} cases)")

        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {e}")
        return False

def main():
    """Main function to download Justia cases."""
    print("⚖️  Justia Legal Database Downloader")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = JustiaDownloader(config)

    # Download cases
    cases = downloader.download_justia_cases(max_cases=200)

    print(f"\n📊 Download Summary:")
    print(f"   Total cases downloaded: {len(cases)}")

    if cases:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(cases, config)

        if success:
            print("✅ Successfully uploaded Justia cases to BigQuery!")
        else:
            print("❌ Failed to upload Justia cases to BigQuery")

        # Save to local file as backup
        output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'justia_cases.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(cases, f, indent=2)

        print(f"💾 Justia cases saved to: {output_file}")

        # Print sample case info
        print(f"\n📋 Sample Cases:")
        for i, case in enumerate(cases[:3]):
            metadata = case['metadata']
            print(f"   {i+1}. {metadata.get('case_name', 'Unknown')}")
            print(f"      Court: {metadata.get('court', 'Unknown')}")
            print(f"      Jurisdiction: {metadata.get('jurisdiction', 'Unknown')}")
            print(f"      Legal Issues: {', '.join(metadata.get('legal_issues', [])[:3])}")
            print()
    else:
        print("❌ No Justia cases were downloaded")

if __name__ == "__main__":
    main()
