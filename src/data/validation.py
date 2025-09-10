"""
Legal Document Data Validation
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module handles validation of legal document datasets for quality assurance.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalDataValidator:
    """Validates legal document datasets for quality and completeness."""

    def __init__(self):
        """Initialize the data validator."""
        self.validation_rules = {
            'required_fields': ['document_id', 'document_type', 'content'],
            'min_content_length': 50,
            'max_content_length': 1000000,
            'valid_document_types': ['contract', 'case_file', 'legal_brief', 'statute', 'regulation'],
            'min_metadata_fields': ['document_type', 'date']
        }

    def validate_legal_data(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate legal document quality.

        Args:
            dataset: List of legal documents to validate

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating {len(dataset)} legal documents")

        validation_results = {
            'total_documents': len(dataset),
            'valid_documents': 0,
            'invalid_documents': 0,
            'validation_errors': [],
            'quality_score': 0.0,
            'completeness_score': 0.0,
            'document_type_distribution': {},
            'validation_timestamp': datetime.now().isoformat()
        }

        # Validate each document
        for i, document in enumerate(dataset):
            doc_validation = self._validate_single_document(document, i)

            if doc_validation['valid']:
                validation_results['valid_documents'] += 1
            else:
                validation_results['invalid_documents'] += 1
                validation_results['validation_errors'].extend(doc_validation['errors'])

            # Track document type distribution
            doc_type = document.get('document_type', 'unknown')
            validation_results['document_type_distribution'][doc_type] = \
                validation_results['document_type_distribution'].get(doc_type, 0) + 1

        # Calculate quality scores
        validation_results['quality_score'] = self._calculate_quality_score(validation_results)
        validation_results['completeness_score'] = self._calculate_completeness_score(validation_results)

        logger.info(f"Validation completed: {validation_results['valid_documents']}/{validation_results['total_documents']} valid")

        return validation_results

    def _validate_single_document(self, document: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Validate a single legal document.

        Args:
            document: Document to validate
            index: Document index for error reporting

        Returns:
            Validation result for the document
        """
        errors = []

        # Check required fields
        for field in self.validation_rules['required_fields']:
            if field not in document:
                errors.append(f"Document {index}: Missing required field '{field}'")
            elif not document[field]:
                errors.append(f"Document {index}: Empty required field '{field}'")

        # Validate content length
        if 'content' in document:
            content_length = len(document['content'])
            if content_length < self.validation_rules['min_content_length']:
                errors.append(f"Document {index}: Content too short ({content_length} chars, min {self.validation_rules['min_content_length']})")
            elif content_length > self.validation_rules['max_content_length']:
                errors.append(f"Document {index}: Content too long ({content_length} chars, max {self.validation_rules['max_content_length']})")

        # Validate document type
        if 'document_type' in document:
            doc_type = document['document_type']
            if doc_type not in self.validation_rules['valid_document_types']:
                errors.append(f"Document {index}: Invalid document type '{doc_type}'")

        # Validate metadata
        if 'metadata' in document:
            metadata = document['metadata']
            for field in self.validation_rules['min_metadata_fields']:
                if field not in metadata:
                    errors.append(f"Document {index}: Missing metadata field '{field}'")

        # Validate document ID format
        if 'document_id' in document:
            doc_id = document['document_id']
            if not isinstance(doc_id, str) or not doc_id.strip():
                errors.append(f"Document {index}: Invalid document_id format")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _calculate_quality_score(self, validation_results: Dict[str, Any]) -> float:
        """
        Calculate overall quality score based on validation results.

        Args:
            validation_results: Validation results dictionary

        Returns:
            Quality score (0.0 to 1.0)
        """
        total_docs = validation_results['total_documents']
        if total_docs == 0:
            return 0.0

        valid_docs = validation_results['valid_documents']
        base_score = valid_docs / total_docs

        # Penalize for validation errors
        error_penalty = min(len(validation_results['validation_errors']) * 0.01, 0.2)

        return max(0.0, base_score - error_penalty)

    def _calculate_completeness_score(self, validation_results: Dict[str, Any]) -> float:
        """
        Calculate completeness score based on document type distribution.

        Args:
            validation_results: Validation results dictionary

        Returns:
            Completeness score (0.0 to 1.0)
        """
        expected_types = set(self.validation_rules['valid_document_types'])
        actual_types = set(validation_results['document_type_distribution'].keys())

        if not expected_types:
            return 1.0

        # Calculate coverage of expected document types
        type_coverage = len(actual_types.intersection(expected_types)) / len(expected_types)

        # Calculate distribution balance
        total_docs = validation_results['total_documents']
        if total_docs == 0:
            return 0.0

        distribution_scores = []
        for doc_type, count in validation_results['document_type_distribution'].items():
            if doc_type in expected_types:
                # Ideal distribution would be equal across all types
                ideal_count = total_docs / len(expected_types)
                distribution_score = 1.0 - abs(count - ideal_count) / ideal_count
                distribution_scores.append(max(0.0, distribution_score))

        distribution_balance = sum(distribution_scores) / len(distribution_scores) if distribution_scores else 0.0

        # Combine coverage and balance
        return (type_coverage * 0.6) + (distribution_balance * 0.4)

    def check_completeness(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check dataset completeness.

        Args:
            dataset: Dataset to check

        Returns:
            Completeness analysis
        """
        logger.info("Checking dataset completeness")

        completeness_analysis = {
            'total_documents': len(dataset),
            'field_completeness': {},
            'document_type_coverage': {},
            'metadata_completeness': {},
            'completeness_timestamp': datetime.now().isoformat()
        }

        if not dataset:
            return completeness_analysis

        # Check field completeness
        all_fields = set()
        for doc in dataset:
            all_fields.update(doc.keys())

        for field in all_fields:
            non_empty_count = sum(1 for doc in dataset if doc.get(field))
            completeness_analysis['field_completeness'][field] = {
                'present': non_empty_count,
                'percentage': (non_empty_count / len(dataset)) * 100
            }

        # Check document type coverage
        doc_types = {}
        for doc in dataset:
            doc_type = doc.get('document_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        completeness_analysis['document_type_coverage'] = doc_types

        # Check metadata completeness
        metadata_fields = set()
        for doc in dataset:
            if 'metadata' in doc and isinstance(doc['metadata'], dict):
                metadata_fields.update(doc['metadata'].keys())

        for field in metadata_fields:
            present_count = sum(1 for doc in dataset
                              if 'metadata' in doc and
                              isinstance(doc['metadata'], dict) and
                              doc['metadata'].get(field))
            completeness_analysis['metadata_completeness'][field] = {
                'present': present_count,
                'percentage': (present_count / len(dataset)) * 100
            }

        return completeness_analysis

    def generate_validation_report(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            dataset: Dataset to validate

        Returns:
            Comprehensive validation report
        """
        logger.info("Generating comprehensive validation report")

        # Run all validation checks
        validation_results = self.validate_legal_data(dataset)
        completeness_analysis = self.check_completeness(dataset)

        # Generate report
        report = {
            'validation_summary': validation_results,
            'completeness_analysis': completeness_analysis,
            'recommendations': self._generate_recommendations(validation_results, completeness_analysis),
            'report_timestamp': datetime.now().isoformat()
        }

        return report

    def _generate_recommendations(self, validation_results: Dict[str, Any],
                                completeness_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on validation results.

        Args:
            validation_results: Validation results
            completeness_analysis: Completeness analysis

        Returns:
            List of recommendations
        """
        recommendations = []

        # Quality recommendations
        if validation_results['quality_score'] < 0.8:
            recommendations.append("Quality score is below 80%. Review and fix validation errors.")

        if validation_results['invalid_documents'] > 0:
            recommendations.append(f"Fix {validation_results['invalid_documents']} invalid documents.")

        # Completeness recommendations
        for field, info in completeness_analysis['field_completeness'].items():
            if info['percentage'] < 90:
                recommendations.append(f"Improve completeness of field '{field}' (currently {info['percentage']:.1f}%)")

        # Document type recommendations
        expected_types = set(self.validation_rules['valid_document_types'])
        actual_types = set(validation_results['document_type_distribution'].keys())
        missing_types = expected_types - actual_types

        if missing_types:
            recommendations.append(f"Add documents of missing types: {', '.join(missing_types)}")

        return recommendations

def main():
    """Test the legal data validation system."""
    print("🔍 Legal Document Data Validation - Phase 2.1")
    print("=" * 60)

    # Initialize validator
    validator = LegalDataValidator()

    # Load sample data for testing
    from ingestion import LegalDataIngestion
    ingestion = LegalDataIngestion()
    datasets = ingestion.load_legal_datasets()

    # Validate the dataset
    sample_docs = datasets['sample_legal_docs']['documents']
    validation_report = validator.generate_validation_report(sample_docs)

    # Print results
    print(f"📊 Validation Results:")
    print(f"  Total Documents: {validation_report['validation_summary']['total_documents']}")
    print(f"  Valid Documents: {validation_report['validation_summary']['valid_documents']}")
    print(f"  Quality Score: {validation_report['validation_summary']['quality_score']:.2f}")
    print(f"  Completeness Score: {validation_report['validation_summary']['completeness_score']:.2f}")

    print(f"\n📋 Document Type Distribution:")
    for doc_type, count in validation_report['validation_summary']['document_type_distribution'].items():
        print(f"  {doc_type}: {count}")

    if validation_report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in validation_report['recommendations']:
            print(f"  - {rec}")

    print("\n✅ Legal data validation completed successfully")

if __name__ == "__main__":
    main()
