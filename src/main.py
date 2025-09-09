#!/usr/bin/env python3
"""
Legal Document Intelligence Platform - Main Application
BigQuery AI Hackathon Entry

This is the main entry point for the Legal Document Intelligence Platform.
It initializes the application and starts the development server.
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from utils.logging_config import setup_logging
from utils.bigquery_client import BigQueryClient

def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Legal Document Intelligence Platform")

        # Load configuration
        config = load_config()
        logger.info(f"Loaded configuration for environment: {config.get('environment', 'development')}")

        # Initialize BigQuery client
        bigquery_client = BigQueryClient(config)
        logger.info("BigQuery client initialized successfully")

        # Test BigQuery connection
        if bigquery_client.test_connection():
            logger.info("BigQuery connection test successful")
        else:
            logger.error("BigQuery connection test failed")
            return 1

        logger.info("Legal Document Intelligence Platform started successfully")
        logger.info("Ready for Phase 1 development and testing")

        return 0

    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
