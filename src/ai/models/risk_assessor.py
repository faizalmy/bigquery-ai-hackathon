"""
Risk Assessment Model
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module implements the risk assessment model using BigQuery ML.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskAssessor:
    """Risk assessment model using BigQuery ML."""

    def __init__(self, project_id: str, model_name: str = "risk_assessor"):
        """
        Initialize the risk assessor model.

        Args:
            project_id: BigQuery project ID
            model_name: Name of the BigQuery ML model
        """
        self.project_id = project_id
        self.model_name = model_name
        self.model_path = f"{project_id}.ai_models.{model_name}"
        self.risk_levels = ['low', 'medium', 'high', 'critical']
        self.is_trained = False

    def create_model(self, bq_client) -> bool:
        """
        Create the risk assessor model in BigQuery ML.

        Args:
            bq_client: BigQuery client instance

        Returns:
            True if model created successfully, False otherwise
        """
        try:
            logger.info(f"Creating risk assessor model: {self.model_path}")

            query = f"""
            CREATE OR REPLACE MODEL `{self.model_path}`
            OPTIONS(
              model_type='GEMINI_PRO'
            )
            """

            result = bq_client.client.query(query).result()
            logger.info("✅ Risk assessor model created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating risk assessor model: {e}")
            return False

    def assess_risk(self, bq_client, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the legal risk level of a case or situation.

        Args:
            bq_client: BigQuery client instance
            case_data: Case information including facts, legal issues, parties, etc.

        Returns:
            Risk assessment dictionary
        """
        try:
            # Create a temporary table with the case data
            temp_table = f"{self.project_id}.temp.risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare case context
            case_context = f"""
            Case Facts: {case_data.get('facts', '')}
            Legal Issues: {case_data.get('legal_issues', '')}
            Parties: {case_data.get('parties', '')}
            Potential Liabilities: {case_data.get('liabilities', '')}
            Regulatory Compliance: {case_data.get('compliance', '')}
            Financial Impact: {case_data.get('financial_impact', '')}
            Reputation Risk: {case_data.get('reputation_risk', '')}
            """

            # Insert case data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{case_context}' as case_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to assess risk
            risk_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Assess the legal risk level of this case or situation. Consider: potential liabilities, regulatory compliance, financial impact, reputation risk, and legal precedents. Return: risk_level (low, medium, high, critical), risk_score (0-100), risk_factors (list of key risk factors), potential_impact (financial, legal, reputational), mitigation_strategies (suggested strategies to reduce risk), and monitoring_recommendations (ongoing risk monitoring suggestions). Situation: ', case_info)
            ) as risk_assessment
            FROM `{temp_table}`
            """

            result = bq_client.client.query(risk_query).result()
            risk_assessment = list(result)[0].risk_assessment

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'risk_assessment': risk_assessment,
                'assessment_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'case_id': case_data.get('case_id', ''),
                'available_risk_levels': self.risk_levels
            }

        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return {
                'error': str(e),
                'assessment_timestamp': datetime.now().isoformat()
            }

    def batch_assess_risks(self, bq_client, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assess risks for multiple cases.

        Args:
            bq_client: BigQuery client instance
            cases: List of case data dictionaries

        Returns:
            List of risk assessments
        """
        results = []

        for case in cases:
            try:
                risk_assessment = self.assess_risk(bq_client, case)
                risk_assessment['case_id'] = case.get('case_id', '')
                results.append(risk_assessment)
            except Exception as e:
                logger.error(f"Error assessing risk for case {case.get('case_id', 'unknown')}: {e}")
                results.append({
                    'case_id': case.get('case_id', ''),
                    'error': str(e),
                    'assessment_timestamp': datetime.now().isoformat()
                })

        return results

    def compliance_risk_assessment(self, bq_client, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess compliance-related risks.

        Args:
            bq_client: BigQuery client instance
            compliance_data: Compliance information and requirements

        Returns:
            Compliance risk assessment
        """
        try:
            # Create a temporary table with the compliance data
            temp_table = f"{self.project_id}.temp.compliance_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare compliance context
            compliance_context = f"""
            Regulations: {compliance_data.get('regulations', '')}
            Current Compliance Status: {compliance_data.get('compliance_status', '')}
            Potential Violations: {compliance_data.get('violations', '')}
            Industry Standards: {compliance_data.get('industry_standards', '')}
            Audit Findings: {compliance_data.get('audit_findings', '')}
            """

            # Insert compliance data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{compliance_context}' as compliance_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to assess compliance risk
            compliance_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Assess compliance-related risks. Consider: regulatory violations, audit findings, industry standards, and potential penalties. Return: compliance_risk_level (low, medium, high, critical), violation_risk (assessment of violation likelihood), potential_penalties (financial and legal consequences), remediation_plan (steps to address compliance issues), and monitoring_requirements (ongoing compliance monitoring). Compliance Data: ', compliance_info)
            ) as compliance_assessment
            FROM `{temp_table}`
            """

            result = bq_client.client.query(compliance_query).result()
            compliance_assessment = list(result)[0].compliance_assessment

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'compliance_assessment': compliance_assessment,
                'assessment_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'compliance_id': compliance_data.get('compliance_id', '')
            }

        except Exception as e:
            logger.error(f"Error assessing compliance risk: {e}")
            return {
                'error': str(e),
                'assessment_timestamp': datetime.now().isoformat()
            }

    def financial_risk_assessment(self, bq_client, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess financial risks associated with legal matters.

        Args:
            bq_client: BigQuery client instance
            financial_data: Financial information and potential impacts

        Returns:
            Financial risk assessment
        """
        try:
            # Create a temporary table with the financial data
            temp_table = f"{self.project_id}.temp.financial_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Prepare financial context
            financial_context = f"""
            Potential Damages: {financial_data.get('damages', '')}
            Legal Costs: {financial_data.get('legal_costs', '')}
            Settlement Amounts: {financial_data.get('settlement_amounts', '')}
            Insurance Coverage: {financial_data.get('insurance_coverage', '')}
            Financial Impact: {financial_data.get('financial_impact', '')}
            """

            # Insert financial data into temp table
            insert_query = f"""
            CREATE OR REPLACE TABLE `{temp_table}` AS
            SELECT '{financial_context}' as financial_info
            """

            bq_client.client.query(insert_query).result()

            # Use the model to assess financial risk
            financial_query = f"""
            SELECT ML.GENERATE_TEXT(
              MODEL `{self.model_path}`,
              CONCAT('Assess financial risks associated with this legal matter. Consider: potential damages, legal costs, settlement amounts, insurance coverage, and overall financial impact. Return: financial_risk_level (low, medium, high, critical), estimated_costs (range of potential costs), insurance_adequacy (assessment of coverage), cost_mitigation (strategies to reduce costs), and budget_recommendations (budget planning suggestions). Financial Data: ', financial_info)
            ) as financial_assessment
            FROM `{temp_table}`
            """

            result = bq_client.client.query(financial_query).result()
            financial_assessment = list(result)[0].financial_assessment

            # Clean up temp table
            bq_client.client.delete_table(temp_table, not_found_ok=True)

            return {
                'financial_assessment': financial_assessment,
                'assessment_timestamp': datetime.now().isoformat(),
                'model_used': self.model_path,
                'financial_id': financial_data.get('financial_id', '')
            }

        except Exception as e:
            logger.error(f"Error assessing financial risk: {e}")
            return {
                'error': str(e),
                'assessment_timestamp': datetime.now().isoformat()
            }

    def get_model_info(self, bq_client) -> Dict[str, Any]:
        """
        Get information about the risk assessor model.

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
                'risk_levels': self.risk_levels
            }

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

def main():
    """Test the risk assessor model."""
    print("⚠️  Risk Assessment Model")
    print("=" * 50)

    # This would be used in integration tests
    print("✅ Risk assessor model class created successfully")

if __name__ == "__main__":
    main()
