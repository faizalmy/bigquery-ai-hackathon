#!/usr/bin/env python3
"""
Test SEC Contracts Download
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests downloading SEC contracts with a smaller sample.
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
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts' / 'data'))

from config import load_config
from utils.bigquery_client import BigQueryClient
from download_sec_contracts import SECContractsDownloader, upload_to_bigquery

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sec_download():
    """Test downloading a small sample of SEC contracts."""
    print("🧪 Testing SEC Contracts Download")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = SECContractsDownloader(config)

    # Test with just one company first
    test_cik = '0000320193'  # Apple Inc.

    try:
        print(f"Testing download for Apple Inc. (CIK: {test_cik})")
        contracts = downloader.download_company_contracts(test_cik, max_contracts=5)

        print(f"✅ Downloaded {len(contracts)} contracts")

        if contracts:
            # Show sample contract info
            for i, contract in enumerate(contracts[:2], 1):
                metadata = contract['metadata']
                print(f"\n📄 Contract {i}:")
                print(f"   Document ID: {contract['document_id']}")
                print(f"   Company: {metadata.get('company_name', 'Unknown')}")
                print(f"   Form Type: {metadata.get('form_type', 'Unknown')}")
                print(f"   Filing Date: {metadata.get('filing_date', 'Unknown')}")
                print(f"   Content Length: {len(contract['raw_content'])} characters")
                print(f"   Word Count: {metadata.get('word_count', 0)} words")

            # Test upload to BigQuery
            print(f"\n📤 Testing BigQuery upload...")
            success = upload_to_bigquery(contracts, config)

            if success:
                print("✅ Successfully uploaded to BigQuery!")
            else:
                print("❌ Failed to upload to BigQuery")

            # Save to local file
            output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'test_sec_contracts.json'
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(contracts, f, indent=2)

            print(f"💾 Test contracts saved to: {output_file}")

        else:
            print("❌ No contracts were downloaded")

    except Exception as e:
        logger.error(f"Error in test download: {e}")
        print(f"❌ Test failed: {e}")

def main():
    """Main function."""
    # Check if .env file exists
    env_file = Path(__file__).parent.parent.parent / '.env'
    if not env_file.exists():
        print("❌ .env file not found. Please run the BigQuery setup script first:")
        print("   ./scripts/setup/bigquery_setup.sh")
        return False

    # Load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

    test_sec_download()
    return True

if __name__ == "__main__":
    main()
