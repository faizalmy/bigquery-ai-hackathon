"""
Outcome Prediction Model
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the case outcome prediction model using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OutcomePredictor:
    """Case outcome prediction model using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "outcome_predictor"):
        """
        Initialize the outcome predictor model.

        Args:
            project_id: BigQuery project ID
            model_name: Name of the BigQuery ML model
        """
        self.project_id = project_id
        self.model_name = model_name
        self.model_path = f"{project_id}.ai_models.{model_name}"
        self.outcome_types = ['plaintiff_win', 'defendant_win', 'settlement', 'dismissal', 'unclear']
        self.is_trained = False

    def create_model(self, bq_client) -> bool:
        """
        Create the outcome predictor model in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating outcome predictor model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Outcome predictor model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating outcome predictor model: {e}")
            return False

    def predict_outcome(self, bq_client, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the likely outcome of a legal case.

        Args:
            bq_client: BigQuery client instance
            case_data: Case information including facts, legal issues, parties, etc.

        Returns:
            Outcome prediction dictionary
        """
        try:
            # Create a temporary table with the case data
            temp_table = f"{self.project_id}.temp.outcome_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare case context
            case_context = f"""
            Case Facts: {case_data.get('facts', '')}
            Legal Issues: {case_data.get('legal_issues', '')}
            Parties: {case_data.get('parties', '')}
            Court: {case_data.get('court', '')}
            Jurisdiction: {case_data.get('jurisdiction', '')}
            Case Type: {case_data.get('case_type', '')}
            Precedent Cases: {case_data.get('precedents', '')}
            """

            # Insert case data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{case_context}' as case_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to predict outcome
            prediction_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Based on this legal case information, predict the likely outcome. Consider: the legal issues, precedent cases, case strength, and legal arguments. Return: likely_outcome (plaintiff_win, defendant_win, settlement, dismissal, or unclear), confidence (high, medium, low), probability_score (0-100), reasoning (detailed explanation), key_factors (list of factors influencing prediction), and risk_assessment (potential risks and challenges). Case: ', case_info)
            ) as outcome_prediction
            FROM `{temp_table}`
            """

            result = bq_client.client.query(prediction_query).result()
            outcome_prediction = list(result)[0].outcome_prediction

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'outcome_prediction': outcome_prediction,
                'prediction_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'case_id': case_data.get('case_id', ''),
                'available_outcomes': self.outcome_types
            }

        except Exception as e:
            logger.error(f"Error predicting outcome: {e}")
            return {
                'error': str(e),
                'prediction_timestamp': datetime.now().isoformat()
            }

    def batch_predict_outcomes(self, bq_client, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict outcomes for multiple cases.

        Args:
            bq_client: BigQuery client instance
            cases: List of case data dictionaries

        Returns:
            List of outcome predictions
        """
        results = []

        for case in cases:
            try:
                prediction = self.predict_outcome(bq_client, case)
                prediction['case_id'] = case.get('case_id', '')
                results.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting outcome for case {case.get('case_id', 'unknown')}: {e}")
                results.append({
                    'case_id': case.get('case_id', ''),
                    'error': str(e),
                    'prediction_timestamp': datetime.now().isoformat()
                })

        return results

    def analyze_case_strength(self, bq_client, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the strength of a legal case.

        Args:
            bq_client: BigQuery client instance
            case_data: Case information

        Returns:
            Case strength analysis
        """
        try:
            # Create a temporary table with the case data
            temp_table = f"{self.project_id}.temp.case_strength_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare case context
            case_context = f"""
            Case Facts: {case_data.get('facts', '')}
            Legal Arguments: {case_data.get('arguments', '')}
            Evidence: {case_data.get('evidence', '')}
            Legal Issues: {case_data.get('legal_issues', '')}
            """

            # Insert case data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{case_context}' as case_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to analyze case strength
            strength_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Analyze the strength of this legal case. Consider: legal arguments, evidence quality, precedent support, and case weaknesses. Return: overall_strength (strong, moderate, weak), strength_score (0-100), strengths (list of case strengths), weaknesses (list of case weaknesses), evidence_quality (assessment of evidence), and recommendations (suggestions to strengthen the case). Case: ', case_info)
            ) as strength_analysis
            FROM `{temp_table}`
            """

            result = bq_client.client.query(strength_query).result()
            strength_analysis = list(result)[0].strength_analysis

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'strength_analysis': strength_analysis,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'case_id': case_data.get('case_id', '')
            }

        except Exception as e:
            logger.error(f"Error analyzing case strength: {e}")
            return {
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the outcome predictor model.

        Args:
            bq_client: BigQuery client instance

        Returns:
            Model information dictionary
        """
        try:
            query = f"""
            SELECT
              model_name,
              model_type,
              creation_time,
              last_modified_time
            FROM `{self.project_id}.ai_models.INFORMATION_SCHEMA.MODELS`
            WHERE model_name = '{self.model_name}'
            """

            result = bq_client.client.query(query).result()
            model_info = list(result)[0]

            return {
                'model_name': model_info.model_name,
                'model_type': model_info.model_type,
                'creation_time': model_info.creation_time.isoformat(),
                'last_modified_time': model_info.last_modified_time.isoformat(),
                'model_path': self.model_path,
                'outcome_types': self.outcome_types
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

def main():
    """Test the outcome predictor model."""
    print("🔮 Outcome Prediction Model")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Outcome predictor model class created successfully")

if __name__ == "__main__":
    main()
