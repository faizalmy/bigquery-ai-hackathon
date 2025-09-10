"""
Legal Document Data Preprocessing
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module handles text cleaning, normalization, and preprocessing of legal documents
for BigQuery AI function processing.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class LegalDocumentPreprocessor:
    """Handles preprocessing of legal documents for AI analysis."""

    def __init__(self):
        """Initialize the legal document preprocessor."""
        self.legal_patterns = {
            'case_citations': r'\b\d+\s+[A-Z][a-z]+\s+\d+\b',
            'statute_citations': r'\b\d+\s+U\.S\.C\.\s+§\s*\d+\b',
            'court_names': r'\b(?:Supreme Court|District Court|Court of Appeals|Circuit Court)\b',
            'legal_terms': r'\b(?:plaintiff|defendant|petitioner|respondent|appellant|appellee)\b',
            'dates': r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            'paragraphs': r'\n\s*\n',
            'sections': r'§\s*\d+',
            'subsections': r'\(\w+\)'
        }

        self.cleaning_rules = {
            'remove_extra_whitespace': True,
            'normalize_quotes': True,
            'remove_control_characters': True,
            'normalize_line_breaks': True,
            'preserve_legal_formatting': True
        }

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize legal document text.

        Args:
            text: Raw legal document text

        Returns:
            Cleaned and normalized text
        """
        if not text or not isinstance(text, str):
            return ""

        logger.debug("Starting text cleaning process")

        # Remove control characters
        if self.cleaning_rules['remove_control_characters']:
            text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # Normalize quotes
        if self.cleaning_rules['normalize_quotes']:
            text = re.sub(r'["""]', '"', text)
            # Note: Smart single quotes normalization removed due to encoding issues

        # Normalize line breaks
        if self.cleaning_rules['normalize_line_breaks']:
            text = re.sub(r'\r\n', '\n', text)
            text = re.sub(r'\r', '\n', text)

        # Remove extra whitespace
        if self.cleaning_rules['remove_extra_whitespace']:
            # Preserve paragraph breaks
            text = re.sub(r'\n\s*\n', '\n\n', text)
            # Remove extra spaces within lines
            text = re.sub(r'[ \t]+', ' ', text)
            # Remove leading/trailing whitespace from lines
            text = '\n'.join(line.strip() for line in text.split('\n'))

        # Preserve legal formatting
        if self.cleaning_rules['preserve_legal_formatting']:
            text = self._preserve_legal_formatting(text)

        logger.debug("Text cleaning completed")
        return text.strip()

    def _preserve_legal_formatting(self, text: str) -> str:
        """
        Preserve important legal document formatting.

        Args:
            text: Text to process

        Returns:
            Text with preserved legal formatting
        """
        # Preserve section numbers
        text = re.sub(r'§\s*(\d+)', r'§ \1', text)

        # Preserve subsection formatting
        text = re.sub(r'\(([a-z])\)', r'(\1)', text)

        # Preserve case citations
        text = re.sub(r'(\d+)\s+([A-Z][a-z]+)\s+(\d+)', r'\1 \2 \3', text)

        return text

    def extract_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from legal document.

        Args:
            document: Legal document dictionary

        Returns:
            Extracted metadata dictionary
        """
        logger.debug(f"Extracting metadata for document: {document.get('document_id', 'unknown')}")

        content = document.get('content', '')
        if not content:
            return {}

        metadata = {
            'extraction_timestamp': datetime.now().isoformat(),
            'document_length': len(content),
            'word_count': len(content.split()),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'line_count': len([l for l in content.split('\n') if l.strip()])
        }

        # Extract legal-specific metadata
        legal_metadata = self._extract_legal_metadata(content)
        metadata.update(legal_metadata)

        # Extract document structure
        structure_metadata = self._extract_document_structure(content)
        metadata.update(structure_metadata)

        logger.debug(f"Metadata extraction completed: {len(metadata)} fields")
        return metadata

    def _extract_legal_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract legal-specific metadata from document content.

        Args:
            content: Document content

        Returns:
            Legal metadata dictionary
        """
        legal_metadata = {}

        # Extract case citations
        case_citations = re.findall(self.legal_patterns['case_citations'], content, re.IGNORECASE)
        if case_citations:
            legal_metadata['case_citations'] = list(set(case_citations))

        # Extract statute citations
        statute_citations = re.findall(self.legal_patterns['statute_citations'], content, re.IGNORECASE)
        if statute_citations:
            legal_metadata['statute_citations'] = list(set(statute_citations))

        # Extract court names
        courts = re.findall(self.legal_patterns['court_names'], content, re.IGNORECASE)
        if courts:
            legal_metadata['courts_mentioned'] = list(set(courts))

        # Extract legal terms
        legal_terms = re.findall(self.legal_patterns['legal_terms'], content, re.IGNORECASE)
        if legal_terms:
            legal_metadata['legal_terms'] = list(set(legal_terms))

        # Extract dates
        dates = re.findall(self.legal_patterns['dates'], content, re.IGNORECASE)
        if dates:
            legal_metadata['dates_mentioned'] = list(set(dates))

        # Extract sections
        sections = re.findall(self.legal_patterns['sections'], content)
        if sections:
            legal_metadata['sections'] = list(set(sections))

        return legal_metadata

    def _extract_document_structure(self, content: str) -> Dict[str, Any]:
        """
        Extract document structure information.

        Args:
            content: Document content

        Returns:
            Structure metadata dictionary
        """
        structure_metadata = {}

        # Count different structural elements
        structure_metadata['has_headers'] = bool(re.search(r'^[A-Z][A-Z\s]+$', content, re.MULTILINE))
        structure_metadata['has_numbered_sections'] = bool(re.search(r'^\d+\.', content, re.MULTILINE))
        structure_metadata['has_bullet_points'] = bool(re.search(r'^[\-\*\+]', content, re.MULTILINE))
        structure_metadata['has_tables'] = bool(re.search(r'\|.*\|', content))

        # Extract headers
        headers = re.findall(r'^([A-Z][A-Z\s]+)$', content, re.MULTILINE)
        if headers:
            structure_metadata['headers'] = [h.strip() for h in headers if len(h.strip()) > 3]

        # Extract numbered sections
        numbered_sections = re.findall(r'^(\d+\.\s*[^\n]+)', content, re.MULTILINE)
        if numbered_sections:
            structure_metadata['numbered_sections'] = [s.strip() for s in numbered_sections]

        return structure_metadata

    def classify_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify legal document type and characteristics.

        Args:
            document: Legal document dictionary

        Returns:
            Classification results
        """
        logger.debug(f"Classifying document: {document.get('document_id', 'unknown')}")

        content = document.get('content', '').lower()
        doc_type = document.get('document_type', '')

        classification = {
            'document_type': doc_type,
            'confidence': 1.0,
            'characteristics': {},
            'classification_timestamp': datetime.now().isoformat()
        }

        # Classify based on content patterns
        if 'contract' in doc_type.lower():
            classification['characteristics'] = self._classify_contract(content)
        elif 'case' in doc_type.lower():
            classification['characteristics'] = self._classify_case_file(content)
        elif 'brief' in doc_type.lower():
            classification['characteristics'] = self._classify_legal_brief(content)
        elif 'statute' in doc_type.lower():
            classification['characteristics'] = self._classify_statute(content)
        else:
            classification['characteristics'] = self._classify_generic(content)

        # Determine urgency level
        classification['urgency_level'] = self._determine_urgency(content)

        # Determine complexity level
        classification['complexity_level'] = self._determine_complexity(content)

        logger.debug(f"Document classification completed: {classification['document_type']}")
        return classification

    def _classify_contract(self, content: str) -> Dict[str, Any]:
        """Classify contract-specific characteristics."""
        return {
            'has_parties': bool(re.search(r'\b(?:party|parties|between|agreement)\b', content)),
            'has_terms': bool(re.search(r'\b(?:terms|conditions|provisions)\b', content)),
            'has_termination': bool(re.search(r'\b(?:termination|expiration|end)\b', content)),
            'has_payment': bool(re.search(r'\b(?:payment|fee|cost|price)\b', content)),
            'has_liability': bool(re.search(r'\b(?:liability|indemnification|damages)\b', content))
        }

    def _classify_case_file(self, content: str) -> Dict[str, Any]:
        """Classify case file-specific characteristics."""
        return {
            'has_plaintiff': bool(re.search(r'\b(?:plaintiff|petitioner|complainant)\b', content)),
            'has_defendant': bool(re.search(r'\b(?:defendant|respondent)\b', content)),
            'has_court': bool(re.search(r'\b(?:court|judge|magistrate)\b', content)),
            'has_judgment': bool(re.search(r'\b(?:judgment|decision|ruling|order)\b', content)),
            'has_legal_issues': bool(re.search(r'\b(?:issue|question|matter)\b', content))
        }

    def _classify_legal_brief(self, content: str) -> Dict[str, Any]:
        """Classify legal brief-specific characteristics."""
        return {
            'has_arguments': bool(re.search(r'\b(?:argument|contend|assert|claim)\b', content)),
            'has_authorities': bool(re.search(r'\b(?:authority|precedent|case law)\b', content)),
            'has_facts': bool(re.search(r'\b(?:facts|circumstances|background)\b', content)),
            'has_legal_standards': bool(re.search(r'\b(?:standard|test|criteria)\b', content)),
            'has_conclusion': bool(re.search(r'\b(?:conclusion|prayer|relief)\b', content))
        }

    def _classify_statute(self, content: str) -> Dict[str, Any]:
        """Classify statute-specific characteristics."""
        return {
            'has_sections': bool(re.search(r'§\s*\d+', content)),
            'has_subsections': bool(re.search(r'\(\w+\)', content)),
            'has_definitions': bool(re.search(r'\b(?:means|defined|definition)\b', content)),
            'has_penalties': bool(re.search(r'\b(?:penalty|fine|punishment)\b', content)),
            'has_effective_date': bool(re.search(r'\b(?:effective|commence|begin)\b', content))
        }

    def _classify_generic(self, content: str) -> Dict[str, Any]:
        """Classify generic legal document characteristics."""
        return {
            'has_legal_language': bool(re.search(r'\b(?:whereas|hereby|therefore|notwithstanding)\b', content)),
            'has_citations': bool(re.search(r'\b\d+\s+[A-Z][a-z]+\s+\d+\b', content)),
            'has_dates': bool(re.search(r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b', content)),
            'has_parties': bool(re.search(r'\b(?:plaintiff|defendant|petitioner|respondent)\b', content)),
            'has_legal_terms': bool(re.search(r'\b(?:court|judge|law|legal|statute|regulation)\b', content))
        }

    def _determine_urgency(self, content: str) -> str:
        """Determine document urgency level."""
        urgent_keywords = ['urgent', 'emergency', 'immediate', 'asap', 'deadline', 'expire']
        high_urgency_keywords = ['emergency', 'immediate', 'deadline']

        content_lower = content.lower()

        if any(keyword in content_lower for keyword in high_urgency_keywords):
            return 'high'
        elif any(keyword in content_lower for keyword in urgent_keywords):
            return 'medium'
        else:
            return 'low'

    def _determine_complexity(self, content: str) -> str:
        """Determine document complexity level."""
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))

        if word_count > 5000 or sentence_count > 200:
            return 'high'
        elif word_count > 2000 or sentence_count > 100:
            return 'medium'
        else:
            return 'low'

    def preprocess_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline for a legal document.

        Args:
            document: Raw legal document

        Returns:
            Preprocessed document with cleaned content and extracted metadata
        """
        logger.info(f"Preprocessing document: {document.get('document_id', 'unknown')}")

        # Clean the text
        cleaned_content = self.clean_text(document.get('content', ''))

        # Extract metadata
        extracted_metadata = self.extract_metadata(document)

        # Classify document
        classification = self.classify_document(document)

        # Create preprocessed document
        preprocessed_doc = {
            'document_id': document.get('document_id'),
            'document_type': document.get('document_type'),
            'title': document.get('title'),
            'original_content': document.get('content'),
            'cleaned_content': cleaned_content,
            'metadata': {
                **document.get('metadata', {}),
                **extracted_metadata
            },
            'classification': classification,
            'preprocessing_timestamp': datetime.now().isoformat()
        }

        logger.info(f"Document preprocessing completed: {document.get('document_id', 'unknown')}")
        return preprocessed_doc

    def preprocess_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess a batch of legal documents.

        Args:
            documents: List of raw legal documents

        Returns:
            List of preprocessed documents
        """
        logger.info(f"Starting batch preprocessing of {len(documents)} documents")

        preprocessed_docs = []
        for i, document in enumerate(documents):
            try:
                preprocessed_doc = self.preprocess_document(document)
                preprocessed_docs.append(preprocessed_doc)

                if (i + 1) % 50 == 0:
                    logger.info(f"Processed {i + 1}/{len(documents)} documents")

            except Exception as e:
                logger.error(f"Error preprocessing document {document.get('document_id', 'unknown')}: {e}")
                # Add original document with error flag
                error_doc = document.copy()
                error_doc['preprocessing_error'] = str(e)
                preprocessed_docs.append(error_doc)

        logger.info(f"Batch preprocessing completed: {len(preprocessed_docs)} documents processed")
        return preprocessed_docs

def main():
    """Test the legal document preprocessing system."""
    print("🔧 Legal Document Preprocessing - Phase 2.2")
    print("=" * 60)

    # Initialize preprocessor
    preprocessor = LegalDocumentPreprocessor()

    # Load sample data for testing
    from ingestion import LegalDataIngestion
    ingestion = LegalDataIngestion()
    datasets = ingestion.load_legal_datasets()

    # Get first few documents for testing
    sample_docs = datasets['sample_legal_docs']['documents'][:3]

    print(f"📋 Testing preprocessing with {len(sample_docs)} sample documents")

    # Test preprocessing
    for i, doc in enumerate(sample_docs):
        print(f"\n📄 Document {i+1}: {doc['document_id']}")
        print(f"  Type: {doc['document_type']}")
        print(f"  Original length: {len(doc['content'])} characters")

        # Preprocess document
        preprocessed = preprocessor.preprocess_document(doc)

        print(f"  Cleaned length: {len(preprocessed['cleaned_content'])} characters")
        print(f"  Word count: {preprocessed['metadata']['word_count']}")
        print(f"  Paragraph count: {preprocessed['metadata']['paragraph_count']}")
        print(f"  Urgency: {preprocessed['classification']['urgency_level']}")
        print(f"  Complexity: {preprocessed['classification']['complexity_level']}")

        # Show extracted legal metadata
        legal_metadata = {k: v for k, v in preprocessed['metadata'].items()
                         if k in ['case_citations', 'statute_citations', 'courts_mentioned', 'legal_terms']}
        if legal_metadata:
            print(f"  Legal elements: {legal_metadata}")

    print(f"\n✅ Legal document preprocessing test completed successfully")

if __name__ == "__main__":
    main()
