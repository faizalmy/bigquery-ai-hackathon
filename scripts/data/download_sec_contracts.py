#!/usr/bin/env python3
"""
SEC EDGAR Contracts Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads real legal contracts from SEC EDGAR database.
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
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SECContractsDownloader:
    """Downloader for SEC EDGAR contracts and filings."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the SEC downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'application/json, text/html, */*'
        })

        # SEC EDGAR API endpoints
        self.base_url = "https://www.sec.gov"
        self.api_url = "https://data.sec.gov"
        self.edgar_url = "https://www.sec.gov/Archives/edgar"

        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests
        self.max_retries = 3
        self.retry_delay = 1.0  # 1 second between retries

    def get_company_filings(self, cik: str, form_types: List[str] = None,
                          start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get company filings from SEC EDGAR.

        Args:
            cik: Company CIK (Central Index Key)
            form_types: List of form types to filter (e.g., ['10-K', '8-K', '10-Q'])
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of filing metadata
        """
        if form_types is None:
            form_types = ['10-K', '8-K', '10-Q', 'DEF 14A']

        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # SEC EDGAR submissions API
        url = f"{self.api_url}/submissions/CIK{cik.zfill(10)}.json"

        for attempt in range(self.max_retries):
            try:
                time.sleep(self.request_delay)
                response = self.session.get(url)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}. Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}: {e}")
                    return []

        try:
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})

            # Filter filings
            filtered_filings = []
            forms = filings.get('form', [])
            filing_dates = filings.get('filingDate', [])
            accession_numbers = filings.get('accessionNumber', [])
            primary_documents = filings.get('primaryDocument', [])

            for i, form in enumerate(forms):
                if form in form_types:
                    filing_date = filing_dates[i] if i < len(filing_dates) else None

                    # Check date range
                    if filing_date and start_date <= filing_date <= end_date:
                        filing_info = {
                            'cik': cik,
                            'company_name': data.get('name', 'Unknown'),
                            'form_type': form,
                            'filing_date': filing_date,
                            'accession_number': accession_numbers[i] if i < len(accession_numbers) else None,
                            'primary_document': primary_documents[i] if i < len(primary_documents) else None
                        }
                        filtered_filings.append(filing_info)

            logger.info(f"Found {len(filtered_filings)} filings for CIK {cik}")
            return filtered_filings

        except Exception as e:
            logger.error(f"Error fetching filings for CIK {cik}: {e}")
            return []

    def download_filing_content(self, accession_number: str, primary_document: str) -> Optional[str]:
        """
        Download the actual filing content.

        Args:
            accession_number: SEC accession number
            primary_document: Primary document filename

        Returns:
            Document content as string
        """
        if not accession_number or not primary_document:
            return None

        # Convert accession number to file path format
        # e.g., 0001234567-23-000001 -> 000123456723000001
        accession_path = accession_number.replace('-', '')

        # Construct file URL
        file_url = f"{self.edgar_url}/data/{accession_path}/{primary_document}"

        try:
            time.sleep(self.request_delay)
            response = self.session.get(file_url)
            response.raise_for_status()

            # Try to decode as text
            content = response.text
            logger.info(f"Downloaded filing: {primary_document} ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"Error downloading filing {primary_document}: {e}")
            return None

    def extract_contracts_from_filing(self, content: str, filing_info: Dict) -> List[Dict]:
        """
        Extract contract information from filing content.

        Args:
            content: Filing content
            filing_info: Filing metadata

        Returns:
            List of contract documents
        """
        contracts = []

        # Look for contract exhibits (EX-10, EX-99, etc.)
        contract_patterns = [
            'EX-10',  # Material contracts
            'EX-99',  # Other exhibits
            'EX-4',   # Instruments defining rights
            'EX-2'    # Merger agreements
        ]

        # Split content into sections
        sections = content.split('\n')
        current_section = []
        current_exhibit = None

        for line in sections:
            line = line.strip()

            # Check if this is an exhibit header
            if any(pattern in line for pattern in contract_patterns):
                # Save previous section if it was a contract
                if current_section and current_exhibit:
                    contract_content = '\n'.join(current_section)
                    if len(contract_content) > 1000:  # Minimum contract size
                        contract = {
                            'document_id': f"SEC_{filing_info['accession_number']}_{current_exhibit}",
                            'source_system': 'SEC_EDGAR',
                            'document_type': 'contract',
                            'raw_content': contract_content,
                            'metadata': {
                                'company_name': filing_info['company_name'],
                                'cik': filing_info['cik'],
                                'form_type': filing_info['form_type'],
                                'filing_date': filing_info['filing_date'],
                                'accession_number': filing_info['accession_number'],
                                'exhibit_type': current_exhibit,
                                'content_length': len(contract_content),
                                'word_count': len(contract_content.split())
                            },
                            'ingestion_timestamp': datetime.now().isoformat()
                        }
                        contracts.append(contract)

                # Start new exhibit
                current_exhibit = line
                current_section = [line]
            else:
                current_section.append(line)

        # Handle last section
        if current_section and current_exhibit:
            contract_content = '\n'.join(current_section)
            if len(contract_content) > 1000:
                contract = {
                    'document_id': f"SEC_{filing_info['accession_number']}_{current_exhibit}",
                    'source_system': 'SEC_EDGAR',
                    'document_type': 'contract',
                    'raw_content': contract_content,
                    'metadata': {
                        'company_name': filing_info['company_name'],
                        'cik': filing_info['cik'],
                        'form_type': filing_info['form_type'],
                        'filing_date': filing_info['filing_date'],
                        'accession_number': filing_info['accession_number'],
                        'exhibit_type': current_exhibit,
                        'content_length': len(contract_content),
                        'word_count': len(contract_content.split())
                    },
                    'ingestion_timestamp': datetime.now().isoformat()
                }
                contracts.append(contract)

        return contracts

    def download_company_contracts(self, cik: str, max_contracts: int = 50) -> List[Dict]:
        """
        Download contracts for a specific company.

        Args:
            cik: Company CIK
            max_contracts: Maximum number of contracts to download

        Returns:
            List of contract documents
        """
        logger.info(f"Downloading contracts for CIK: {cik}")

        # Get recent filings
        filings = self.get_company_filings(cik)

        all_contracts = []
        contracts_downloaded = 0

        for filing in filings:
            if contracts_downloaded >= max_contracts:
                break

            # Download filing content
            content = self.download_filing_content(
                filing['accession_number'],
                filing['primary_document']
            )

            if content:
                # Extract contracts from filing
                contracts = self.extract_contracts_from_filing(content, filing)

                for contract in contracts:
                    if contracts_downloaded >= max_contracts:
                        break
                    all_contracts.append(contract)
                    contracts_downloaded += 1

                logger.info(f"Extracted {len(contracts)} contracts from {filing['form_type']} filing")

        logger.info(f"Total contracts downloaded for CIK {cik}: {len(all_contracts)}")
        return all_contracts

def get_popular_company_ciks() -> List[str]:
    """Get CIKs for popular companies with lots of filings."""
    return [
        '0000320193',  # Apple Inc.
        '0000789019',  # Microsoft Corporation
        '0001018724',  # Amazon.com Inc.
        '0001652044',  # Google (Alphabet Inc.)
        '0001318605',  # Tesla Inc.
        '0001067983',  # Berkshire Hathaway
        '0001326801',  # Meta Platforms Inc.
        '0001045810',  # NVIDIA Corporation
        '0000004962',  # Johnson & Johnson
        '0000078006',  # JPMorgan Chase & Co.
        '0000001800',  # Bank of America Corp
        '0000004962',  # Procter & Gamble Co
        '0000004962',  # Coca-Cola Co
        '0000004962',  # Walt Disney Co
        '0000004962',  # Netflix Inc
    ]

def upload_to_bigquery(contracts: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload contracts to BigQuery."""
    try:
        bq_client = BigQueryClient(config)
        project_id = config['bigquery']['project_id']
        table_id = f"{project_id}.raw_data.legal_documents"

        # Convert to BigQuery format
        rows_to_insert = []
        for contract in contracts:
            row = {
                'document_id': contract['document_id'],
                'source_system': contract['source_system'],
                'document_type': contract['document_type'],
                'raw_content': contract['raw_content'],
                'metadata': json.dumps(contract['metadata']),
                'ingestion_timestamp': contract['ingestion_timestamp']
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
                logger.info(f"Successfully inserted batch {i//batch_size + 1} ({len(batch)} contracts)")

        return True

    except Exception as e:
        logger.error(f"Error uploading to BigQuery: {e}")
        return False

def main():
    """Main function to download SEC contracts."""
    print("🏢 SEC EDGAR Contracts Downloader")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = SECContractsDownloader(config)

    # Get company CIKs
    company_ciks = get_popular_company_ciks()

    all_contracts = []
    total_contracts = 0

    # Download contracts for each company
    for cik in company_ciks:
        try:
            contracts = downloader.download_company_contracts(cik, max_contracts=10)
            all_contracts.extend(contracts)
            total_contracts += len(contracts)

            logger.info(f"Downloaded {len(contracts)} contracts from CIK {cik}")

            # Rate limiting between companies
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error downloading contracts for CIK {cik}: {e}")
            continue

    print(f"\n📊 Download Summary:")
    print(f"   Total contracts downloaded: {total_contracts}")
    print(f"   Companies processed: {len(company_ciks)}")

    if all_contracts:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(all_contracts, config)

        if success:
            print("✅ Successfully uploaded contracts to BigQuery!")
        else:
            print("❌ Failed to upload contracts to BigQuery")

        # Save to local file as backup
        output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'sec_contracts.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(all_contracts, f, indent=2)

        print(f"💾 Contracts saved to: {output_file}")
    else:
        print("❌ No contracts were downloaded")

if __name__ == "__main__":
    main()
