"""
BigQuery AI Functions Implementation
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements Track 1 BigQuery AI functions for legal document processing:
- ML.GENERATE_TEXT: Document summarization
- AI.GENERATE_TABLE: Legal data extraction
- AI.GENERATE_BOOL: Urgency detection
- AI.FORECAST: Case outcome prediction
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)

class BigQueryAIFunctions:
    """Implements Track 1 BigQuery AI functions for legal document processing."""

    def __init__(self):
        """Initialize BigQuery AI functions."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']

    def ml_generate_text_summarization(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement ML.GENERATE_TEXT for document summarization.

        Args:
            document_id: Specific document ID to summarize (optional)
            limit: Number of documents to process (default: 10)

        Returns:
            Dict containing summarization results
        """
        try:
            logger.info(f"Starting ML.GENERATE_TEXT summarization...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build query
            if document_id:
                where_clause = f"WHERE document_id = '{document_id}'"
            else:
                where_clause = f"ORDER BY created_at DESC LIMIT {limit}"

            query = f"""
            SELECT
                document_id,
                document_type,
                content,
                ML.GENERATE_TEXT(
                    MODEL `{self.project_id}.ai_models.gemini_pro`,
                    CONCAT(
                        'Summarize this legal document in 2-3 sentences. ',
                        'Focus on the key legal issues, parties involved, and main outcome. ',
                        'Document: ', content
                    ),
                    STRUCT(
                        0.1 AS temperature,
                        1024 AS max_output_tokens,
                        0.8 AS top_p,
                        40 AS top_k
                    )
                ) AS summary_result
            FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
            {where_clause}
            """

            logger.info("Executing ML.GENERATE_TEXT query...")
            result = self.bigquery_client.execute_query(query)

            # Process results
            summaries = []
            for row in result:
                summary_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'content_length': len(row.content),
                    'summary': row.summary_result[0]['ml_generate_text_result'] if row.summary_result else None,
                    'created_at': datetime.now().isoformat()
                }
                summaries.append(summary_data)

            logger.info(f"Generated {len(summaries)} document summaries")

            return {
                'function': 'ML.GENERATE_TEXT',
                'purpose': 'Document Summarization',
                'total_documents': len(summaries),
                'summaries': summaries,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"ML.GENERATE_TEXT summarization failed: {e}")
            raise

    def ai_generate_table_extraction(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement AI.GENERATE_TABLE for legal data extraction.

        Args:
            document_id: Specific document ID to extract from (optional)
            limit: Number of documents to process (default: 10)

        Returns:
            Dict containing extraction results
        """
        try:
            logger.info(f"Starting AI.GENERATE_TABLE extraction...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build query
            if document_id:
                where_clause = f"WHERE document_id = '{document_id}'"
            else:
                where_clause = f"ORDER BY created_at DESC LIMIT {limit}"

            query = f"""
            SELECT
                document_id,
                document_type,
                content,
                AI.GENERATE_TABLE(
                    MODEL `{self.project_id}.ai_models.gemini_pro`,
                    CONCAT(
                        'Extract the following information from this legal document as a table: ',
                        '1. Court Name, 2. Case Number, 3. Date, 4. Judge, 5. Parties, 6. Legal Issues, 7. Outcome. ',
                        'Document: ', content
                    ),
                    STRUCT(
                        0.1 AS temperature,
                        1024 AS max_output_tokens
                    )
                ) AS extraction_result
            FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
            {where_clause}
            """

            logger.info("Executing AI.GENERATE_TABLE query...")
            result = self.bigquery_client.execute_query(query)

            # Process results
            extractions = []
            for row in result:
                extraction_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'content_length': len(row.content),
                    'extracted_data': row.extraction_result[0]['ai_generate_table_result'] if row.extraction_result else None,
                    'created_at': datetime.now().isoformat()
                }
                extractions.append(extraction_data)

            logger.info(f"Generated {len(extractions)} data extractions")

            return {
                'function': 'AI.GENERATE_TABLE',
                'purpose': 'Legal Data Extraction',
                'total_documents': len(extractions),
                'extractions': extractions,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI.GENERATE_TABLE extraction failed: {e}")
            raise

    def ai_generate_bool_urgency(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement AI.GENERATE_BOOL for urgency detection.

        Args:
            document_id: Specific document ID to analyze (optional)
            limit: Number of documents to process (default: 10)

        Returns:
            Dict containing urgency detection results
        """
        try:
            logger.info(f"Starting AI.GENERATE_BOOL urgency detection...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build query
            if document_id:
                where_clause = f"WHERE document_id = '{document_id}'"
            else:
                where_clause = f"ORDER BY created_at DESC LIMIT {limit}"

            query = f"""
            SELECT
                document_id,
                document_type,
                content,
                AI.GENERATE_BOOL(
                    MODEL `{self.project_id}.ai_models.gemini_pro`,
                    CONCAT(
                        'Is this legal document urgent? Consider factors like: ',
                        '1. Time-sensitive deadlines, 2. Emergency situations, 3. Immediate legal action required, ',
                        '4. Court dates approaching, 5. Statute of limitations. ',
                        'Document: ', content
                    ),
                    STRUCT(
                        0.1 AS temperature
                    )
                ) AS urgency_result
            FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
            {where_clause}
            """

            logger.info("Executing AI.GENERATE_BOOL query...")
            result = self.bigquery_client.execute_query(query)

            # Process results
            urgency_analyses = []
            for row in result:
                urgency_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'content_length': len(row.content),
                    'is_urgent': row.urgency_result[0]['ai_generate_bool_result'] if row.urgency_result else None,
                    'created_at': datetime.now().isoformat()
                }
                urgency_analyses.append(urgency_data)

            logger.info(f"Generated {len(urgency_analyses)} urgency analyses")

            return {
                'function': 'AI.GENERATE_BOOL',
                'purpose': 'Urgency Detection',
                'total_documents': len(urgency_analyses),
                'urgency_analyses': urgency_analyses,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI.GENERATE_BOOL urgency detection failed: {e}")
            raise

    def ai_forecast_outcome(self, case_type: str = "case_law", limit: int = 10) -> Dict[str, Any]:
        """
        Implement AI.FORECAST for case outcome prediction.

        Args:
            case_type: Type of cases to analyze (default: "case_law")
            limit: Number of cases to process (default: 10)

        Returns:
            Dict containing forecast results
        """
        try:
            logger.info(f"Starting AI.FORECAST outcome prediction...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # First, create time series data from our legal documents
            # This is a simplified approach - in practice, you'd have historical case outcomes

            # Create sample time series data for demonstration
            query = f"""
            WITH case_timeline AS (
                SELECT
                    document_id,
                    document_type,
                    created_at,
                    LENGTH(content) as content_length,
                    CASE
                        WHEN LENGTH(content) > 5000 THEN 0.8  -- Longer documents often have more complex outcomes
                        WHEN LENGTH(content) > 2000 THEN 0.6  -- Medium complexity
                        ELSE 0.4  -- Shorter documents
                    END as outcome_score
                FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
                WHERE document_type = '{case_type}'
                ORDER BY created_at DESC
                LIMIT {limit}
            )
            SELECT
                document_id,
                document_type,
                created_at,
                content_length,
                outcome_score,
                AI.FORECAST(
                    MODEL `{self.project_id}.ai_models.timesfm`,
                    outcome_score,
                    STRUCT(
                        7 AS horizon,  -- 7 days ahead
                        'DAILY' AS frequency
                    )
                ) AS forecast_result
            FROM case_timeline
            """

            logger.info("Executing AI.FORECAST query...")
            result = self.bigquery_client.execute_query(query)

            # Process results
            forecasts = []
            for row in result:
                forecast_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'created_at': row.created_at,
                    'content_length': row.content_length,
                    'current_outcome_score': row.outcome_score,
                    'forecast': row.forecast_result[0]['ai_forecast_result'] if row.forecast_result else None,
                    'created_at': datetime.now().isoformat()
                }
                forecasts.append(forecast_data)

            logger.info(f"Generated {len(forecasts)} outcome forecasts")

            return {
                'function': 'AI.FORECAST',
                'purpose': 'Case Outcome Prediction',
                'total_documents': len(forecasts),
                'forecasts': forecasts,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI.FORECAST outcome prediction failed: {e}")
            raise

    def run_all_track1_functions(self, limit: int = 5) -> Dict[str, Any]:
        """
        Run all Track 1 functions on sample documents.

        Args:
            limit: Number of documents to process for each function

        Returns:
            Dict containing results from all functions
        """
        try:
            logger.info("Running all Track 1 BigQuery AI functions...")

            results = {
                'timestamp': datetime.now().isoformat(),
                'functions_executed': [],
                'total_documents_processed': 0
            }

            # Run ML.GENERATE_TEXT
            try:
                summary_results = self.ml_generate_text_summarization(limit=limit)
                results['ml_generate_text'] = summary_results
                results['functions_executed'].append('ML.GENERATE_TEXT')
                results['total_documents_processed'] += summary_results['total_documents']
            except Exception as e:
                logger.error(f"ML.GENERATE_TEXT failed: {e}")
                results['ml_generate_text'] = {'error': str(e)}

            # Run AI.GENERATE_TABLE
            try:
                extraction_results = self.ai_generate_table_extraction(limit=limit)
                results['ai_generate_table'] = extraction_results
                results['functions_executed'].append('AI.GENERATE_TABLE')
                results['total_documents_processed'] += extraction_results['total_documents']
            except Exception as e:
                logger.error(f"AI.GENERATE_TABLE failed: {e}")
                results['ai_generate_table'] = {'error': str(e)}

            # Run AI.GENERATE_BOOL
            try:
                urgency_results = self.ai_generate_bool_urgency(limit=limit)
                results['ai_generate_bool'] = urgency_results
                results['functions_executed'].append('AI.GENERATE_BOOL')
                results['total_documents_processed'] += urgency_results['total_documents']
            except Exception as e:
                logger.error(f"AI.GENERATE_BOOL failed: {e}")
                results['ai_generate_bool'] = {'error': str(e)}

            # Run AI.FORECAST
            try:
                forecast_results = self.ai_forecast_outcome(limit=limit)
                results['ai_forecast'] = forecast_results
                results['functions_executed'].append('AI.FORECAST')
                results['total_documents_processed'] += forecast_results['total_documents']
            except Exception as e:
                logger.error(f"AI.FORECAST failed: {e}")
                results['ai_forecast'] = {'error': str(e)}

            logger.info(f"Completed Track 1 functions. Executed: {len(results['functions_executed'])}")

            return results

        except Exception as e:
            logger.error(f"Track 1 functions execution failed: {e}")
            raise
