#!/usr/bin/env python3
"""
Master HFforLegal Dataset Download and Processing Script
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script orchestrates the complete pipeline for downloading and processing
real legal documents from the HFforLegal/case-law dataset.
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_script(script_path: Path, description: str) -> bool:
    """
    Run a Python script and return success status.

    Args:
        script_path: Path to the script to run
        description: Description of what the script does

    Returns:
        bool: True if script succeeded, False otherwise
    """
    try:
        logger.info(f"Running {description}...")
        logger.info(f"Script: {script_path}")

        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )

        if result.returncode == 0:
            logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ {description} failed")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Failed to run {script_path}: {e}")
        return False

def main():
    """Main execution function."""
    try:
        print("🚀 HFforLegal Legal Data Pipeline")
        print("=" * 50)
        print("Downloading and processing real legal documents...")
        print("Dataset: HFforLegal/case-law")
        print("License: CC-BY-4.0")
        print("Focus: US legal decisions for BigQuery AI")
        print(f"Started at: {datetime.now().isoformat()}")
        print()

        # Get script directory
        script_dir = Path(__file__).parent

        # Step 1: Download HFforLegal case-law dataset
        download_script = script_dir / "download_caselaw_dataset.py"
        if not download_script.exists():
            logger.error(f"Download script not found: {download_script}")
            return 1

        if not run_script(download_script, "HFforLegal Case-law Dataset Download"):
            logger.error("Download step failed. Stopping pipeline.")
            return 1

        print()

        # Step 2: Process legal data
        process_script = script_dir / "process_caselaw_data.py"
        if not process_script.exists():
            logger.error(f"Process script not found: {process_script}")
            return 1

        if not run_script(process_script, "HFforLegal Legal Data Processing"):
            logger.error("Processing step failed. Stopping pipeline.")
            return 1

        print()
        print("🎉 HFforLegal Legal Data Pipeline Completed Successfully!")
        print("=" * 50)
        print(f"Completed at: {datetime.now().isoformat()}")
        print()
        print("📁 Output Files:")
        print("  - data/raw/caselaw_data/caselaw_documents.json")
        print("  - data/processed/processed_hf_legal_documents.json")
        print("  - data/processed/hf_legal_processing_report.json")
        print()
        print("✅ Ready for BigQuery AI functions!")
        print()
        print("🎯 Next Steps:")
        print("  1. Load data into BigQuery")
        print("  2. Test BigQuery AI functions")
        print("  3. Create Jupyter notebooks")
        print("  4. Build Streamlit UI")

        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
