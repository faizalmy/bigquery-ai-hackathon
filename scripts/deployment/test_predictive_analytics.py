#!/usr/bin/env python3
"""
Test Predictive Analytics Models
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests the predictive analytics functionality.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from utils.bigquery_client import BigQueryClient
from config import load_config
from ai.predictive_analytics import PredictiveAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_case_outcome_prediction():
    """Test case outcome prediction functionality."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize predictive analytics
        analytics = PredictiveAnalytics(project_id)

        logger.info("🧪 Testing Case Outcome Prediction...")

        # Test case data
        case_data = {
            'content': 'This is a Supreme Court case involving constitutional law and First Amendment rights of public employees.',
            'type': 'constitutional_law',
            'jurisdiction': 'federal'
        }

        # Test outcome prediction
        prediction_result = analytics.predict_case_outcome(bq_client, case_data)

        if 'prediction' in prediction_result:
            logger.info("✅ Case Outcome Prediction: SUCCESS")
            logger.info(f"   🎯 Predicted Outcome: {prediction_result['prediction']['outcome']}")
            logger.info(f"   📊 Confidence Score: {prediction_result['prediction']['confidence_score']}")
            logger.info(f"   ⚡ Complexity Level: {prediction_result['prediction']['complexity_level']}")
            logger.info(f"   ⏰ Timeline: {prediction_result['prediction']['estimated_timeline']}")
            logger.info(f"   📝 Method: {prediction_result['method']}")
            return True
        else:
            logger.error(f"❌ Case Outcome Prediction: {prediction_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Case outcome prediction test failed: {e}")
        return False

def test_risk_assessment():
    """Test risk assessment functionality."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize predictive analytics
        analytics = PredictiveAnalytics(project_id)

        logger.info("🧪 Testing Risk Assessment...")

        # Test case data
        case_data = {
            'content': 'This case involves potential constitutional violations and First Amendment rights issues with significant legal precedent.',
            'type': 'constitutional_law'
        }

        # Test risk assessment
        risk_result = analytics.assess_legal_risk(bq_client, case_data)

        if 'risk_assessment' in risk_result:
            logger.info("✅ Risk Assessment: SUCCESS")
            logger.info(f"   ⚠️  Risk Score: {risk_result['risk_assessment']['risk_score']}")
            logger.info(f"   🚨 Risk Category: {risk_result['risk_assessment']['risk_category']}")
            logger.info(f"   🎯 Primary Risk Factor: {risk_result['risk_assessment']['primary_risk_factor']}")
            logger.info(f"   💡 Mitigation Strategy: {risk_result['risk_assessment']['mitigation_strategy']}")
            logger.info(f"   📝 Method: {risk_result['method']}")
            return True
        else:
            logger.error(f"❌ Risk Assessment: {risk_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Risk assessment test failed: {e}")
        return False

def test_strategy_generation():
    """Test strategy generation functionality."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize predictive analytics
        analytics = PredictiveAnalytics(project_id)

        logger.info("🧪 Testing Strategy Generation...")

        # Test case data
        case_data = {
            'content': 'This constitutional law case involves First Amendment rights of public employees and requires strategic legal approach.',
            'type': 'constitutional_law'
        }

        # Test strategy generation
        strategy_result = analytics.generate_legal_strategy(bq_client, case_data)

        if 'strategy' in strategy_result:
            logger.info("✅ Strategy Generation: SUCCESS")
            logger.info(f"   🎯 Primary Strategy: {strategy_result['strategy']['primary_strategy']}")
            logger.info(f"   ⚔️  Tactical Approach: {strategy_result['strategy']['tactical_approach']}")
            logger.info(f"   💬 Key Arguments: {strategy_result['strategy']['key_arguments']}")
            logger.info(f"   👥 Resources: {strategy_result['strategy']['resource_requirements']}")
            logger.info(f"   ⏰ Timeline: {strategy_result['strategy']['estimated_timeline']}")
            logger.info(f"   📝 Method: {strategy_result['method']}")
            return True
        else:
            logger.error(f"❌ Strategy Generation: {strategy_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Strategy generation test failed: {e}")
        return False

def test_compliance_checking():
    """Test compliance checking functionality."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize predictive analytics
        analytics = PredictiveAnalytics(project_id)

        logger.info("🧪 Testing Compliance Checking...")

        # Test document data
        document_data = {
            'content': 'This legal document contains standard contract terms and regulatory compliance requirements.',
            'type': 'contract'
        }

        # Test compliance checking
        compliance_result = analytics.check_compliance(bq_client, document_data)

        if 'compliance_check' in compliance_result:
            logger.info("✅ Compliance Checking: SUCCESS")
            logger.info(f"   📊 Compliance Score: {compliance_result['compliance_check']['compliance_score']}")
            logger.info(f"   ✅ Compliance Status: {compliance_result['compliance_check']['compliance_status']}")
            logger.info(f"   📋 Compliance Areas: {compliance_result['compliance_check']['compliance_areas']}")
            logger.info(f"   💡 Recommendations: {compliance_result['compliance_check']['recommendations']}")
            logger.info(f"   📝 Method: {compliance_result['method']}")
            return True
        else:
            logger.error(f"❌ Compliance Checking: {compliance_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Compliance checking test failed: {e}")
        return False

def test_comprehensive_analysis():
    """Test comprehensive analysis functionality."""
    try:
        # Load configuration
        config = load_config()
        project_id = config['bigquery']['project_id']

        # Initialize BigQuery client
        bq_client = BigQueryClient(config)

        # Initialize predictive analytics
        analytics = PredictiveAnalytics(project_id)

        logger.info("🧪 Testing Comprehensive Analysis...")

        # Test case data
        case_data = {
            'content': 'This is a complex constitutional law case involving First Amendment rights, potential violations, and requires comprehensive legal analysis.',
            'type': 'constitutional_law',
            'jurisdiction': 'federal'
        }

        # Test comprehensive analysis
        comprehensive_result = analytics.comprehensive_analysis(bq_client, case_data)

        if 'comprehensive_analysis' in comprehensive_result:
            logger.info("✅ Comprehensive Analysis: SUCCESS")

            analysis = comprehensive_result['comprehensive_analysis']

            # Check if all components are present
            components = ['outcome_prediction', 'risk_assessment', 'strategy_generation', 'compliance_check']
            for component in components:
                if component in analysis:
                    logger.info(f"   ✅ {component.replace('_', ' ').title()}: Included")
                else:
                    logger.info(f"   ❌ {component.replace('_', ' ').title()}: Missing")

            logger.info(f"   📊 Overall Confidence: {analysis.get('overall_confidence', 0):.3f}")
            logger.info(f"   📝 Method: {comprehensive_result['method']}")
            return True
        else:
            logger.error(f"❌ Comprehensive Analysis: {comprehensive_result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Comprehensive analysis test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔮 Predictive Analytics Models - Test Suite")
    print("=" * 60)

    test_results = {}

    # Test 1: Case Outcome Prediction
    print("\n1️⃣ Testing Case Outcome Prediction...")
    test_results['outcome_prediction'] = test_case_outcome_prediction()

    # Test 2: Risk Assessment
    print("\n2️⃣ Testing Risk Assessment...")
    test_results['risk_assessment'] = test_risk_assessment()

    # Test 3: Strategy Generation
    print("\n3️⃣ Testing Strategy Generation...")
    test_results['strategy_generation'] = test_strategy_generation()

    # Test 4: Compliance Checking
    print("\n4️⃣ Testing Compliance Checking...")
    test_results['compliance_checking'] = test_compliance_checking()

    # Test 5: Comprehensive Analysis
    print("\n5️⃣ Testing Comprehensive Analysis...")
    test_results['comprehensive_analysis'] = test_comprehensive_analysis()

    # Print results summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)

    successful_tests = 0
    for test_name, result in test_results.items():
        if result:
            logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
            successful_tests += 1
        else:
            logger.error(f"❌ {test_name.replace('_', ' ').title()}: FAILED")

    total_tests = len(test_results)
    logger.info(f"🎯 Overall: {successful_tests}/{total_tests} tests passed")

    if successful_tests == total_tests:
        print("\n🎉 All predictive analytics tests passed!")
        print("✅ Phase 2.6 Predictive Analytics Models are working")
        print("\n📋 Working Features:")
        print("   🔮 Case Outcome Prediction - SQL-based outcome analysis")
        print("   ⚠️  Risk Assessment - Legal risk scoring and mitigation")
        print("   🎯 Strategy Generation - Legal strategy recommendations")
        print("   ✅ Compliance Checking - Regulatory compliance analysis")
        print("   🔍 Comprehensive Analysis - Integrated legal analysis")
        print("\n🚀 Ready to proceed to Phase 2.7: Final Validation")
    else:
        print(f"\n⚠️  {successful_tests}/{total_tests} predictive analytics tests passed")
        print("🔧 Some components need further development")

    return 0 if successful_tests == total_tests else 1

if __name__ == "__main__":
    exit(main())
