"""
Legal Document Data Quality Assessment
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module handles data quality assessment and monitoring for legal documents.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)

class LegalDataQualityAssessment:
    """Handles quality assessment and monitoring of legal document data."""

    def __init__(self):
        """Initialize the data quality assessment system."""
        self.quality_metrics = {
            'completeness': {
                'required_fields': ['document_id', 'document_type', 'content'],
                'weight': 0.3
            },
            'consistency': {
                'document_types': ['contract', 'case_file', 'legal_brief', 'statute', 'regulation'],
                'weight': 0.2
            },
            'accuracy': {
                'min_content_length': 50,
                'max_content_length': 1000000,
                'weight': 0.2
            },
            'relevance': {
                'legal_keywords': ['court', 'law', 'legal', 'statute', 'regulation', 'contract', 'case'],
                'weight': 0.15
            },
            'timeliness': {
                'max_age_days': 365,
                'weight': 0.15
            }
        }

        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.8,
            'acceptable': 0.7,
            'poor': 0.6,
            'unacceptable': 0.0
        }

    def assess_document_quality(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess quality of a single legal document.

        Args:
            document: Legal document to assess

        Returns:
            Quality assessment results
        """
        logger.debug(f"Assessing quality for document: {document.get('document_id', 'unknown')}")

        assessment = {
            'document_id': document.get('document_id'),
            'assessment_timestamp': datetime.now().isoformat(),
            'quality_scores': {},
            'issues': [],
            'recommendations': []
        }

        # Assess each quality dimension
        for dimension, config in self.quality_metrics.items():
            score, issues = self._assess_dimension(document, dimension, config)
            assessment['quality_scores'][dimension] = score

            if issues:
                assessment['issues'].extend(issues)

        # Calculate overall quality score
        overall_score = self._calculate_overall_score(assessment['quality_scores'])
        assessment['overall_quality_score'] = overall_score
        assessment['quality_grade'] = self._get_quality_grade(overall_score)

        # Generate recommendations
        assessment['recommendations'] = self._generate_recommendations(assessment)

        logger.debug(f"Quality assessment completed: {assessment['quality_grade']}")
        return assessment

    def _assess_dimension(self, document: Dict[str, Any], dimension: str, config: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Assess a specific quality dimension.

        Args:
            document: Document to assess
            dimension: Quality dimension name
            config: Configuration for the dimension

        Returns:
            Tuple of (score, issues)
        """
        issues = []

        if dimension == 'completeness':
            return self._assess_completeness(document, config, issues)
        elif dimension == 'consistency':
            return self._assess_consistency(document, config, issues)
        elif dimension == 'accuracy':
            return self._assess_accuracy(document, config, issues)
        elif dimension == 'relevance':
            return self._assess_relevance(document, config, issues)
        elif dimension == 'timeliness':
            return self._assess_timeliness(document, config, issues)
        else:
            return 0.0, [f"Unknown quality dimension: {dimension}"]

    def _assess_completeness(self, document: Dict[str, Any], config: Dict[str, Any], issues: List[str]) -> Tuple[float, List[str]]:
        """Assess document completeness."""
        required_fields = config['required_fields']
        present_fields = 0

        for field in required_fields:
            if field in document and document[field]:
                present_fields += 1
            else:
                issues.append(f"Missing or empty required field: {field}")

        # Check metadata completeness
        metadata = document.get('metadata', {})
        if not metadata:
            issues.append("Missing metadata section")
        else:
            # Check for essential metadata fields
            essential_metadata = ['document_type', 'date']
            for field in essential_metadata:
                if field not in metadata:
                    issues.append(f"Missing essential metadata field: {field}")

        score = present_fields / len(required_fields)
        return score, issues

    def _assess_consistency(self, document: Dict[str, Any], config: Dict[str, Any], issues: List[str]) -> Tuple[float, List[str]]:
        """Assess document consistency."""
        valid_types = config['document_types']
        doc_type = document.get('document_type', '')

        if doc_type not in valid_types:
            issues.append(f"Invalid document type: {doc_type}")
            return 0.0, issues

        # Check consistency between document type and content
        content = document.get('content', '').lower()
        type_consistency_score = self._check_type_content_consistency(doc_type, content)

        if type_consistency_score < 0.5:
            issues.append(f"Document type '{doc_type}' inconsistent with content")

        return type_consistency_score, issues

    def _check_type_content_consistency(self, doc_type: str, content: str) -> float:
        """Check consistency between document type and content."""
        type_keywords = {
            'contract': ['agreement', 'party', 'terms', 'conditions', 'signature'],
            'case_file': ['plaintiff', 'defendant', 'court', 'judge', 'case'],
            'legal_brief': ['argument', 'authority', 'precedent', 'brief', 'motion'],
            'statute': ['section', 'subsection', 'law', 'statute', 'regulation'],
            'regulation': ['regulation', 'rule', 'compliance', 'requirement', 'standard']
        }

        keywords = type_keywords.get(doc_type, [])
        if not keywords:
            return 0.5  # Neutral score for unknown types

        matches = sum(1 for keyword in keywords if keyword in content)
        return matches / len(keywords)

    def _assess_accuracy(self, document: Dict[str, Any], config: Dict[str, Any], issues: List[str]) -> Tuple[float, List[str]]:
        """Assess document accuracy."""
        content = document.get('content', '')
        content_length = len(content)

        min_length = config['min_content_length']
        max_length = config['max_content_length']

        if content_length < min_length:
            issues.append(f"Content too short: {content_length} chars (min: {min_length})")
            return 0.0, issues
        elif content_length > max_length:
            issues.append(f"Content too long: {content_length} chars (max: {max_length})")
            return 0.5, issues

        # Check for common accuracy issues
        accuracy_score = 1.0

        # Check for encoding issues
        if any(ord(char) > 127 for char in content[:1000]):  # Check first 1000 chars
            if not self._is_valid_unicode(content[:1000]):
                issues.append("Potential encoding issues detected")
                accuracy_score -= 0.2

        # Check for excessive whitespace
        if content.count('  ') > len(content) * 0.1:  # More than 10% double spaces
            issues.append("Excessive whitespace detected")
            accuracy_score -= 0.1

        # Check for missing punctuation
        sentences = content.split('.')
        if len(sentences) > 10:  # Only check if document has multiple sentences
            sentences_without_punctuation = sum(1 for s in sentences if s.strip() and not s.strip()[-1] in '.!?')
            if sentences_without_punctuation > len(sentences) * 0.3:
                issues.append("Many sentences missing proper punctuation")
                accuracy_score -= 0.1

        return max(0.0, accuracy_score), issues

    def _is_valid_unicode(self, text: str) -> bool:
        """Check if text contains valid Unicode characters."""
        try:
            text.encode('utf-8').decode('utf-8')
            return True
        except UnicodeError:
            return False

    def _assess_relevance(self, document: Dict[str, Any], config: Dict[str, Any], issues: List[str]) -> Tuple[float, List[str]]:
        """Assess document relevance to legal domain."""
        content = document.get('content', '').lower()
        legal_keywords = config['legal_keywords']

        keyword_matches = sum(1 for keyword in legal_keywords if keyword in content)
        relevance_score = keyword_matches / len(legal_keywords)

        if relevance_score < 0.3:
            issues.append("Document appears to have low legal relevance")

        return relevance_score, issues

    def _assess_timeliness(self, document: Dict[str, Any], config: Dict[str, Any], issues: List[str]) -> Tuple[float, List[str]]:
        """Assess document timeliness."""
        metadata = document.get('metadata', {})
        date_str = metadata.get('date', '')

        if not date_str:
            issues.append("No date information available")
            return 0.5, issues

        try:
            # Parse date (assuming ISO format or common formats)
            if '-' in date_str:
                doc_date = datetime.fromisoformat(date_str.split('T')[0])
            else:
                # Try other common formats
                doc_date = datetime.strptime(date_str, '%Y-%m-%d')

            age_days = (datetime.now() - doc_date).days
            max_age = config['max_age_days']

            if age_days > max_age:
                issues.append(f"Document is {age_days} days old (max recommended: {max_age})")
                return max(0.0, 1.0 - (age_days - max_age) / max_age), issues

            return 1.0, issues

        except ValueError:
            issues.append(f"Invalid date format: {date_str}")
            return 0.0, issues

    def _calculate_overall_score(self, quality_scores: Dict[str, float]) -> float:
        """Calculate overall quality score."""
        weighted_score = 0.0
        total_weight = 0.0

        for dimension, score in quality_scores.items():
            weight = self.quality_metrics[dimension]['weight']
            weighted_score += score * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _get_quality_grade(self, score: float) -> str:
        """Get quality grade based on score."""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['acceptable']:
            return 'acceptable'
        elif score >= self.quality_thresholds['poor']:
            return 'poor'
        else:
            return 'unacceptable'

    def _generate_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on assessment."""
        recommendations = []
        score = assessment['overall_quality_score']

        if score < 0.8:
            recommendations.append("Overall quality below 80% - review and improve document")

        # Specific recommendations based on issues
        issues = assessment['issues']
        if any('Missing' in issue for issue in issues):
            recommendations.append("Add missing required fields")

        if any('Invalid' in issue for issue in issues):
            recommendations.append("Correct invalid field values")

        if any('encoding' in issue.lower() for issue in issues):
            recommendations.append("Fix character encoding issues")

        if any('whitespace' in issue.lower() for issue in issues):
            recommendations.append("Clean up excessive whitespace")

        if any('relevance' in issue.lower() for issue in issues):
            recommendations.append("Ensure document contains legal content")

        return recommendations

    def assess_batch_quality(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess quality of a batch of legal documents.

        Args:
            documents: List of legal documents to assess

        Returns:
            Batch quality assessment results
        """
        logger.info(f"Starting batch quality assessment of {len(documents)} documents")

        assessments = []
        for document in documents:
            try:
                assessment = self.assess_document_quality(document)
                assessments.append(assessment)
            except Exception as e:
                logger.error(f"Error assessing document {document.get('document_id', 'unknown')}: {e}")

        # Calculate batch statistics
        batch_stats = self._calculate_batch_statistics(assessments)

        batch_assessment = {
            'total_documents': len(documents),
            'assessed_documents': len(assessments),
            'assessment_timestamp': datetime.now().isoformat(),
            'batch_statistics': batch_stats,
            'individual_assessments': assessments
        }

        logger.info(f"Batch quality assessment completed: {len(assessments)} documents assessed")
        return batch_assessment

    def _calculate_batch_statistics(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate batch-level quality statistics."""
        if not assessments:
            return {}

        # Overall quality scores
        overall_scores = [a['overall_quality_score'] for a in assessments]

        # Quality grade distribution
        grade_distribution = {}
        for assessment in assessments:
            grade = assessment['quality_grade']
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

        # Dimension scores
        dimension_scores = {}
        for dimension in self.quality_metrics.keys():
            scores = [a['quality_scores'][dimension] for a in assessments if dimension in a['quality_scores']]
            if scores:
                dimension_scores[dimension] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'std': statistics.stdev(scores) if len(scores) > 1 else 0.0
                }

        # Common issues
        all_issues = []
        for assessment in assessments:
            all_issues.extend(assessment['issues'])

        issue_frequency = {}
        for issue in all_issues:
            issue_frequency[issue] = issue_frequency.get(issue, 0) + 1

        # Sort issues by frequency
        common_issues = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'overall_quality': {
                'mean': statistics.mean(overall_scores),
                'median': statistics.median(overall_scores),
                'min': min(overall_scores),
                'max': max(overall_scores),
                'std': statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0.0
            },
            'grade_distribution': grade_distribution,
            'dimension_scores': dimension_scores,
            'common_issues': common_issues,
            'documents_above_threshold': sum(1 for score in overall_scores if score >= 0.8)
        }

def main():
    """Test the legal document quality assessment system."""
    print("📊 Legal Document Quality Assessment - Phase 2.2")
    print("=" * 60)

    # Initialize quality assessor
    quality_assessor = LegalDataQualityAssessment()

    # Load sample data for testing
    from ingestion import LegalDataIngestion
    ingestion = LegalDataIngestion()
    datasets = ingestion.load_legal_datasets()

    # Get first few documents for testing
    sample_docs = datasets['sample_legal_docs']['documents'][:5]

    print(f"📋 Testing quality assessment with {len(sample_docs)} sample documents")

    # Test individual document assessment
    for i, doc in enumerate(sample_docs):
        print(f"\n📄 Document {i+1}: {doc['document_id']}")
        assessment = quality_assessor.assess_document_quality(doc)

        print(f"  Overall Score: {assessment['overall_quality_score']:.2f}")
        print(f"  Quality Grade: {assessment['quality_grade']}")
        print(f"  Issues: {len(assessment['issues'])}")

        if assessment['issues']:
            print(f"  Top Issues:")
            for issue in assessment['issues'][:3]:
                print(f"    - {issue}")

        if assessment['recommendations']:
            print(f"  Recommendations:")
            for rec in assessment['recommendations'][:2]:
                print(f"    - {rec}")

    # Test batch assessment
    print(f"\n📊 Batch Quality Assessment:")
    batch_assessment = quality_assessor.assess_batch_quality(sample_docs)
    batch_stats = batch_assessment['batch_statistics']

    print(f"  Total Documents: {batch_assessment['total_documents']}")
    print(f"  Assessed Documents: {batch_assessment['assessed_documents']}")
    print(f"  Mean Quality Score: {batch_stats['overall_quality']['mean']:.2f}")
    print(f"  Documents Above 80%: {batch_stats['documents_above_threshold']}")

    print(f"  Quality Grade Distribution:")
    for grade, count in batch_stats['grade_distribution'].items():
        print(f"    {grade}: {count}")

    print(f"\n✅ Legal document quality assessment test completed successfully")

if __name__ == "__main__":
    main()
