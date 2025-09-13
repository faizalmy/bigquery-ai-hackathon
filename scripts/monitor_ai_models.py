#!/usr/bin/env python3
"""
AI Models Monitor Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script monitors the status of BigQuery AI models.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from bigquery_client import BigQueryClient

def monitor_ai_models():
    """Monitor AI models status."""
    try:
        print("🔍 AI MODELS MONITOR")
        print("=" * 40)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Initialize client
        client = BigQueryClient()
        if not client.connect():
            print("❌ Failed to connect to BigQuery")
            return False

        project_id = client.config['project']['id']
        expected_models = ['gemini_pro', 'text_embedding', 'timesfm']

        print(f"📊 Monitoring models in: {project_id}.ai_models")
        print(f"🎯 Expected models: {', '.join(expected_models)}")
        print()

        # Check models
        try:
            models = list(client.client.list_models(f'{project_id}.ai_models'))
            print(f"📋 Found {len(models)} models:")

            if len(models) > 0:
                for model in models:
                    model_name = model.model_id.split('.')[-1]
                    print(f"  ✅ {model_name}")
                    print(f"     Created: {model.created}")
                    print(f"     Type: {model.model_type}")
                    print(f"     Location: {model.location}")
                    print()

                # Check if all expected models are present
                found_models = [model.model_id.split('.')[-1] for model in models]
                missing_models = [model for model in expected_models if model not in found_models]

                if not missing_models:
                    print("🎉 ALL MODELS ARE READY!")
                    print("✅ Ready to test AI functions")
                    return True
                else:
                    print(f"⏳ Still waiting for: {', '.join(missing_models)}")
                    return False
            else:
                print("⏳ No models found yet - still being created")
                print("💡 Models can take 10-20 minutes to be fully available")
                return False

        except Exception as e:
            print(f"❌ Error checking models: {e}")
            return False

    except Exception as e:
        print(f"❌ Monitor failed: {e}")
        return False

def main():
    """Main monitoring function."""
    try:
        if monitor_ai_models():
            print("\n🚀 Models are ready! You can now:")
            print("1. Test AI functions: python3 scripts/ai/test_bigquery_ai_functions.py")
            print("2. Run integration tests")
            print("3. Complete Phase 2 implementation")
            return 0
        else:
            print("\n⏳ Models are still being created. Check again in 5 minutes.")
            print("💡 You can run this script again: python3 scripts/monitor_ai_models.py")
            return 1

    except Exception as e:
        print(f"\n❌ Monitor script failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
