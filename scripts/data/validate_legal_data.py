#!/usr/bin/env python3
"""
Legal Data Validation Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script validates the quality and completeness of downloaded legal documents.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from config import load_config
from utils.bigquery_client import BigQueryClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalDataValidator:
    """Validator for legal document data quality."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the data validator."""
        self.config = config
        self.bq_client = BigQueryClient(config)

        # Quality thresholds
        self.min_content_length = 500
        self.min_word_count = 100
        self.max_content_length = 1000000  # 1MB limit

        # Legal document patterns
        self.legal_patterns = {
            'contract_indicators': [
                'agreement', 'contract', 'terms and conditions', 'whereas',
                'party', 'parties', 'obligation', 'liability', 'indemnification'
            ],
            'court_case_indicators': [
                'court', 'judge', 'plaintiff', 'defendant', 'motion',
                'ruling', 'decision', 'opinion', 'judgment', 'appeal'
            ],
            'brief_indicators': [
                'brief', 'argument', 'contention', 'submit', 'respectfully',
                'motion', 'response', 'reply', 'opposition'
            ]
        }

    def validate_document_content(self, document: Dict) -> Dict[str, Any]:
        """
        Validate individual document content.

        Args:
            document: Document dictionary

        Returns:
            Validation results dictionary
        """
        validation_results = {
            'document_id': document.get('document_id', 'unknown'),
            'is_valid': True,
            'issues': [],
            'quality_score': 0.0,
            'metrics': {}
        }

        content = document.get('raw_content', '')
        metadata = document.get('metadata', {})
        doc_type = document.get('document_type', '')

        # Check content length
        content_length = len(content)
        validation_results['metrics']['content_length'] = content_length

        if content_length < self.min_content_length:
            validation_results['is_valid'] = False
            validation_results['issues'].append(f"Content too short: {content_length} chars (min: {self.min_content_length})")
        elif content_length > self.max_content_length:
            validation_results['is_valid'] = False
            validation_results['issues'].append(f"Content too long: {content_length} chars (max: {self.max_content_length})")

        # Check word count
        word_count = len(content.split())
        validation_results['metrics']['word_count'] = word_count

        if word_count < self.min_word_count:
            validation_results['is_valid'] = False
            validation_results['issues'].append(f"Word count too low: {word_count} words (min: {self.min_word_count})")

        # Check for legal content indicators
        content_lower = content.lower()
        legal_indicators = self.legal_patterns.get(f'{doc_type}_indicators', [])
        if not legal_indicators:
            # Fallback to general legal indicators
            legal_indicators = (
                self.legal_patterns['contract_indicators'] +
                self.legal_patterns['court_case_indicators'] +
                self.legal_patterns['brief_indicators']
            )

        legal_indicators_found = sum(1 for indicator in legal_indicators if indicator in content_lower)
        validation_results['metrics']['legal_indicators_found'] = legal_indicators_found

        if legal_indicators_found < 3:
            validation_results['issues'].append(f"Few legal indicators found: {legal_indicators_found}")

        # Check for required metadata
        required_metadata = ['company_name', 'court', 'case_name']
        missing_metadata = []

        for field in required_metadata:
            if field in metadata and not metadata[field]:
                missing_metadata.append(field)

        if missing_metadata:
            validation_results['issues'].append(f"Missing metadata: {', '.join(missing_metadata)}")

        # Check for duplicate content
        if self._is_duplicate_content(content):
            validation_results['is_valid'] = False
            validation_results['issues'].append("Duplicate content detected")

        # Calculate quality score
        quality_score = self._calculate_quality_score(validation_results)
        validation_results['quality_score'] = quality_score

        return validation_results

    def _is_duplicate_content(self, content: str) -> bool:
        """Check if content appears to be duplicate."""
        # Simple duplicate detection based on content patterns
        lines = content.split('\n')
        unique_lines = set(lines)

        # If more than 80% of lines are unique, likely not a duplicate
        uniqueness_ratio = len(unique_lines) / len(lines) if lines else 0
        return uniqueness_ratio < 0.2

    def _calculate_quality_score(self, validation_results: Dict) -> float:
        """Calculate overall quality score for document."""
        score = 1.0

        # Deduct points for issues
        for issue in validation_results['issues']:
            if 'too short' in issue or 'too long' in issue:
                score -= 0.3
            elif 'word count' in issue:
                score -= 0.2
            elif 'legal indicators' in issue:
                score -= 0.1
            elif 'metadata' in issue:
                score -= 0.1
            elif 'duplicate' in issue:
                score -= 0.5

        # Bonus for good metrics
        metrics = validation_results['metrics']
        if metrics.get('legal_indicators_found', 0) > 5:
            score += 0.1

        return max(0.0, min(1.0, score))

    def validate_dataset(self, document_type: str = None) -> Dict[str, Any]:
        """
        Validate entire dataset from BigQuery.

        Args:
            document_type: Specific document type to validate (optional)

        Returns:
            Validation summary
        """
        logger.info(f"Validating dataset for document type: {document_type or 'all'}")

        # Query documents from BigQuery
        project_id = self.config['bigquery']['project_id']

        if document_type:
            query = f"""
            SELECT
                document_id,
                source_system,
                document_type,
                raw_content,
                metadata,
                ingestion_timestamp
            FROM `{project_id}.raw_data.legal_documents`
            WHERE document_type = '{document_type}'
            LIMIT 1000
            """
        else:
            query = f"""
            SELECT
                document_id,
                source_system,
                document_type,
                raw_content,
                metadata,
                ingestion_timestamp
            FROM `{project_id}.raw_data.legal_documents`
            LIMIT 1000
            """

        try:
            job = self.bq_client.execute_query(query)
            if not job:
                logger.error("Failed to execute validation query")
                return {}

            documents = []
            for row in job.result():
                doc = {
                    'document_id': row.document_id,
                    'source_system': row.source_system,
                    'document_type': row.document_type,
                    'raw_content': row.raw_content,
                    'metadata': json.loads(row.metadata) if row.metadata else {},
                    'ingestion_timestamp': row.ingestion_timestamp
                }
                documents.append(doc)

            logger.info(f"Retrieved {len(documents)} documents for validation")

        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return {}

        # Validate each document
        validation_results = []
        for doc in documents:
            result = self.validate_document_content(doc)
            validation_results.append(result)

        # Generate summary
        summary = self._generate_validation_summary(validation_results)

        return summary

    def _generate_validation_summary(self, validation_results: List[Dict]) -> Dict[str, Any]:
        """Generate validation summary from individual results."""
        total_documents = len(validation_results)
        valid_documents = sum(1 for r in validation_results if r['is_valid'])
        invalid_documents = total_documents - valid_documents

        # Calculate average quality score
        quality_scores = [r['quality_score'] for r in validation_results]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        # Count issues by type
        issue_counts = {}
        for result in validation_results:
            for issue in result['issues']:
                issue_type = issue.split(':')[0] if ':' in issue else issue
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Document type breakdown
        doc_type_counts = {}
        for result in validation_results:
            doc_type = result.get('document_type', 'unknown')
            doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1

        summary = {
            'validation_timestamp': datetime.now().isoformat(),
            'total_documents': total_documents,
            'valid_documents': valid_documents,
            'invalid_documents': invalid_documents,
            'validation_rate': valid_documents / total_documents if total_documents > 0 else 0,
            'average_quality_score': avg_quality_score,
            'issue_counts': issue_counts,
            'document_type_breakdown': doc_type_counts,
            'quality_distribution': {
                'excellent': sum(1 for s in quality_scores if s >= 0.9),
                'good': sum(1 for s in quality_scores if 0.7 <= s < 0.9),
                'fair': sum(1 for s in quality_scores if 0.5 <= s < 0.7),
                'poor': sum(1 for s in quality_scores if s < 0.5)
            }
        }

        return summary

    def print_validation_report(self, summary: Dict[str, Any]):
        """Print detailed validation report."""
        print("\n" + "=" * 60)
        print("📊 LEGAL DATA VALIDATION REPORT")
        print("=" * 60)

        print(f"⏱️  Validation Time: {summary['validation_timestamp']}")
        print(f"📄 Total Documents: {summary['total_documents']}")
        print(f"✅ Valid Documents: {summary['valid_documents']}")
        print(f"❌ Invalid Documents: {summary['invalid_documents']}")
        print(f"📈 Validation Rate: {summary['validation_rate']:.1%}")
        print(f"⭐ Average Quality Score: {summary['average_quality_score']:.2f}")

        print(f"\n📋 Document Type Breakdown:")
        for doc_type, count in summary['document_type_breakdown'].items():
            print(f"   {doc_type.replace('_', ' ').title()}: {count} documents")

        print(f"\n⭐ Quality Distribution:")
        quality_dist = summary['quality_distribution']
        print(f"   Excellent (≥0.9): {quality_dist['excellent']} documents")
        print(f"   Good (0.7-0.9): {quality_dist['good']} documents")
        print(f"   Fair (0.5-0.7): {quality_dist['fair']} documents")
        print(f"   Poor (<0.5): {quality_dist['poor']} documents")

        if summary['issue_counts']:
            print(f"\n⚠️  Common Issues:")
            for issue, count in sorted(summary['issue_counts'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {issue}: {count} occurrences")

        # Recommendations
        print(f"\n💡 Recommendations:")
        if summary['validation_rate'] < 0.8:
            print("   - Review data ingestion process for quality issues")
        if summary['average_quality_score'] < 0.7:
            print("   - Improve content filtering and validation")
        if 'Content too short' in summary['issue_counts']:
            print("   - Increase minimum content length threshold")
        if 'Duplicate content' in summary['issue_counts']:
            print("   - Implement better duplicate detection")

def main():
    """Main function to run data validation."""
    print("🔍 Legal Data Validation")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Initialize validator
    validator = LegalDataValidator(config)

    # Validate all documents
    summary = validator.validate_dataset()

    if summary:
        # Print validation report
        validator.print_validation_report(summary)

        # Save validation results
        results_file = Path(__file__).parent.parent.parent / 'data' / 'validation' / 'validation_results.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n💾 Validation results saved to: {results_file}")

        # Return success status
        return summary['validation_rate'] > 0.7
    else:
        print("❌ Validation failed - no data found or error occurred")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
