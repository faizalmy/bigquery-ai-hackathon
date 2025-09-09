"""
Configuration Management for Legal Document Intelligence Platform
BigQuery AI Hackathon Entry

This module handles configuration loading and management for different environments.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration for the specified environment.

    Args:
        environment: Environment name (development, staging, production)
                    If None, uses ENVIRONMENT environment variable or defaults to development

    Returns:
        Configuration dictionary
    """
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')

    config_path = Path(__file__).parent.parent / 'config' / 'environments' / f'{environment}.yaml'

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override with environment variables if present
    config = _override_with_env_vars(config)

    return config

def _override_with_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Override configuration values with environment variables.

    Args:
        config: Base configuration dictionary

    Returns:
        Updated configuration dictionary
    """
    # BigQuery configuration
    if os.getenv('BIGQUERY_PROJECT_ID'):
        config['bigquery']['project_id'] = os.getenv('BIGQUERY_PROJECT_ID')

    if os.getenv('BIGQUERY_LOCATION'):
        config['bigquery']['location'] = os.getenv('BIGQUERY_LOCATION')

    if os.getenv('BIGQUERY_DATASET_PREFIX'):
        config['bigquery']['dataset_prefix'] = os.getenv('BIGQUERY_DATASET_PREFIX')

    # API configuration
    if os.getenv('API_HOST'):
        config['api']['host'] = os.getenv('API_HOST')

    if os.getenv('API_PORT'):
        config['api']['port'] = int(os.getenv('API_PORT'))

    if os.getenv('API_WORKERS'):
        config['api']['workers'] = int(os.getenv('API_WORKERS'))

    # Environment settings
    if os.getenv('DEBUG'):
        config['debug'] = os.getenv('DEBUG').lower() == 'true'

    if os.getenv('LOG_LEVEL'):
        config['log_level'] = os.getenv('LOG_LEVEL')

    return config

def get_bigquery_config() -> Dict[str, Any]:
    """
    Get BigQuery-specific configuration.

    Returns:
        BigQuery configuration dictionary
    """
    config = load_config()
    return config.get('bigquery', {})

def get_ai_models_config() -> Dict[str, Any]:
    """
    Get AI models configuration.

    Returns:
        AI models configuration dictionary
    """
    config = load_config()
    return config.get('ai_models', {})

def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration.

    Returns:
        API configuration dictionary
    """
    config = load_config()
    return config.get('api', {})
