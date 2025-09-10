#!/usr/bin/env python3
"""
Legal Document Preprocessing Pipeline
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module handles preprocessing of legal documents for AI analysis.
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalDocumentPreprocessor:
    """Preprocessor for legal documents."""

    def __init__(self):
        """Initialize the preprocessor."""
        self.legal_terms = self._load_legal_terms()
        self.document_types = self._load_document_types()

    def _load_legal_terms(self) -> List[str]:
        """Load common legal terms for classification."""
        return [
            'plaintiff', 'defendant', 'court', 'judge', 'jury', 'trial',
            'appeal', 'motion', 'brief', 'hearing', 'ruling', 'decision',
            'statute', 'regulation', 'constitution', 'amendment', 'clause',
            'liability', 'damages', 'negligence', 'breach', 'contract',
            'tort', 'criminal', 'civil', 'administrative', 'procedural',
            'due process', 'equal protection', 'freedom of speech',
            'search and seizure', 'jury trial', 'burden of proof',
            'precedent', 'jurisdiction', 'venue', 'standing'
        ]

    def _load_document_types(self) -> Dict[str, List[str]]:
        """Load document type classification patterns."""
        return {
            'supreme_court_case': [
                'supreme court', 'scotus', 'certiorari', 'writ of certiorari',
                'oral argument', 'opinion', 'dissent', 'concurrence'
            ],
            'federal_regulation': [
                'code of federal regulations', 'cfr', 'title', 'section',
                'regulation', 'administrative', 'agency', 'rulemaking'
            ],
            'court_case': [
                'court of appeals', 'district court', 'circuit court',
                'case number', 'docket', 'filed', 'opinion', 'judgment'
            ],
            'legal_brief': [
                'brief', 'motion', 'memorandum', 'petition', 'response',
                'reply', 'opposition', 'support', 'amicus'
            ],
            'contract': [
                'agreement', 'contract', 'terms', 'conditions', 'party',
                'obligation', 'consideration', 'breach', 'performance'
            ],
            'statute': [
                'statute', 'law', 'act', 'section', 'subsection',
                'legislature', 'congress', 'bill', 'enactment'
            ]
        }

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize legal document text.

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep legal symbols
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\"\'§¶]', ' ', text)

        # Normalize legal citations
        text = self._normalize_citations(text)

        # Remove page numbers and headers
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)

        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _normalize_citations(self, text: str) -> str:
        """Normalize legal citations in text."""
        # Normalize case citations
        text = re.sub(r'(\d+)\s+U\.S\.\s+(\d+)', r'\1 U.S. \2', text)
        text = re.sub(r'(\d+)\s+F\.\s*(\d+)(d|rd|th)?\s+(\d+)', r'\1 F.\2\3 \4', text)

        # Normalize statute citations
        text = re.sub(r'(\d+)\s+U\.S\.C\.\s+§\s*(\d+)', r'\1 U.S.C. § \2', text)
        text = re.sub(r'(\d+)\s+CFR\s+§\s*(\d+)', r'\1 CFR § \2', text)

        return text

    def classify_document(self, document: Dict[str, Any]) -> str:
        """
        Classify document type based on content and metadata.

        Args:
            document: Document with content and metadata

        Returns:
            Document type classification
        """
        content = document.get('raw_content', '').lower()
        metadata = document.get('metadata', {})

        # Check metadata first
        if 'document_type' in metadata:
            doc_type = metadata['document_type']
            if doc_type in self.document_types:
                return doc_type

        # Classify based on content patterns
        type_scores = {}

        for doc_type, patterns in self.document_types.items():
            score = 0
            for pattern in patterns:
                if pattern in content:
                    score += 1
            type_scores[doc_type] = score

        # Return type with highest score
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type

        return 'legal_document'  # Default classification

    def extract_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured metadata from document.

        Args:
            document: Document with content and metadata

        Returns:
            Extracted metadata
        """
        content = document.get('raw_content', '')
        existing_metadata = document.get('metadata', {})

        extracted = {
            'content_length': len(content),
            'word_count': len(content.split()) if content else 0,
            'sentence_count': len(re.findall(r'[.!?]+', content)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'legal_terms_found': self._count_legal_terms(content),
            'has_citations': self._has_citations(content),
            'has_legal_structure': self._has_legal_structure(content),
            'complexity_score': self._calculate_complexity_score(content)
        }

        # Merge with existing metadata
        extracted.update(existing_metadata)

        return extracted

    def _count_legal_terms(self, content: str) -> int:
        """Count legal terms in content."""
        content_lower = content.lower()
        count = 0
        for term in self.legal_terms:
            if term in content_lower:
                count += 1
        return count

    def _has_citations(self, content: str) -> bool:
        """Check if content contains legal citations."""
        citation_patterns = [
            r'\d+\s+U\.S\.\s+\d+',  # Supreme Court
            r'\d+\s+F\.\s*\d+',     # Federal cases
            r'\d+\s+U\.S\.C\.\s+§', # US Code
            r'\d+\s+CFR\s+§',       # CFR
            r'v\.\s+\w+',           # Case names
            r'No\.\s+\d+'           # Case numbers
        ]

        for pattern in citation_patterns:
            if re.search(pattern, content):
                return True
        return False

    def _has_legal_structure(self, content: str) -> bool:
        """Check if content has legal document structure."""
        structure_indicators = [
            'plaintiff', 'defendant', 'court', 'case', 'matter',
            'whereas', 'therefore', 'hereby', 'pursuant to',
            'in accordance with', 'subject to', 'notwithstanding'
        ]

        content_lower = content.lower()
        count = sum(1 for indicator in structure_indicators if indicator in content_lower)
        return count >= 3

    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate document complexity score."""
        if not content:
            return 0.0

        # Factors: length, legal terms, citations, structure
        length_score = min(len(content) / 10000, 1.0)  # Normalize to 0-1
        legal_terms_score = min(self._count_legal_terms(content) / 20, 1.0)
        citations_score = 1.0 if self._has_citations(content) else 0.0
        structure_score = 1.0 if self._has_legal_structure(content) else 0.0

        # Weighted average
        complexity = (
            length_score * 0.3 +
            legal_terms_score * 0.3 +
            citations_score * 0.2 +
            structure_score * 0.2
        )

        return round(complexity, 2)

    def assess_quality(self, document: Dict[str, Any]) -> float:
        """
        Assess document quality score.

        Args:
            document: Document to assess

        Returns:
            Quality score (0.0 to 1.0)
        """
        content = document.get('raw_content', '')
        metadata = document.get('metadata', {})

        if not content:
            return 0.0

        # Quality factors
        length_score = min(len(content) / 1000, 1.0)  # Minimum 1000 chars
        completeness_score = 1.0 if len(content) > 500 else 0.5
        structure_score = 1.0 if self._has_legal_structure(content) else 0.3
        citations_score = 1.0 if self._has_citations(content) else 0.7
        legal_terms_score = min(self._count_legal_terms(content) / 10, 1.0)

        # Metadata completeness
        metadata_score = 0.8 if metadata else 0.5
        if metadata and 'source' in metadata:
            metadata_score = 1.0

        # Weighted quality score
        quality = (
            length_score * 0.2 +
            completeness_score * 0.2 +
            structure_score * 0.2 +
            citations_score * 0.15 +
            legal_terms_score * 0.15 +
            metadata_score * 0.1
        )

        return round(quality, 2)

    def preprocess_document(self, raw_document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess a single legal document.

        Args:
            raw_document: Raw document from data source

        Returns:
            Processed document ready for AI analysis
        """
        try:
            # Clean content
            cleaned_content = self.clean_text(raw_document.get('raw_content', ''))

            # Classify document
            document_type = self.classify_document(raw_document)

            # Extract metadata
            extracted_metadata = self.extract_metadata(raw_document)

            # Assess quality
            quality_score = self.assess_quality(raw_document)

            # Create processed document
            processed_document = {
                'document_id': raw_document.get('document_id', ''),
                'source_system': raw_document.get('source_system', ''),
                'document_type': document_type,
                'cleaned_content': cleaned_content,
                'extracted_metadata': extracted_metadata,
                'quality_score': quality_score,
                'processed_timestamp': datetime.now().isoformat(),
                'original_metadata': raw_document.get('metadata', {})
            }

            return processed_document

        except Exception as e:
            logger.error(f"Error preprocessing document {raw_document.get('document_id', 'unknown')}: {e}")
            return None

    def preprocess_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess a batch of legal documents.

        Args:
            documents: List of raw documents

        Returns:
            List of processed documents
        """
        processed_documents = []

        for doc in documents:
            processed = self.preprocess_document(doc)
            if processed:
                processed_documents.append(processed)

        logger.info(f"Processed {len(processed_documents)}/{len(documents)} documents successfully")
        return processed_documents

def main():
    """Test the preprocessing pipeline."""
    print("🔧 Legal Document Preprocessing Pipeline")
    print("=" * 50)

    # Initialize preprocessor
    preprocessor = LegalDocumentPreprocessor()

    # Test with sample document
    sample_doc = {
        'document_id': 'TEST_001',
        'source_system': 'TEST',
        'raw_content': 'In the Supreme Court of the United States, the plaintiff filed a motion for summary judgment pursuant to Rule 56 of the Federal Rules of Civil Procedure. The court must consider whether there are genuine issues of material fact.',
        'metadata': {
            'source': 'Test Source',
            'date': '2025-01-01'
        }
    }

    # Process document
    processed = preprocessor.preprocess_document(sample_doc)

    if processed:
        print("✅ Sample document processed successfully")
        print(f"   Document Type: {processed['document_type']}")
        print(f"   Quality Score: {processed['quality_score']}")
        print(f"   Word Count: {processed['extracted_metadata']['word_count']}")
        print(f"   Legal Terms: {processed['extracted_metadata']['legal_terms_found']}")
        print(f"   Has Citations: {processed['extracted_metadata']['has_citations']}")
        print(f"   Complexity Score: {processed['extracted_metadata']['complexity_score']}")
    else:
        print("❌ Failed to process sample document")

if __name__ == "__main__":
    main()
