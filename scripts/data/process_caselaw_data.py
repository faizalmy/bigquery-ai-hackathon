#!/usr/bin/env python3
"""
Caselaw Data Processing Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script processes the Caselaw Access Project dataset and prepares it
for BigQuery AI functions with proper formatting and metadata.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import hashlib

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CaselawDataProcessor:
    """Processes Caselaw Access Project data for BigQuery AI functions."""

    def __init__(self):
        """Initialize Caselaw data processor."""
        self.input_dir = Path("data/raw/caselaw_data")
        self.output_dir = Path("data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Processing statistics
        self.stats = {
            "total_documents": 0,
            "processed_documents": 0,
            "failed_documents": 0,
            "total_size_mb": 0,
            "document_types": {},
            "jurisdictions": {},
            "courts": {}
        }

    def process_caselaw_data(self) -> bool:
        """
        Process Caselaw Access Project data.

        Returns:
            bool: True if processing successful, False otherwise
        """
        try:
            logger.info("Starting Caselaw data processing...")

            # Find input file
            input_file = self.input_dir / "caselaw_documents.json"

            if not input_file.exists():
                logger.error(f"Input file not found: {input_file}")
                return False

            # Load and process documents
            with open(input_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)

            if not documents:
                logger.error("No documents found in input file")
                return False

            logger.info(f"Processing {len(documents)} documents...")

            # Process documents
            processed_docs = []
            for i, doc in enumerate(documents):
                try:
                    processed_doc = self._process_caselaw_document(doc, i)
                    if processed_doc:
                        processed_docs.append(processed_doc)
                        self.stats["processed_documents"] += 1

                        # Update statistics
                        self._update_stats(processed_doc)
                    else:
                        self.stats["failed_documents"] += 1

                except Exception as e:
                    logger.warning(f"Failed to process document {i}: {e}")
                    self.stats["failed_documents"] += 1
                    continue

            self.stats["total_documents"] = len(documents)

            if not processed_docs:
                logger.error("No documents were successfully processed")
                return False

            # Save processed documents
            output_file = self.output_dir / "processed_hf_legal_documents.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_docs, f, indent=2, ensure_ascii=False)

            # Generate processing report
            self._generate_processing_report()

            logger.info(f"Successfully processed {len(processed_docs)} Caselaw documents")
            logger.info(f"Output saved to: {output_file}")

            return True

        except Exception as e:
            logger.error(f"Failed to process Caselaw data: {e}")
            return False

    def _process_caselaw_document(self, doc: Dict, index: int) -> Optional[Dict]:
        """Process a single Caselaw document."""
        try:
            # Validate required fields
            if not self._validate_document(doc):
                return None

            # Clean and normalize content
            cleaned_content = self._clean_legal_content(doc.get('content', ''))
            if not cleaned_content or len(cleaned_content) < 200:
                logger.warning(f"Document {index} content too short after cleaning")
                return None

            # Extract and enhance metadata
            metadata = self._extract_caselaw_metadata(doc)

            # Generate document hash for uniqueness
            doc_hash = self._generate_document_hash(cleaned_content)

            # Create processed document optimized for BigQuery AI
            processed_doc = {
                "document_id": doc.get('document_id', f"caselaw_{index+1:06d}"),
                "document_type": "case_law",
                "title": self._clean_legal_title(doc.get('title', 'Court Decision')),
                "content": cleaned_content,
                "metadata": {
                    **metadata,
                    "source": "Caselaw Access Project",
                    "dataset": "free-law/Caselaw_Access_Project",
                    "document_type": "case_law",
                    "jurisdiction": metadata.get('jurisdiction', 'US_Federal_State'),
                    "date": metadata.get('date', datetime.now().isoformat()),
                    "urgency": "standard",
                    "file_size": len(cleaned_content.encode('utf-8')),
                    "word_count": len(cleaned_content.split()),
                    "document_hash": doc_hash,
                    "processing_timestamp": datetime.now().isoformat(),
                    "bigquery_ai_ready": True
                },
                "created_at": doc.get('created_at', datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat()
            }

            # Update size statistics
            doc_size = len(json.dumps(processed_doc).encode('utf-8'))
            self.stats["total_size_mb"] += doc_size / 1024 / 1024

            return processed_doc

        except Exception as e:
            logger.error(f"Failed to process Caselaw document {index}: {e}")
            return None

    def _validate_document(self, doc: Dict) -> bool:
        """Validate document structure."""
        required_fields = ['document_id', 'title', 'content']

        for field in required_fields:
            if field not in doc or not doc[field]:
                logger.warning(f"Missing required field: {field}")
                return False

        return True

    def _clean_legal_content(self, content: str) -> str:
        """Clean and normalize legal document content."""
        if not content:
            return ""

        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)

        # Remove HTML tags if present
        content = re.sub(r'<[^>]+>', '', content)

        # Clean up legal formatting
        content = re.sub(r'\[.*?\]', '', content)  # Remove citations in brackets
        content = re.sub(r'\(.*?\)', '', content)  # Remove parenthetical citations

        # Normalize legal punctuation
        content = re.sub(r'\.{3,}', '...', content)
        content = re.sub(r'\!{2,}', '!', content)
        content = re.sub(r'\?{2,}', '?', content)

        # Remove excessive line breaks and formatting
        content = re.sub(r'\n+', ' ', content)
        content = re.sub(r'\r+', ' ', content)

        # Clean up common OCR errors
        content = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\-\'\"\/]', '', content)

        # Normalize quotes
        content = content.replace('"', '"').replace('"', '"')
        content = content.replace(''', "'").replace(''', "'")

        return content.strip()

    def _clean_legal_title(self, title: str) -> str:
        """Clean legal document title."""
        if not title:
            return "Court Decision"

        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)

        # Remove special characters but keep legal formatting
        title = re.sub(r'[^\w\s\.\,\-\'\"\(\)]', '', title)

        # Limit length
        if len(title) > 200:
            title = title[:197] + "..."

        return title.strip()

    def _extract_caselaw_metadata(self, doc: Dict) -> Dict:
        """Extract and enhance Caselaw metadata."""
        metadata = doc.get('metadata', {})

        # Extract court information
        court = metadata.get('court', 'Unknown Court')
        jurisdiction = self._determine_jurisdiction(court, metadata)

        # Extract case information
        case_id = metadata.get('case_id', '')
        docket_number = metadata.get('docket_number', '')
        citation = metadata.get('citation', '')

        # Extract date information
        date = metadata.get('date', '')
        year = metadata.get('year', '')

        # Determine case type
        case_type = self._determine_case_type(metadata)

        return {
            **metadata,
            'court': court,
            'jurisdiction': jurisdiction,
            'case_id': case_id,
            'docket_number': docket_number,
            'citation': citation,
            'date': date,
            'year': year,
            'case_type': case_type,
            'normalized_document_type': 'case_law',
            'normalized_jurisdiction': jurisdiction
        }

    def _determine_jurisdiction(self, court: str, metadata: Dict) -> str:
        """Determine jurisdiction from court information."""
        court_lower = court.lower()

        if 'supreme' in court_lower and 'united states' in court_lower:
            return 'US_Federal_Supreme'
        elif 'federal' in court_lower or 'district' in court_lower:
            return 'US_Federal'
        elif 'state' in court_lower:
            return 'US_State'
        elif metadata.get('state'):
            return f"US_State_{metadata['state']}"
        else:
            return 'US_Federal_State'

    def _determine_case_type(self, metadata: Dict) -> str:
        """Determine case type from metadata."""
        # Common case types
        case_type_indicators = {
            'criminal': ['criminal', 'felony', 'misdemeanor', 'theft', 'assault'],
            'civil': ['civil', 'contract', 'tort', 'liability'],
            'constitutional': ['constitutional', 'first amendment', 'fourth amendment'],
            'administrative': ['administrative', 'regulatory', 'agency'],
            'family': ['family', 'divorce', 'custody', 'adoption'],
            'business': ['business', 'corporate', 'commercial', 'partnership']
        }

        # Check metadata fields for case type indicators
        text_to_check = ' '.join([
            str(metadata.get('case_type', '')),
            str(metadata.get('subject', '')),
            str(metadata.get('topics', ''))
        ]).lower()

        for case_type, indicators in case_type_indicators.items():
            if any(indicator in text_to_check for indicator in indicators):
                return case_type

        return 'general'

    def _generate_document_hash(self, content: str) -> str:
        """Generate a hash for document uniqueness."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _update_stats(self, doc: Dict) -> None:
        """Update processing statistics."""
        metadata = doc.get('metadata', {})

        # Document types
        doc_type = metadata.get('normalized_document_type', 'unknown')
        self.stats['document_types'][doc_type] = self.stats['document_types'].get(doc_type, 0) + 1

        # Jurisdictions
        jurisdiction = metadata.get('normalized_jurisdiction', 'unknown')
        self.stats['jurisdictions'][jurisdiction] = self.stats['jurisdictions'].get(jurisdiction, 0) + 1

        # Courts
        court = metadata.get('court', 'unknown')
        self.stats['courts'][court] = self.stats['courts'].get(court, 0) + 1

    def _generate_processing_report(self) -> None:
        """Generate processing report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dataset": "HFforLegal/case-law",
            "processing_stats": self.stats,
            "success_rate": (self.stats["processed_documents"] / max(self.stats["total_documents"], 1)) * 100,
            "average_document_size_kb": (self.stats["total_size_mb"] * 1024) / max(self.stats["processed_documents"], 1),
            "bigquery_ai_ready": True
        }

        report_file = self.output_dir / "hf_legal_processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Processing report saved to: {report_file}")


def main():
    """Main execution function."""
    try:
        print("⚖️ HFforLegal Case-law Data Processor")
        print("=" * 40)
        print("Processing HFforLegal case-law data for BigQuery AI...")

        # Initialize processor
        processor = CaselawDataProcessor()

        # Process Caselaw data
        if processor.process_caselaw_data():
            print("✅ Caselaw documents processed successfully!")

            # Print statistics
            stats = processor.stats
            print(f"\n📊 Processing Statistics:")
            print(f"  Total Documents: {stats['total_documents']}")
            print(f"  Processed: {stats['processed_documents']}")
            print(f"  Failed: {stats['failed_documents']}")
            print(f"  Success Rate: {(stats['processed_documents'] / max(stats['total_documents'], 1)) * 100:.1f}%")
            print(f"  Total Size: {stats['total_size_mb']:.2f} MB")
            print(f"  Document Types: {len(stats['document_types'])}")
            print(f"  Jurisdictions: {len(stats['jurisdictions'])}")
            print(f"  Courts: {len(stats['courts'])}")
            print()
            print("🎯 Ready for BigQuery AI functions!")

            return 0
        else:
            print("❌ Failed to process Caselaw documents")
            return 1

    except Exception as e:
        logger.error(f"Processing script failed: {e}")
        print(f"\n❌ Processing script failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
