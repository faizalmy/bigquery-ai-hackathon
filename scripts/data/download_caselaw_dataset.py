#!/usr/bin/env python3
"""
Caselaw Access Project Dataset Download Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script downloads real legal documents from the Caselaw Access Project
dataset on Hugging Face, which contains over 6.7 million U.S. court decisions.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from datasets import load_dataset
    import pandas as pd
except ImportError:
    logger.error("Required packages not installed. Please install: pip install datasets pandas")
    sys.exit(1)

class CaselawDatasetDownloader:
    """Downloads legal documents from Caselaw Access Project dataset."""

    def __init__(self, max_size_mb: int = 100, max_documents: int = 1000):
        """
        Initialize Caselaw dataset downloader.

        Args:
            max_size_mb: Maximum size in MB for downloaded data
            max_documents: Maximum number of documents to download
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_documents = max_documents
        self.current_size = 0
        self.downloaded_documents = []
        self.output_dir = Path("data/raw/caselaw_data")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Dataset configuration
        self.dataset_name = "HFforLegal/case-law"
        self.dataset_info = {
            "name": "Case-law Dataset",
            "description": "Comprehensive collection of legal decisions from various countries",
            "source": "HFforLegal Community",
            "license": "CC-BY-4.0",
            "size": "534k documents",
            "url": "https://huggingface.co/datasets/HFforLegal/case-law"
        }

    def download_caselaw_dataset(self) -> bool:
        """
        Download HFforLegal case-law dataset.

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            logger.info("Starting HFforLegal case-law dataset download...")
            logger.info(f"Dataset: {self.dataset_name}")
            logger.info(f"Max documents: {self.max_documents}")
            logger.info(f"Max size: {self.max_size_bytes / 1024 / 1024:.1f} MB")

            # Load dataset from Hugging Face (US split for English content)
            logger.info("Loading US case-law dataset from Hugging Face...")
            dataset = load_dataset(
                self.dataset_name,
                split="us",  # Use US split for English legal documents
                streaming=True,  # Use streaming to avoid downloading entire dataset
                trust_remote_code=True
            )

            # Process documents in batches
            processed_docs = self._process_dataset_stream(dataset)

            if not processed_docs:
                logger.error("No documents were processed")
                return False

            # Save to file
            output_file = self.output_dir / "caselaw_documents.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_docs, f, indent=2, ensure_ascii=False)

            logger.info(f"Downloaded {len(processed_docs)} legal documents")
            logger.info(f"Total size: {self.current_size / 1024 / 1024:.2f} MB")
            logger.info(f"Output saved to: {output_file}")

            return True

        except Exception as e:
            logger.error(f"Failed to download Caselaw dataset: {e}")
            return False

    def _process_dataset_stream(self, dataset) -> List[Dict]:
        """Process dataset stream and convert to our format."""
        processed_docs = []
        doc_count = 0

        logger.info("Processing dataset stream...")

        for item in dataset:
            try:
                # Check limits
                if doc_count >= self.max_documents:
                    logger.info(f"Reached maximum document limit: {self.max_documents}")
                    break

                # Process document
                processed_doc = self._process_caselaw_document(item, doc_count)
                if processed_doc:
                    # Check size limits
                    doc_size = len(json.dumps(processed_doc).encode('utf-8'))
                    if self.current_size + doc_size > self.max_size_bytes:
                        logger.info(f"Reached size limit: {self.max_size_bytes / 1024 / 1024:.1f} MB")
                        break

                    processed_docs.append(processed_doc)
                    self.current_size += doc_size
                    self.downloaded_documents.append(processed_doc)
                    doc_count += 1

                    # Progress logging
                    if doc_count % 100 == 0:
                        logger.info(f"Processed {doc_count} documents...")

            except Exception as e:
                logger.warning(f"Failed to process document {doc_count}: {e}")
                continue

        return processed_docs

    def _process_caselaw_document(self, item: Dict, index: int) -> Optional[Dict]:
        """Process a single Caselaw document."""
        try:
            # Extract document content
            content = self._extract_document_content(item)
            if not content or len(content) < 200:  # Skip short documents
                return None

            # Extract metadata
            metadata = self._extract_document_metadata(item)

            # Create document in our format
            processed_doc = {
                "document_id": f"caselaw_{index+1:06d}",
                "document_type": "case_law",
                "title": self._extract_document_title(item),
                "content": content,
                "metadata": {
                    **metadata,
                    "source": "Caselaw Access Project",
                    "dataset": self.dataset_name,
                    "jurisdiction": "US_Federal_State",
                    "date": datetime.now().isoformat(),
                    "urgency": "standard",
                    "file_size": len(content.encode('utf-8')),
                    "word_count": len(content.split())
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            return processed_doc

        except Exception as e:
            logger.warning(f"Failed to process caselaw document: {e}")
            return None

    def _extract_document_content(self, item: Dict) -> str:
        """Extract document content from HFforLegal case-law item."""
        content = ""

        # HFforLegal dataset uses 'document' field for content
        if 'document' in item and item['document']:
            content = str(item['document'])

        # Clean content
        if content:
            # Remove excessive whitespace
            content = ' '.join(content.split())

            # Limit content length to avoid huge documents
            if len(content) > 10000:
                content = content[:10000] + "..."

        return content

    def _extract_document_title(self, item: Dict) -> str:
        """Extract document title from HFforLegal case-law item."""
        title = "Court Decision"

        # HFforLegal dataset uses 'title' field
        if 'title' in item and item['title']:
            title = str(item['title'])

        # Clean title
        if title and len(title) > 200:
            title = title[:197] + "..."

        return title or "Court Decision"

    def _extract_document_metadata(self, item: Dict) -> Dict:
        """Extract metadata from HFforLegal case-law item."""
        metadata = {}

        # HFforLegal dataset specific fields
        hf_fields = [
            'id', 'title', 'citation', 'docket_number',
            'state', 'issuer', 'hash', 'timestamp'
        ]

        for field in hf_fields:
            if field in item and item[field]:
                metadata[field] = item[field]

        # Map HFforLegal fields to our standard format
        if 'state' in metadata:
            metadata['jurisdiction'] = f"US_State_{metadata['state']}"
            metadata['court'] = metadata.get('issuer', 'Unknown Court')

        if 'timestamp' in metadata:
            metadata['date'] = metadata['timestamp']

        # Add processing metadata
        metadata['processing_timestamp'] = datetime.now().isoformat()
        metadata['dataset_version'] = '1.0'
        metadata['source_dataset'] = 'HFforLegal/case-law'

        return metadata

    def generate_download_report(self) -> Dict[str, Any]:
        """Generate download report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "dataset_info": self.dataset_info,
            "download_stats": {
                "total_documents": len(self.downloaded_documents),
                "total_size_mb": self.current_size / 1024 / 1024,
                "max_size_mb": self.max_size_bytes / 1024 / 1024,
                "size_utilization": (self.current_size / self.max_size_bytes) * 100,
                "max_documents": self.max_documents,
                "document_utilization": (len(self.downloaded_documents) / self.max_documents) * 100
            },
            "output_file": str(self.output_dir / "caselaw_documents.json")
        }


def main():
    """Main execution function."""
    try:
        print("⚖️ HFforLegal Case-law Dataset Downloader")
        print("=" * 60)
        print("Downloading real legal decisions from various countries...")
        print("Dataset: HFforLegal/case-law")
        print("License: CC-BY-4.0")
        print("Focus: US legal decisions (English content)")
        print()

        # Initialize downloader
        downloader = CaselawDatasetDownloader(max_size_mb=100, max_documents=1000)

        # Download dataset
        if downloader.download_caselaw_dataset():
            print("✅ Caselaw dataset downloaded successfully!")

            # Generate report
            report = downloader.generate_download_report()
            print(f"\n📊 Download Report:")
            print(f"  Dataset: {report['dataset_info']['name']}")
            print(f"  Documents: {report['download_stats']['total_documents']}")
            print(f"  Size: {report['download_stats']['total_size_mb']:.2f} MB")
            print(f"  Size Utilization: {report['download_stats']['size_utilization']:.1f}%")
            print(f"  Document Utilization: {report['download_stats']['document_utilization']:.1f}%")
            print(f"  Output: {report['output_file']}")
            print()
            print("🎯 Ready for BigQuery AI functions!")

            return 0
        else:
            print("❌ Failed to download Caselaw dataset")
            return 1

    except Exception as e:
        logger.error(f"Download script failed: {e}")
        print(f"\n❌ Download script failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
