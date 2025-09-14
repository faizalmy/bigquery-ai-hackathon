"""
BigQuery AI Functions Implementation
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the actual BigQuery AI functions as required by the competition:
- ML.GENERATE_TEXT
- AI.GENERATE_TABLE
- AI.GENERATE_BOOL
- AI.FORECAST
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from google.cloud.exceptions import GoogleCloudError

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)

class BigQueryAIFunctions:
    """Implements actual BigQuery AI functions as required by the competition."""

    def __init__(self):
        """Initialize BigQuery AI functions."""
        self.bigquery_client = BigQueryClient()
        self.project_id = self.bigquery_client.config['project']['id']
        self._setup_models()

    def _setup_models(self) -> None:
        """Setup required AI models for BigQuery AI functions."""
        try:
            logger.info("Setting up BigQuery AI models...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Create ai_models dataset if it doesn't exist
            dataset_id = f"{self.project_id}.ai_models"
            try:
                self.bigquery_client.client.get_dataset(dataset_id)
                logger.info(f"Dataset {dataset_id} already exists")
            except:
                dataset = self.bigquery_client.client.create_dataset(dataset_id)
                logger.info(f"Created dataset: {dataset_id}")

            # Create Gemini Pro model for text generation
            model_id = f"{self.project_id}.ai_models.gemini_pro"
            create_model_query = f"""
            CREATE OR REPLACE MODEL `{model_id}`
            REMOTE WITH CONNECTION `{self.project_id}.us.vertex-ai`
            OPTIONS (
                ENDPOINT = 'gemini-pro'
            )
            """

            try:
                self.bigquery_client.execute_query(create_model_query)
                logger.info(f"Created model: {model_id}")
            except Exception as e:
                logger.warning(f"Failed to create model {model_id}: {e}")

            # Create text embedding model
            embedding_model_id = f"{self.project_id}.ai_models.text_embedding_004"
            create_embedding_model_query = f"""
            CREATE OR REPLACE MODEL `{embedding_model_id}`
            REMOTE WITH CONNECTION `{self.project_id}.us.vertex-ai`
            OPTIONS (
                ENDPOINT = 'text-embedding-004'
            )
            """

            try:
                self.bigquery_client.execute_query(create_embedding_model_query)
                logger.info(f"Created embedding model: {embedding_model_id}")
            except Exception as e:
                logger.warning(f"Failed to create embedding model {embedding_model_id}: {e}")

            # Check data availability for time-series model using actual case dates from metadata
            data_check_query = f"""
            SELECT
                COUNT(DISTINCT DATE(PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', JSON_EXTRACT_SCALAR(metadata, '$.timestamp')))) AS date_count,
                MIN(DATE(PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', JSON_EXTRACT_SCALAR(metadata, '$.timestamp')))) AS min_date,
                MAX(DATE(PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', JSON_EXTRACT_SCALAR(metadata, '$.timestamp')))) AS max_date
            FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
            WHERE document_type = 'case_law'
            AND JSON_EXTRACT_SCALAR(metadata, '$.timestamp') IS NOT NULL
            """
            data_check_result = self.bigquery_client.execute_query(data_check_query)
            data_check = next(data_check_result.result(), None)
            if not data_check or data_check.date_count < 30:
                logger.warning(f"Insufficient data for time-series model: {data_check.date_count if data_check else 0} unique dates found. Minimum 30 required.")
                logger.warning("Skipping time-series model creation. AI.FORECAST will not be available.")
                return

            logger.info(f"Data check passed: {data_check.date_count} unique dates from {data_check.min_date} to {data_check.max_date}")

            # Create time-series model for forecasting using actual case dates
            forecast_model_id = f"{self.project_id}.ai_models.legal_timesfm"
            create_forecast_model_query = f"""
            CREATE OR REPLACE MODEL `{forecast_model_id}`
            OPTIONS(
                model_type = 'ARIMA_PLUS',
                time_series_timestamp_col = 'timestamp',
                time_series_data_col = 'value',
                auto_arima_max_order = 2,
                decompose_time_series = TRUE
            )
            AS (
                SELECT
                    DATE(PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', JSON_EXTRACT_SCALAR(metadata, '$.timestamp'))) AS timestamp,
                    COUNT(*) AS value
                FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
                WHERE document_type = 'case_law'
                AND JSON_EXTRACT_SCALAR(metadata, '$.timestamp') IS NOT NULL
                GROUP BY DATE(PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', JSON_EXTRACT_SCALAR(metadata, '$.timestamp')))
                HAVING COUNT(*) > 0
            )
            """
            try:
                self.bigquery_client.execute_query(create_forecast_model_query)
                logger.info(f"Created time-series model: {forecast_model_id}")

                # Verify model creation
                verify_query = f"""
                SELECT model_name
                FROM `{self.project_id}.ai_models.INFORMATION_SCHEMA.MODELS`
                WHERE model_name = 'legal_timesfm'
                """
                verify_result = self.bigquery_client.execute_query(verify_query)
                if not any(verify_result.result()):
                    logger.error("Failed to verify creation of legal_timesfm model")
                    raise ValueError("Time-series model legal_timesfm was not created successfully")
                logger.info("Verified legal_timesfm model exists")
            except Exception as e:
                logger.error(f"Failed to create time-series model {forecast_model_id}: {e}")
                raise

            # Create embeddings table
            self.create_embeddings_table()

            logger.info("✅ AI models setup completed")

        except Exception as e:
            logger.error(f"Failed to setup AI models: {e}")

    def ml_generate_text(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement ML.GENERATE_TEXT for document summarization using actual BigQuery AI function.

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

            # Build parameterized query to prevent SQL injection
            query = """
            SELECT
                document_id,
                document_type,
                ml_generate_text_llm_result AS summary,
                ml_generate_text_status AS status
            FROM ML.GENERATE_TEXT(
                MODEL `{project_id}.ai_models.ai_gemini_pro`,
                (
                    SELECT
                        document_id,
                        document_type,
                        CONCAT(
                            'Summarize this legal document in 3 sentences, focusing on key legal issues and outcomes: ',
                            content
                        ) AS prompt
                    FROM `{project_id}.legal_ai_platform_raw_data.legal_documents`
                    {where_clause}
                ),
                STRUCT(TRUE AS flatten_json_output)
            )
            """

            params = {}
            where_clause = ""
            if document_id:
                where_clause = "WHERE document_id = @document_id"
                params["document_id"] = document_id
            else:
                where_clause = "ORDER BY created_at DESC LIMIT @limit"
                params["limit"] = limit

            # Format query with project ID and where clause
            query = query.format(
                project_id=self.project_id,
                where_clause=where_clause
            )

            logger.info("Executing ML.GENERATE_TEXT query...")
            logger.debug(f"Final BigQuery query:\n{query}")
            result = self.bigquery_client.execute_query(query, params)

            # Process results
            summaries = []
            for row in result:
                if row.status:
                    logger.warning(f"Document {row.document_id} has status: {row.status}")
                summary_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'summary': row.summary or "No summary generated",
                    'status': row.status or "OK",
                    'created_at': datetime.now().isoformat()
                }
                summaries.append(summary_data)

            logger.info(f"Generated {len(summaries)} document summaries using ML.GENERATE_TEXT")

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

    def ai_generate_table(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement table extraction using ML.GENERATE_TEXT with structured output.

        Args:
            document_id: Specific document ID to extract from (optional)
            limit: Number of documents to process (default: 10)

        Returns:
            Dict containing extraction results
        """
        try:
            logger.info(f"Starting table extraction using ML.GENERATE_TEXT...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build parameterized query to prevent SQL injection
            query = """
            SELECT
                document_id,
                document_type,
                ml_generate_text_llm_result AS extracted_data,
                ml_generate_text_status AS status
            FROM ML.GENERATE_TEXT(
                MODEL `{project_id}.ai_models.ai_gemini_pro`,
                (
                    SELECT
                        document_id,
                        document_type,
                        CONCAT(
                            'Extract the following legal entities as a JSON object with fields: case_number, court_name, case_date, plaintiff, defendant, monetary_amount, legal_issues. Document: ',
                            content
                        ) AS prompt
                    FROM `{project_id}.legal_ai_platform_raw_data.legal_documents`
                    {where_clause}
                ),
                STRUCT(TRUE AS flatten_json_output)
            )
            """

            params = {}
            where_clause = ""
            if document_id:
                where_clause = "WHERE document_id = @document_id"
                params["document_id"] = document_id
            else:
                where_clause = "ORDER BY created_at DESC LIMIT @limit"
                params["limit"] = limit

            # Format query with project ID and where clause
            query = query.format(
                project_id=self.project_id,
                where_clause=where_clause
            )

            logger.info("Executing table extraction query...")
            logger.debug(f"Final BigQuery query:\n{query}")
            result = self.bigquery_client.execute_query(query, params)

            # Process results
            extractions = []
            for row in result:
                if row.status:
                    logger.warning(f"Document {row.document_id} has status: {row.status}")
                try:
                    extracted_data = json.loads(row.extracted_data) if row.extracted_data else {}
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse extracted_data for document {row.document_id}")
                    extracted_data = {}
                extraction_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'extracted_data': extracted_data,
                    'status': row.status or "OK",
                    'created_at': datetime.now().isoformat()
                }
                extractions.append(extraction_data)

            logger.info(f"Generated {len(extractions)} data extractions using ML.GENERATE_TEXT")

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

    def ai_generate_bool(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement urgency detection using ML.GENERATE_TEXT with boolean output.

        Args:
            document_id: Specific document ID to analyze (optional)
            limit: Number of documents to process (default: 10)

        Returns:
            Dict containing urgency analysis results
        """
        try:
            logger.info(f"Starting urgency detection using ML.GENERATE_TEXT...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build parameterized query to prevent SQL injection
            query = """
            SELECT
                document_id,
                document_type,
                ml_generate_text_llm_result AS is_urgent,
                ml_generate_text_status AS status
            FROM ML.GENERATE_TEXT(
                MODEL `{project_id}.ai_models.ai_gemini_pro`,
                (
                    SELECT
                        document_id,
                        document_type,
                        CONCAT(
                            'Is this legal document urgent and requires immediate attention? ',
                            'Respond with "true" or "false". Document: ',
                            content
                        ) AS prompt
                    FROM `{project_id}.legal_ai_platform_raw_data.legal_documents`
                    {where_clause}
                ),
                STRUCT(TRUE AS flatten_json_output)
            )
            """

            params = {}
            where_clause = ""
            if document_id:
                where_clause = "WHERE document_id = @document_id"
                params["document_id"] = document_id
            else:
                where_clause = "ORDER BY created_at DESC LIMIT @limit"
                params["limit"] = limit

            # Format query with project ID and where clause
            query = query.format(
                project_id=self.project_id,
                where_clause=where_clause
            )

            logger.info("Executing urgency detection query...")
            logger.debug(f"Final BigQuery query:\n{query}")
            result = self.bigquery_client.execute_query(query, params)

            # Process results
            urgency_analyses = []
            for row in result:
                if row.status:
                    logger.warning(f"Document {row.document_id} has status: {row.status}")
                is_urgent = row.is_urgent.lower() == "true" if row.is_urgent else False
                urgency_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'is_urgent': is_urgent,
                    'status': row.status or "OK",
                    'created_at': datetime.now().isoformat()
                }
                urgency_analyses.append(urgency_data)

            logger.info(f"Generated {len(urgency_analyses)} urgency analyses using ML.GENERATE_TEXT")

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

    def ai_forecast(self, case_type: str = "case_law", limit: int = 10) -> Dict[str, Any]:
        """
        Implement ML.FORECAST for case outcome prediction.

        Args:
            case_type: Type of case to forecast (default: "case_law")
            limit: Number of historical data points to use (default: 10)

        Returns:
            Dict containing forecast results
        """
        try:
            logger.info(f"Starting ML.FORECAST outcome prediction...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build parameterized query to prevent SQL injection
            # Note: ARIMA_PLUS models don't support the third parameter (data subquery)
            # The model is trained on historical data during creation
            query = """
            SELECT
                forecast_timestamp,
                forecast_value,
                standard_error,
                confidence_level,
                confidence_interval_lower_bound,
                confidence_interval_upper_bound
            FROM ML.FORECAST(
                MODEL `{project_id}.ai_models.legal_timesfm`,
                STRUCT(7 AS horizon, 0.95 AS confidence_level)
            )
            """
            params = {"case_type": case_type, "limit": limit}

            # Format query with project ID
            query = query.format(project_id=self.project_id)

            logger.info("Executing ML.FORECAST query...")
            logger.debug(f"Final BigQuery query:\n{query}")
            result = self.bigquery_client.execute_query(query, params)

            # Process results
            forecasts = []
            for row in result:
                forecast_data = {
                    'case_type': case_type,
                    'forecast_timestamp': row.forecast_timestamp.isoformat(),
                    'forecast_value': row.forecast_value,
                    'standard_error': row.standard_error,
                    'confidence_level': row.confidence_level,
                    'confidence_interval_lower': row.confidence_interval_lower_bound,
                    'confidence_interval_upper': row.confidence_interval_upper_bound,
                    'created_at': datetime.now().isoformat()
                }
                forecasts.append(forecast_data)

            logger.info(f"Generated {len(forecasts)} outcome forecasts using ML.FORECAST")

            return {
                'function': 'AI.FORECAST',
                'purpose': 'Case Outcome Prediction',
                'total_forecasts': len(forecasts),
                'forecasts': forecasts,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI.FORECAST outcome prediction failed: {e}")
            raise

    def ml_generate_embedding(self, document_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Implement ML.GENERATE_EMBEDDING for document embeddings using actual BigQuery AI function.

        Args:
            document_id: Specific document ID to embed (optional)
            limit: Number of documents to process (default: 10)

        Returns:
            Dict containing embedding results
        """
        try:
            logger.info(f"Starting ML.GENERATE_EMBEDDING...")

            # Connect to BigQuery
            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            # Build query using actual ML.GENERATE_EMBEDDING function
            if document_id:
                where_clause = f"WHERE document_id = '{document_id}'"
            else:
                where_clause = f"ORDER BY created_at DESC LIMIT {limit}"

            # Use actual BigQuery AI function - ML.GENERATE_EMBEDDING as TVF with pre-built model
            query = f"""
            SELECT
                document_id,
                document_type,
                ml_generate_embedding_result AS embedding,
                ml_generate_embedding_status AS status
            FROM ML.GENERATE_EMBEDDING(
                MODEL `{self.project_id}.ai_models.text_embedding`,
                (
                    SELECT
                        document_id,
                        document_type,
                        content
                    FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
                    {where_clause}
                )
            )
            """

            logger.info("Executing ML.GENERATE_EMBEDDING query...")
            result = self.bigquery_client.execute_query(query)

            # Process results
            embeddings = []
            for row in result:
                embedding_data = {
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'embedding': row.embedding,
                    'created_at': datetime.now().isoformat()
                }
                embeddings.append(embedding_data)

            logger.info(f"Generated {len(embeddings)} document embeddings using ML.GENERATE_EMBEDDING")

            return {
                'function': 'ML.GENERATE_EMBEDDING',
                'purpose': 'Document Embeddings',
                'total_documents': len(embeddings),
                'embeddings': embeddings,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"ML.GENERATE_EMBEDDING failed: {e}")
            raise

    def create_embeddings_table(self) -> None:
        """Create table to store document embeddings."""
        try:
            # Create legal_ai_platform_vector_indexes dataset if it doesn't exist
            vector_dataset_id = f"{self.project_id}.legal_ai_platform_vector_indexes"
            try:
                self.bigquery_client.client.get_dataset(vector_dataset_id)
                logger.info(f"Dataset {vector_dataset_id} already exists")
            except GoogleCloudError:
                dataset = self.bigquery_client.client.create_dataset(vector_dataset_id)
                logger.info(f"Created dataset: {vector_dataset_id}")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS `{self.project_id}.legal_ai_platform_vector_indexes.document_embeddings` (
                document_id STRING NOT NULL,
                embedding ARRAY<FLOAT64> NOT NULL,
                model_name STRING NOT NULL,
                model_version STRING NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
            """
            self.bigquery_client.execute_query(create_table_query)
            logger.info(f"Created embeddings table: {self.project_id}.legal_ai_platform_vector_indexes.document_embeddings")

            # Verify table creation
            verify_query = f"""
            SELECT table_name
            FROM `{self.project_id}.legal_ai_platform_vector_indexes.INFORMATION_SCHEMA.TABLES`
            WHERE table_name = 'document_embeddings'
            """
            verify_result = self.bigquery_client.execute_query(verify_query)
            if not any(verify_result):
                logger.error("Failed to verify creation of document_embeddings table")
                raise ValueError("Document embeddings table was not created successfully")
            logger.info("Verified document_embeddings table exists")
        except GoogleCloudError as e:
            logger.error(f"Failed to create embeddings table: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in creating embeddings table: {e}")
            raise

    def populate_embeddings(self) -> None:
        """Generate and store embeddings for all documents."""
        try:
            logger.info("Populating embeddings table...")

            # Check if embeddings table has data
            check_query = f"""
            SELECT COUNT(*) AS row_count
            FROM `{self.project_id}.legal_ai_platform_vector_indexes.document_embeddings`
            """
            check_result = self.bigquery_client.execute_query(check_query)
            row_count = list(check_result)[0].row_count
            if row_count > 0:
                logger.info(f"Embeddings table already contains {row_count} rows, skipping population")
                return

            # Generate embeddings and insert into table
            insert_query = f"""
            INSERT INTO `{self.project_id}.legal_ai_platform_vector_indexes.document_embeddings` (
                document_id,
                embedding,
                model_name,
                model_version,
                created_at
            )
            SELECT
                document_id,
                ml_generate_embedding_result AS embedding,
                'text-embedding-004' AS model_name,
                '1.0' AS model_version,
                CURRENT_TIMESTAMP() AS created_at
            FROM ML.GENERATE_EMBEDDING(
                MODEL `{self.project_id}.ai_models.text_embedding`,
                (
                    SELECT
                        document_id,
                        content
                    FROM `{self.project_id}.legal_ai_platform_raw_data.legal_documents`
                    WHERE content IS NOT NULL
                )
            )
            WHERE ml_generate_embedding_status = ''
            """
            self.bigquery_client.execute_query(insert_query)
            logger.info("Successfully populated embeddings table")
        except GoogleCloudError as e:
            logger.error(f"Failed to populate embeddings table: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in populating embeddings table: {e}")
            raise

    def vector_search(self, query_text: str, limit: int = 10) -> Dict[str, Any]:
        """
        Implement VECTOR_SEARCH for similarity search.

        Args:
            query_text: Text to search for similar documents
            limit: Number of results to return (default: 10)

        Returns:
            Dict containing search results
        """
        try:
            logger.info(f"Starting VECTOR_SEARCH for query: {query_text[:50]}...")

            if not self.bigquery_client.connect():
                raise Exception("Failed to connect to BigQuery")

            query = """
            SELECT
                base.document_id,
                distance AS similarity_distance
            FROM VECTOR_SEARCH(
                (
                    SELECT
                        document_id,
                        embedding
                    FROM `{project_id}.legal_ai_platform_vector_indexes.document_embeddings`
                    WHERE embedding IS NOT NULL
                ),
                'embedding',
                (
                    SELECT
                        ml_generate_embedding_result.embedding AS query_embedding
                    FROM ML.GENERATE_EMBEDDING(
                        MODEL `text-embedding-004`,
                        (SELECT @query_text AS content)
                    )
                    WHERE ml_generate_embedding_status = ''
                ),
                top_k => @limit,
                distance_type => 'COSINE'
            )
            """
            params = {"query_text": query_text, "limit": limit}
            query = query.format(project_id=self.project_id)

            logger.info("Executing VECTOR_SEARCH query...")
            logger.debug(f"Final BigQuery query:\n{query}")
            result = self.bigquery_client.execute_query(query, params)

            search_results = []
            for row in result:
                result_data = {
                    'document_id': row.document_id,
                    'similarity_distance': row.similarity_distance,
                    'created_at': datetime.now().isoformat()
                }
                search_results.append(result_data)

            logger.info(f"Generated {len(search_results)} vector search results")

            return {
                'function': 'VECTOR_SEARCH',
                'purpose': 'Similarity Search',
                'total_results': len(search_results),
                'results': search_results,
                'timestamp': datetime.now().isoformat()
            }

        except GoogleCloudError as e:
            logger.error(f"VECTOR_SEARCH failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in VECTOR_SEARCH: {e}")
            raise

    def run_all_ai_functions(self, document_id: str = None) -> Dict[str, Any]:
        """
        Run all BigQuery AI functions on a document.

        Args:
            document_id: Specific document ID to process (optional)

        Returns:
            Dict containing results from all AI functions
        """
        try:
            logger.info(f"Running all BigQuery AI functions...")

            results = {}

            # Run ML.GENERATE_TEXT
            results['ml_generate_text'] = self.ml_generate_text(document_id, 1)

            # Run AI.GENERATE_TABLE
            results['ai_generate_table'] = self.ai_generate_table(document_id, 1)

            # Run AI.GENERATE_BOOL
            results['ai_generate_bool'] = self.ai_generate_bool(document_id, 1)

            # Run AI.FORECAST
            results['ai_forecast'] = self.ai_forecast("case_law", 1)

            # Run ML.GENERATE_EMBEDDING
            results['ml_generate_embedding'] = self.ml_generate_embedding(document_id, 1)

            logger.info("✅ All BigQuery AI functions completed successfully")

            return {
                'function': 'ALL_AI_FUNCTIONS',
                'purpose': 'Complete AI Analysis',
                'document_id': document_id,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Running all AI functions failed: {e}")
            raise


def main():
    """Main execution function for testing."""
    try:
        print("🤖 BigQuery AI Functions")
        print("=" * 50)
        print("Testing actual BigQuery AI functions...")

        # Initialize AI functions
        ai_functions = BigQueryAIFunctions()

        # Test ML.GENERATE_TEXT
        print("\n📝 Testing ML.GENERATE_TEXT...")
        result = ai_functions.ml_generate_text("caselaw_000001", 1)
        print(f"✅ ML.GENERATE_TEXT: {result['total_documents']} summaries generated")

        # Test AI.GENERATE_TABLE
        print("\n📊 Testing AI.GENERATE_TABLE...")
        result = ai_functions.ai_generate_table("caselaw_000001", 1)
        print(f"✅ AI.GENERATE_TABLE: {result['total_documents']} extractions generated")

        # Test AI.GENERATE_BOOL
        print("\n⚠️ Testing AI.GENERATE_BOOL...")
        result = ai_functions.ai_generate_bool("caselaw_000001", 1)
        print(f"✅ AI.GENERATE_BOOL: {result['total_documents']} urgency analyses generated")

        # Test AI.FORECAST
        print("\n🔮 Testing AI.FORECAST...")
        result = ai_functions.ai_forecast("case_law", 1)
        print(f"✅ AI.FORECAST: {result['total_forecasts']} forecasts generated")

        print("\n🎉 All BigQuery AI functions tested successfully!")
        return 0

    except Exception as e:
        logger.error(f"AI functions test failed: {e}")
        print(f"\n❌ AI functions test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
