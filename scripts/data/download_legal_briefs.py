#!/usr/bin/env python3
"""
Legal Briefs Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads real legal briefs from Free Law Project API.
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

class LegalBriefsDownloader:
    """Downloader for legal briefs from Free Law Project."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the legal briefs downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'application/json'
        })

        # Free Law Project API endpoints
        self.base_url = "https://www.courtlistener.com/api/rest/v3"
        self.search_url = f"{self.base_url}/search/"

        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests

    def search_legal_briefs(self, max_results: int = 100,
                           brief_types: List[str] = None) -> List[Dict]:
        """
        Search for legal briefs using Free Law Project API.

        Args:
            max_results: Maximum number of results
            brief_types: List of brief types to filter

        Returns:
            List of brief metadata
        """
        if brief_types is None:
            brief_types = ['motion', 'brief', 'response', 'reply']

        params = {
            'type': 'r',  # RECAP documents (briefs, motions, etc.)
            'order_by': 'dateFiled desc',
            'format': 'json',
            'filed_after': (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d'),
            'filed_before': datetime.now().strftime('%Y-%m-%d')
        }

        all_briefs = []
        offset = 0
        page_size = 20

        while len(all_briefs) < max_results:
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
                    if len(all_briefs) >= max_results:
                        break

                    # Filter by brief type
                    doc_type = result.get('document_type', '').lower()
                    if any(brief_type in doc_type for brief_type in brief_types):
                        brief_info = {
                            'brief_id': result.get('absolute_url', ''),
                            'case_name': result.get('caseName', ''),
                            'court': result.get('court', ''),
                            'date_filed': result.get('dateFiled', ''),
                            'date_created': result.get('date_created', ''),
                            'resource_uri': result.get('resource_uri', ''),
                            'absolute_url': result.get('absolute_url', ''),
                            'document_type': result.get('document_type', ''),
                            'attachment_number': result.get('attachment_number', 0),
                            'is_available': result.get('is_available', False),
                            'page_count': result.get('page_count', 0),
                            'docket_number': result.get('docket_number', ''),
                            'case_id': result.get('case_id', '')
                        }
                        all_briefs.append(brief_info)

                offset += page_size

                # Check if we have more results
                if len(results) < page_size:
                    break

            except Exception as e:
                logger.error(f"Error searching legal briefs: {e}")
                break

        logger.info(f"Found {len(all_briefs)} legal briefs")
        return all_briefs

    def download_brief_content(self, resource_uri: str) -> Optional[str]:
        """
        Download the full brief content.

        Args:
            resource_uri: Brief resource URI

        Returns:
            Brief content as string
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
                logger.info(f"Downloaded brief content: {len(content)} chars")
                return content
            else:
                logger.warning(f"No content found for brief: {resource_uri}")
                return None

        except Exception as e:
            logger.error(f"Error downloading brief content from {resource_uri}: {e}")
            return None

    def process_brief_data(self, brief_info: Dict, content: str) -> Dict:
        """
        Process brief data into our standard format.

        Args:
            brief_info: Brief metadata
            content: Brief content

        Returns:
            Processed brief document
        """
        # Extract legal arguments and key information
        legal_arguments = self.extract_legal_arguments(content)
        brief_type = self.classify_brief_type(content, brief_info.get('document_type', ''))

        processed_brief = {
            'document_id': f"BRIEF_{brief_info['brief_id'].split('/')[-1] if brief_info['brief_id'] else 'unknown'}",
            'source_system': 'FREE_LAW_PROJECT',
            'document_type': 'legal_brief',
            'raw_content': content,
            'metadata': {
                'case_name': brief_info.get('case_name', ''),
                'court': brief_info.get('court', ''),
                'date_filed': brief_info.get('date_filed', ''),
                'date_created': brief_info.get('date_created', ''),
                'docket_number': brief_info.get('docket_number', ''),
                'case_id': brief_info.get('case_id', ''),
                'brief_type': brief_type,
                'document_type': brief_info.get('document_type', ''),
                'attachment_number': brief_info.get('attachment_number', 0),
                'page_count': brief_info.get('page_count', 0),
                'legal_arguments': legal_arguments,
                'content_length': len(content),
                'word_count': len(content.split()) if content else 0
            },
            'ingestion_timestamp': datetime.now().isoformat()
        }

        return processed_brief

    def extract_legal_arguments(self, content: str) -> List[str]:
        """Extract legal arguments from brief content."""
        legal_arguments = []

        # Common legal argument patterns
        argument_patterns = [
            'standing',
            'jurisdiction',
            'venue',
            'statute of limitations',
            'failure to state a claim',
            'summary judgment',
            'motion to dismiss',
            'motion for summary judgment',
            'discovery',
            'evidence',
            'precedent',
            'constitutional',
            'statutory',
            'regulatory',
            'contractual',
            'tortious',
            'negligence',
            'breach of contract',
            'fraud',
            'misrepresentation'
        ]

        content_lower = content.lower()
        for pattern in argument_patterns:
            if pattern in content_lower:
                legal_arguments.append(pattern.replace('_', ' ').title())

        return legal_arguments[:10]  # Limit to top 10 arguments

    def classify_brief_type(self, content: str, doc_type: str) -> str:
        """Classify the type of legal brief."""
        content_lower = content.lower()
        doc_type_lower = doc_type.lower()

        # Classification based on content and document type
        if 'motion' in doc_type_lower or 'motion' in content_lower:
            if 'dismiss' in content_lower:
                return 'Motion to Dismiss'
            elif 'summary judgment' in content_lower:
                return 'Motion for Summary Judgment'
            elif 'discovery' in content_lower:
                return 'Discovery Motion'
            else:
                return 'Motion'
        elif 'brief' in doc_type_lower or 'brief' in content_lower:
            if 'appellate' in content_lower or 'appeal' in content_lower:
                return 'Appellate Brief'
            elif 'amicus' in content_lower:
                return 'Amicus Brief'
            elif 'trial' in content_lower:
                return 'Trial Brief'
            else:
                return 'Legal Brief'
        elif 'response' in doc_type_lower or 'response' in content_lower:
            return 'Response Brief'
        elif 'reply' in doc_type_lower or 'reply' in content_lower:
            return 'Reply Brief'
        else:
            return 'Legal Document'

    def download_legal_briefs(self, max_briefs: int = 100,
                            brief_types: List[str] = None) -> List[Dict]:
        """
        Download legal briefs from Free Law Project.

        Args:
            max_briefs: Maximum number of briefs to download
            brief_types: List of brief types to filter

        Returns:
            List of brief documents
        """
        logger.info(f"Downloading up to {max_briefs} legal briefs")

        # Search for briefs
        briefs_info = self.search_legal_briefs(max_results=max_briefs, brief_types=brief_types)

        all_briefs = []

        for i, brief_info in enumerate(briefs_info):
            if len(all_briefs) >= max_briefs:
                break

            logger.info(f"Processing brief {i+1}/{len(briefs_info)}: {brief_info.get('case_name', 'Unknown')}")

            # Download brief content
            content = self.download_brief_content(brief_info.get('resource_uri', ''))

            if content and len(content) > 500:  # Minimum content length
                # Process brief data
                processed_brief = self.process_brief_data(brief_info, content)
                all_briefs.append(processed_brief)

                logger.info(f"Processed brief: {processed_brief['document_id']}")
            else:
                logger.warning(f"Skipping brief with insufficient content: {brief_info.get('case_name', 'Unknown')}")

        logger.info(f"Total briefs processed: {len(all_briefs)}")
        return all_briefs

def upload_to_bigquery(briefs: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload legal briefs to BigQuery."""
    try:
        bq_client = BigQueryClient(config)
        project_id = config['bigquery']['project_id']
        table_id = f"{project_id}.raw_data.legal_documents"

        # Convert to BigQuery format
        rows_to_insert = []
        for brief in briefs:
            row = {
                'document_id': brief['document_id'],
                'source_system': brief['source_system'],
                'document_type': brief['document_type'],
                'raw_content': brief['raw_content'],
                'metadata': json.dumps(brief['metadata']),
                'ingestion_timestamp': brief['ingestion_timestamp']
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
                logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} briefs)")

        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {e}")
        return False

def main():
    """Main function to download legal briefs."""
    print("📋 Legal Briefs Downloader")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = LegalBriefsDownloader(config)

    # Download legal briefs
    briefs = downloader.download_legal_briefs(max_briefs=100)

    print(f"\n📊 Download Summary:")
    print(f"   Total briefs downloaded: {len(briefs)}")

    if briefs:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(briefs, config)

        if success:
            print("✅ Successfully uploaded legal briefs to BigQuery!")
        else:
            print("❌ Failed to upload legal briefs to BigQuery")

        # Save to local file as backup
        output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'legal_briefs.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(briefs, f, indent=2)

        print(f"💾 Legal briefs saved to: {output_file}")

        # Print sample brief info
        print(f"\n📋 Sample Briefs:")
        for i, brief in enumerate(briefs[:3]):
            metadata = brief['metadata']
            print(f"   {i+1}. {metadata.get('case_name', 'Unknown')}")
            print(f"      Court: {metadata.get('court', 'Unknown')}")
            print(f"      Brief Type: {metadata.get('brief_type', 'Unknown')}")
            print(f"      Legal Arguments: {', '.join(metadata.get('legal_arguments', [])[:3])}")
            print()
    else:
        print("❌ No legal briefs were downloaded")

if __name__ == "__main__":
    main()
