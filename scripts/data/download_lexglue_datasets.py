#!/usr/bin/env python3
"""
LexGLUE Benchmark Datasets Downloader
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads LexGLUE benchmark datasets from GitHub repository.
"""

import os
import sys
import json
import time
import requests
import logging
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LexGLUEDownloader:
    """Downloader for LexGLUE benchmark datasets."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the LexGLUE downloader."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Legal AI Platform (contact@example.com)',
            'Accept': 'application/vnd.github.v3+json'
        })

        # LexGLUE GitHub repository (corrected URL)
        self.github_repo = "coastalcph/lexglue"
        self.github_url = f"https://api.github.com/repos/{self.github_repo}"
        self.download_url = f"https://github.com/{self.github_repo}/archive/refs/heads/master.zip"

        # Available datasets
        self.datasets = {
            'ecthr_a': 'European Court of Human Rights - Article 3',
            'ecthr_b': 'European Court of Human Rights - Article 6',
            'eurlex': 'EU Legal Documents',
            'scotus': 'US Supreme Court Cases',
            'ledgar': 'Legal Document Classification',
            'unfair_tos': 'Unfair Terms of Service',
            'case_hold': 'Case Law Holdings'
        }

    def download_lexglue_repository(self) -> str:
        """
        Download the LexGLUE repository as a ZIP file.

        Returns:
            Path to the downloaded ZIP file
        """
        logger.info("📥 Downloading LexGLUE repository...")

        try:
            response = self.session.get(self.download_url, stream=True)
            response.raise_for_status()

            # Create temporary file for ZIP
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

            # Download in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)

            temp_file.close()
            logger.info(f"✅ Downloaded LexGLUE repository to: {temp_file.name}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Error downloading LexGLUE repository: {e}")
            return None

    def extract_dataset_files(self, zip_path: str, output_dir: str) -> Dict[str, List[str]]:
        """
        Extract dataset files from the ZIP archive.

        Args:
            zip_path: Path to the ZIP file
            output_dir: Directory to extract files to

        Returns:
            Dictionary mapping dataset names to file paths
        """
        logger.info("📂 Extracting LexGLUE datasets...")

        dataset_files = {}

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(output_dir)

                # Find dataset files
                extracted_dir = Path(output_dir) / "lexglue-master"

                for dataset_name in self.datasets.keys():
                    dataset_files[dataset_name] = []

                    # Look for dataset files (train.json, test.json, dev.json)
                    for split in ['train', 'test', 'dev']:
                        file_pattern = f"**/{dataset_name}/{split}.json"
                        files = list(extracted_dir.glob(file_pattern))

                        if files:
                            dataset_files[dataset_name].extend([str(f) for f in files])
                            logger.info(f"Found {len(files)} {split} files for {dataset_name}")

                logger.info(f"✅ Extracted {sum(len(files) for files in dataset_files.values())} dataset files")
                return dataset_files

        except Exception as e:
            logger.error(f"Error extracting LexGLUE datasets: {e}")
            return {}

    def process_dataset_file(self, file_path: str, dataset_name: str) -> List[Dict]:
        """
        Process a single dataset file.

        Args:
            file_path: Path to the dataset file
            dataset_name: Name of the dataset

        Returns:
            List of processed documents
        """
        documents = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different data formats
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'data' in data:
                items = data['data']
            else:
                items = [data]

            for i, item in enumerate(items):
                # Extract text content
                text_content = ""
                if 'text' in item:
                    text_content = item['text']
                elif 'content' in item:
                    text_content = item['content']
                elif 'sentence' in item:
                    text_content = item['sentence']
                elif 'case_text' in item:
                    text_content = item['case_text']

                # Extract label/task information
                label = item.get('label', item.get('task', 'unknown'))

                # Create document
                document = {
                    'document_id': f"LEXGLUE_{dataset_name}_{i:06d}",
                    'source_system': 'LEXGLUE',
                    'document_type': 'legal_document',
                    'raw_content': text_content,
                    'metadata': {
                        'dataset': dataset_name,
                        'dataset_description': self.datasets.get(dataset_name, ''),
                        'label': label,
                        'task': item.get('task', ''),
                        'split': Path(file_path).stem,  # train, test, dev
                        'file_path': file_path,
                        'content_length': len(text_content),
                        'word_count': len(text_content.split()) if text_content else 0,
                        'source': 'LexGLUE Benchmark'
                    },
                    'ingestion_timestamp': datetime.now().isoformat()
                }

                documents.append(document)

            logger.info(f"Processed {len(documents)} documents from {file_path}")
            return documents

        except Exception as e:
            logger.error(f"Error processing dataset file {file_path}: {e}")
            return []

    def download_lexglue_datasets(self, max_documents: int = 200) -> List[Dict]:
        """
        Download and process LexGLUE benchmark datasets.

        Args:
            max_documents: Maximum number of documents to download

        Returns:
            List of processed documents
        """
        logger.info(f"🚀 Starting LexGLUE dataset download (target: {max_documents} documents)")

        all_documents = []

        try:
            # Download repository
            zip_path = self.download_lexglue_repository()
            if not zip_path:
                return []

            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract datasets
                dataset_files = self.extract_dataset_files(zip_path, temp_dir)

                # Process each dataset
                for dataset_name, files in dataset_files.items():
                    if len(all_documents) >= max_documents:
                        break

                    logger.info(f"Processing dataset: {dataset_name}")

                    for file_path in files:
                        if len(all_documents) >= max_documents:
                            break

                        # Process file
                        documents = self.process_dataset_file(file_path, dataset_name)

                        # Add documents (respecting max limit)
                        remaining_slots = max_documents - len(all_documents)
                        all_documents.extend(documents[:remaining_slots])

                        logger.info(f"Added {min(len(documents), remaining_slots)} documents from {dataset_name}")

                # Clean up ZIP file
                os.unlink(zip_path)

        except Exception as e:
            logger.error(f"Error downloading LexGLUE datasets: {e}")

        logger.info(f"✅ Total LexGLUE documents processed: {len(all_documents)}")
        return all_documents

    def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about available LexGLUE datasets."""
        return {
            'datasets': self.datasets,
            'total_datasets': len(self.datasets),
            'repository': self.github_repo,
            'description': 'LexGLUE: A Benchmark Dataset for Legal Language Understanding in English'
        }

def upload_to_bigquery(documents: List[Dict], config: Dict[str, Any]) -> bool:
    """Upload LexGLUE documents to BigQuery."""
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
    """Main function to download LexGLUE datasets."""
    print("📚 LexGLUE Benchmark Datasets Downloader")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize downloader
    downloader = LexGLUEDownloader(config)

    # Show dataset info
    info = downloader.get_dataset_info()
    print(f"\n📋 Available Datasets:")
    for dataset, description in info['datasets'].items():
        print(f"   • {dataset}: {description}")

    # Download datasets
    documents = downloader.download_lexglue_datasets(max_documents=200)

    print(f"\n📊 Download Summary:")
    print(f"   Total documents downloaded: {len(documents)}")

    if documents:
        # Upload to BigQuery
        print("\n📤 Uploading to BigQuery...")
        success = upload_to_bigquery(documents, config)

        if success:
            print("✅ Successfully uploaded LexGLUE documents to BigQuery!")
        else:
            print("❌ Failed to upload LexGLUE documents to BigQuery")

        # Save to local file as backup
        output_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'lexglue_datasets.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(documents, f, indent=2)

        print(f"💾 LexGLUE documents saved to: {output_file}")

        # Print sample document info
        print(f"\n📋 Sample Documents:")
        for i, doc in enumerate(documents[:3]):
            metadata = doc['metadata']
            print(f"   {i+1}. Dataset: {metadata.get('dataset', 'Unknown')}")
            print(f"      Label: {metadata.get('label', 'Unknown')}")
            print(f"      Split: {metadata.get('split', 'Unknown')}")
            print(f"      Content Length: {metadata.get('content_length', 0)} chars")
            print()
    else:
        print("❌ No LexGLUE documents were downloaded")

if __name__ == "__main__":
    main()
