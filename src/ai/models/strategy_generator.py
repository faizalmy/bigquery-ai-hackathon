"""
Strategy Generation Model
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the legal strategy generation model using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyGenerator:
    """Legal strategy generation model using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "strategy_generator"):
        """
        Initialize the strategy generator model.

        Args:
            project_id: BigQuery project ID
            model_name: Name of the BigQuery ML model
        """
        self.project_id = project_id
        self.model_name = model_name
        self.model_path = f"{project_id}.ai_models.{model_name}"
        self.strategy_types = ['litigation', 'settlement', 'compliance', 'preventive', 'defensive']
        self.is_trained = False

    def create_model(self, bq_client) -> bool:
        """
        Create the strategy generator model in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating strategy generator model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Strategy generator model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating strategy generator model: {e}")
            return False

    def generate_strategy(self, bq_client, case_data: Dict[str, Any], strategy_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate legal strategy recommendations for a case.

        Args:
            bq_client: BigQuery client instance
            case_data: Case information including facts, legal issues, parties, etc.
            strategy_type: Optional specific strategy type to focus on

        Returns:
            Strategy generation dictionary
        """
        try:
            # Create a temporary table with the case data
            temp_table = f"{self.project_id}.temp.strategy_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare case context
            case_context = f"""
            Case Facts: {case_data.get('facts', '')}
            Legal Issues: {case_data.get('legal_issues', '')}
            Parties: {case_data.get('parties', '')}
            Court: {case_data.get('court', '')}
            Jurisdiction: {case_data.get('jurisdiction', '')}
            Case Type: {case_data.get('case_type', '')}
            Client Goals: {case_data.get('client_goals', '')}
            Budget Constraints: {case_data.get('budget_constraints', '')}
            Timeline: {case_data.get('timeline', '')}
            """

            # Insert case data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{case_context}' as case_info
            """

            bq_client.client.query(insert_query).result()

            # Prepare strategy generation prompt
            strategy_prompt = f"""
            Generate comprehensive legal strategy recommendations for this case. Consider: case facts, legal issues, client goals, budget constraints, and timeline. Return: recommended_strategy (primary strategy approach), alternative_strategies (backup options), key_actions (specific steps to take), timeline (recommended timeline), resource_requirements (staff, budget, time), risk_mitigation (strategies to minimize risks), success_metrics (how to measure success), and contingency_plans (what to do if strategy fails). Case: {case_context}
            """

            if strategy_type:
                strategy_prompt += f" Focus on {strategy_type} strategy approach."

            # Use the model to generate strategy
            strategy_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('{strategy_prompt}')
            ) as strategy_recommendations
            FROM `{temp_table}`
            """

            result = bq_client.client.query(strategy_query).result()
            strategy_recommendations = list(result)[0].strategy_recommendations

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'strategy_recommendations': strategy_recommendations,
                'generation_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'case_id': case_data.get('case_id', ''),
                'strategy_type_requested': strategy_type,
                'available_strategy_types': self.strategy_types
            }

        except Exception as e:
            logger.error(f"Error generating strategy: {e}")
            return {
                'error': str(e),
                'generation_timestamp': datetime.now().isoformat()
            }

    def generate_litigation_strategy(self, bq_client, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate litigation-specific strategy recommendations.

        Args:
            bq_client: BigQuery client instance
            case_data: Case information

        Returns:
            Litigation strategy recommendations
        """
        try:
            # Create a temporary table with the case data
            temp_table = f"{self.project_id}.temp.litigation_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare case context
            case_context = f"""
            Case Facts: {case_data.get('facts', '')}
            Legal Issues: {case_data.get('legal_issues', '')}
            Evidence: {case_data.get('evidence', '')}
            Witnesses: {case_data.get('witnesses', '')}
            Court: {case_data.get('court', '')}
            Judge: {case_data.get('judge', '')}
            Opposing Counsel: {case_data.get('opposing_counsel', '')}
            """

            # Insert case data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{case_context}' as case_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to generate litigation strategy
            litigation_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Generate detailed litigation strategy for this case. Consider: case facts, evidence, witnesses, court dynamics, and opposing counsel. Return: litigation_approach (overall approach), discovery_strategy (evidence gathering plan), motion_strategy (key motions to file), trial_strategy (trial preparation and execution), witness_strategy (witness preparation and examination), settlement_leverage (negotiation positioning), and timeline (litigation timeline with key milestones). Case: ', case_info)
            ) as litigation_strategy
            FROM `{temp_table}`
            """

            result = bq_client.client.query(litigation_query).result()
            litigation_strategy = list(result)[0].litigation_strategy

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'litigation_strategy': litigation_strategy,
                'generation_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'case_id': case_data.get('case_id', '')
            }

        except Exception as e:
            logger.error(f"Error generating litigation strategy: {e}")
            return {
                'error': str(e),
                'generation_timestamp': datetime.now().isoformat()
            }

    def generate_settlement_strategy(self, bq_client, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate settlement strategy recommendations.

        Args:
            bq_client: BigQuery client instance
            case_data: Case information

        Returns:
            Settlement strategy recommendations
        """
        try:
            # Create a temporary table with the case data
            temp_table = f"{self.project_id}.temp.settlement_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare case context
            case_context = f"""
            Case Facts: {case_data.get('facts', '')}
            Legal Issues: {case_data.get('legal_issues', '')}
            Potential Damages: {case_data.get('damages', '')}
            Settlement History: {case_data.get('settlement_history', '')}
            Client Goals: {case_data.get('client_goals', '')}
            Budget Constraints: {case_data.get('budget_constraints', '')}
            """

            # Insert case data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{case_context}' as case_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to generate settlement strategy
            settlement_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Generate comprehensive settlement strategy for this case. Consider: case strength, potential damages, client goals, and budget constraints. Return: settlement_approach (overall settlement strategy), negotiation_tactics (specific negotiation techniques), settlement_range (acceptable settlement amounts), timing_strategy (when to negotiate), leverage_points (key negotiation advantages), risk_assessment (settlement vs. litigation risks), and implementation_plan (steps to execute settlement). Case: ', case_info)
            ) as settlement_strategy
            FROM `{temp_table}`
            """

            result = bq_client.client.query(settlement_query).result()
            settlement_strategy = list(result)[0].settlement_strategy

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'settlement_strategy': settlement_strategy,
                'generation_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'case_id': case_data.get('case_id', '')
            }

        except Exception as e:
            logger.error(f"Error generating settlement strategy: {e}")
            return {
                'error': str(e),
                'generation_timestamp': datetime.now().isoformat()
            }

    def batch_generate_strategies(self, bq_client, cases: List[Dict[str, Any]], strategy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate strategies for multiple cases.

        Args:
            bq_client: BigQuery client instance
            cases: List of case data dictionaries
            strategy_type: Optional specific strategy type to focus on

        Returns:
            List of strategy recommendations
        """
        results = []

        for case in cases:
            try:
                strategy = self.generate_strategy(bq_client, case, strategy_type)
                strategy['case_id'] = case.get('case_id', '')
                results.append(strategy)
            except Exception as e:
                logger.error(f"Error generating strategy for case {case.get('case_id', 'unknown')}: {e}")
                results.append({
                    'case_id': case.get('case_id', ''),
                    'error': str(e),
                    'generation_timestamp': datetime.now().isoformat()
                })

        return results

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the strategy generator model.

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
                'strategy_types': self.strategy_types
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

def main():
    """Test the strategy generator model."""
    print("🎯 Strategy Generation Model")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Strategy generator model class created successfully")

if __name__ == "__main__":
    main()
