#!/usr/bin/env python3
"""
Free Law Project Court Cases Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads real court cases from Free Law Project API.
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

class CourtCasesDownloader:
    """Downloader for court cases from Free Law Project."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the court cases downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'application/json'
        })

        # Free Law Project API endpoints
        self.base_url = "https://www.courtlistener.com/api/rest/v3"
        self.search_url = f"{self.base_url}/search/"
        self.opinions_url = f"{self.base_url}/search/"

        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests

    def search_court_cases(self, query: str = "", max_results: int = 100,
                          court_types: List[str] = None) -> List[Dict]:
        """
        Search for court cases using Free Law Project API.

        Args:
            query: Search query
            max_results: Maximum number of results
            court_types: List of court types to filter

        Returns:
            List of case metadata
        """
        if court_types is None:
            court_types = ['f', 'c', 'b', 'a']  # Federal, Circuit, Bankruptcy, Appellate

        params = {
            'q': query,
            'stat_Precedential': 'on',
            'order_by': 'score desc',
            'format': 'json',
            'stat_Errata': 'on',
            'type': 'o',  # Opinions only
            'filed_after': (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d'),
            'filed_before': datetime.now().strftime('%Y-%m-%d')
        }

        all_cases = []
        offset = 0
        page_size = 20

        while len(all_cases) < max_results:
            params['offset'] = offset

            try:
                time.sleep(self.request_delay)
                response = self.session.get(self.search_url, params=params)
                response.raise_for_status()

                data = response.json()
                results = data.get('results', [])

                if not results:
                    break

                for result in results:
                    if len(all_cases) >= max_results:
                        break

                    # Filter by court type
                    court = result.get('court', '')
                    if any(court_type in court for court_type in court_types):
                        case_info = {
                            'case_id': result.get('absolute_url', ''),
                            'case_name': result.get('caseName', ''),
                            'court': result.get('court', ''),
                            'date_filed': result.get('dateFiled', ''),
                            'date_created': result.get('date_created', ''),
                            'resource_uri': result.get('resource_uri', ''),
                            'absolute_url': result.get('absolute_url', ''),
                            'snippet': result.get('snippet', ''),
                            'outcome': result.get('outcome', 'Unknown'),
                            'precedential': result.get('precedential', False),
                            'jurisdiction': result.get('jurisdiction', ''),
                            'docket_number': result.get('docket_number', ''),
                            'citation_count': result.get('citation_count', 0)
                        }
                        all_cases.append(case_info)

                offset += page_size

                # Check if we have more results
                if len(results) < page_size:
                    break

            except Exception as e:
                logger.error(f"Error searching court cases: {e}")
                break

        logger.info(f"Found {len(all_cases)} court cases")
        return all_cases

    def download_case_content(self, resource_uri: str) -> Optional[str]:
        """
        Download the full case content.

        Args:
            resource_uri: Case resource URI

        Returns:
            Case content as string
        """
        if not resource_uri:
            return None

        try:
            time.sleep(self.request_delay)
            response = self.session.get(resource_uri)
            response.raise_for_status()

            data = response.json()
            content = data.get('plain_text', '')

            if content:
                logger.info(f"Downloaded case content: {len(content)} chars")
                return content
            else:
                logger.warning(f"No content found for case: {resource_uri}")
                return None

        except Exception as e:
            logger.error(f"Error downloading case content from {resource_uri}: {e}")
            return None

    def process_case_data(self, case_info: Dict, content: str) -> Dict:
        """
        Process case data into our standard format.

        Args:
            case_info: Case metadata
            content: Case content

        Returns:
            Processed case document
        """
        # Extract legal issues and key information
        legal_issues = self.extract_legal_issues(content)
        case_outcome = self.determine_case_outcome(content, case_info.get('outcome', ''))

        processed_case = {
            'document_id': f"COURT_{case_info['case_id'].split('/')[-1] if case_info['case_id'] else 'unknown'}",
            'source_system': 'FREE_LAW_PROJECT',
            'document_type': 'court_case',
            'raw_content': content,
            'metadata': {
                'case_name': case_info.get('case_name', ''),
                'court': case_info.get('court', ''),
                'date_filed': case_info.get('date_filed', ''),
                'date_created': case_info.get('date_created', ''),
                'docket_number': case_info.get('docket_number', ''),
                'jurisdiction': case_info.get('jurisdiction', ''),
                'outcome': case_outcome,
                'precedential': case_info.get('precedential', False),
                'citation_count': case_info.get('citation_count', 0),
                'legal_issues': legal_issues,
                'content_length': len(content),
                'word_count': len(content.split()) if content else 0
            },
            'ingestion_timestamp': datetime.now().isoformat()
        }

        return processed_case

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
            'procedural'
        ]

        content_lower = content.lower()
        for pattern in issue_patterns:
            if pattern in content_lower:
                legal_issues.append(pattern.replace('_', ' ').title())

        return legal_issues[:5]  # Limit to top 5 issues

    def determine_case_outcome(self, content: str, outcome: str) -> str:
        """Determine case outcome from content and metadata."""
        if outcome and outcome != 'Unknown':
            return outcome

        content_lower = content.lower()

        # Look for outcome indicators
        if any(word in content_lower for word in ['affirmed', 'affirm']):
            return 'Affirmed'
        elif any(word in content_lower for word in ['reversed', 'reverse']):
            return 'Reversed'
        elif any(word in content_lower for word in ['remanded', 'remand']):
            return 'Remanded'
        elif any(word in content_lower for word in ['dismissed', 'dismiss']):
            return 'Dismissed'
        elif any(word in content_lower for word in ['granted', 'grant']):
            return 'Granted'
        elif any(word in content_lower for word in ['denied', 'deny']):
            return 'Denied'
        else:
            return 'Unknown'

    def download_court_cases(self, max_cases: int = 100,
                           court_types: List[str] = None) -> List[Dict]:
        """
        Download court cases from Free Law Project.

        Args:
            max_cases: Maximum number of cases to download
            court_types: List of court types to filter

        Returns:
            List of case documents
        """
        logger.info(f"Downloading up to {max_cases} court cases")

        # Search for cases
        cases_info = self.search_court_cases(max_results=max_cases, court_types=court_types)

        all_cases = []

        for i, case_info in enumerate(cases_info):
            if len(all_cases) >= max_cases:
                break

            logger.info(f"Processing case {i+1}/{len(cases_info)}: {case_info.get('case_name', 'Unknown')}")

            # Download case content
            content = self.download_case_content(case_info.get('resource_uri', ''))

            if content and len(content) > 500:  # Minimum content length
                # Process case data
                processed_case = self.process_case_data(case_info, content)
                all_cases.append(processed_case)

                logger.info(f"Processed case: {processed_case['document_id']}")
            else:
                logger.warning(f"Skipping case with insufficient content: {case_info.get('case_name', 'Unknown')}")

        logger.info(f"Total cases processed: {len(all_cases)}")
        return all_cases

def upload_to_bigquery(cases: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload court cases to BigQuery."""
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
    """Main function to download court cases."""
    print("⚖️  Free Law Project Court Cases Downloader")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = CourtCasesDownloader(config)

    # Download court cases
    cases = downloader.download_court_cases(max_cases=100)

    print(f"\n📊 Download Summary:")
    print(f"   Total cases downloaded: {len(cases)}")

    if cases:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(cases, config)

        if success:
            print("✅ Successfully uploaded court cases to BigQuery!")
        else:
            print("❌ Failed to upload court cases to BigQuery")

        # Save to local file as backup in organized folder structure
        output_dir = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'court_cases'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'court_cases_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(cases, f, indent=2)

        print(f"💾 Court cases saved to: {output_file}")

        # Print sample case info
        print(f"\n📋 Sample Cases:")
        for i, case in enumerate(cases[:3]):
            metadata = case['metadata']
            print(f"   {i+1}. {metadata.get('case_name', 'Unknown')}")
            print(f"      Court: {metadata.get('court', 'Unknown')}")
            print(f"      Outcome: {metadata.get('outcome', 'Unknown')}")
            print(f"      Legal Issues: {', '.join(metadata.get('legal_issues', []))}")
            print()
    else:
        print("❌ No court cases were downloaded")

if __name__ == "__main__":
    main()
