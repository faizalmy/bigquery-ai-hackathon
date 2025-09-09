#!/usr/bin/env python3
"""
Data Organization Utilities
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module provides utilities for organizing raw and processed data
into a structured folder hierarchy.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataOrganizer:
    """Utility class for organizing data into structured folders."""

    def __init__(self, base_data_path: Optional[Path] = None):
        """
        Initialize the data organizer.

        Args:
            base_data_path: Base path for data directory. If None, uses project root.
        """
        if base_data_path is None:
            # Assume this is called from src/utils/
            self.base_path = Path(__file__).parent.parent.parent / 'data'
        else:
            self.base_path = Path(base_data_path)

        # Define folder structure
        self.raw_folders = [
            'sec_contracts',
            'court_cases',
            'legal_briefs',
            'lii_documents',
            'lexglue_datasets',
            'justia_cases',
            'openlegal_data'
        ]

        self.processed_folders = [
            'cleaned_documents',
            'embeddings',
            'extracted_metadata',
            'structured_data'
        ]

        self.external_folders = [
            'cambridge_law',
            'lexglue',
            'public_datasets'
        ]

        self.utility_folders = [
            'validation',
            'samples'
        ]

    def ensure_folder_structure(self) -> bool:
        """
        Ensure all required folder structure exists.

        Returns:
            True if all folders were created successfully
        """
        try:
            # Create raw data folders
            for folder in self.raw_folders:
                folder_path = self.base_path / 'raw' / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured raw folder: {folder_path}")

            # Create processed data folders
            for folder in self.processed_folders:
                folder_path = self.base_path / 'processed' / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured processed folder: {folder_path}")

            # Create external data folders
            for folder in self.external_folders:
                folder_path = self.base_path / 'external' / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured external folder: {folder_path}")

            # Create utility folders
            for folder in self.utility_folders:
                folder_path = self.base_path / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured utility folder: {folder_path}")

            logger.info("📁 All folder structure ensured successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating folder structure: {e}")
            return False

    def get_raw_data_path(self, data_type: str) -> Path:
        """
        Get the path for raw data of a specific type.

        Args:
            data_type: Type of data (e.g., 'sec_contracts', 'court_cases')

        Returns:
            Path object for the raw data folder
        """
        if data_type not in self.raw_folders:
            raise ValueError(f"Unknown data type: {data_type}. Valid types: {self.raw_folders}")

        return self.base_path / 'raw' / data_type

    def get_processed_data_path(self, data_type: str) -> Path:
        """
        Get the path for processed data of a specific type.

        Args:
            data_type: Type of processed data (e.g., 'cleaned_documents', 'embeddings')

        Returns:
            Path object for the processed data folder
        """
        if data_type not in self.processed_folders:
            raise ValueError(f"Unknown processed data type: {data_type}. Valid types: {self.processed_folders}")

        return self.base_path / 'processed' / data_type

    def get_validation_path(self) -> Path:
        """Get the path for validation data."""
        return self.base_path / 'validation'

    def get_external_data_path(self, data_type: str) -> Path:
        """
        Get the path for external data of a specific type.

        Args:
            data_type: Type of external data (e.g., 'cambridge_law', 'lexglue')

        Returns:
            Path object for the external data folder
        """
        if data_type not in self.external_folders:
            raise ValueError(f"Unknown external data type: {data_type}. Valid types: {self.external_folders}")

        return self.base_path / 'external' / data_type

    def create_timestamped_filename(self, base_name: str, extension: str = 'json') -> str:
        """
        Create a timestamped filename.

        Args:
            base_name: Base name for the file
            extension: File extension (default: 'json')

        Returns:
            Timestamped filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.{extension}"

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current data organization.

        Returns:
            Dictionary with folder structure and file counts
        """
        summary = {
            'base_path': str(self.base_path),
            'raw_data': {},
            'processed_data': {},
            'external_data': {},
            'utility_folders': {}
        }

        # Count files in raw data folders
        for folder in self.raw_folders:
            folder_path = self.base_path / 'raw' / folder
            if folder_path.exists():
                files = list(folder_path.glob('*'))
                summary['raw_data'][folder] = {
                    'path': str(folder_path),
                    'file_count': len(files),
                    'files': [f.name for f in files]
                }
            else:
                summary['raw_data'][folder] = {
                    'path': str(folder_path),
                    'file_count': 0,
                    'files': []
                }

        # Count files in processed data folders
        for folder in self.processed_folders:
            folder_path = self.base_path / 'processed' / folder
            if folder_path.exists():
                files = list(folder_path.glob('*'))
                summary['processed_data'][folder] = {
                    'path': str(folder_path),
                    'file_count': len(files),
                    'files': [f.name for f in files]
                }
            else:
                summary['processed_data'][folder] = {
                    'path': str(folder_path),
                    'file_count': 0,
                    'files': []
                }

        # Count files in external data folders
        for folder in self.external_folders:
            folder_path = self.base_path / 'external' / folder
            if folder_path.exists():
                files = list(folder_path.glob('*'))
                summary['external_data'][folder] = {
                    'path': str(folder_path),
                    'file_count': len(files),
                    'files': [f.name for f in files]
                }
            else:
                summary['external_data'][folder] = {
                    'path': str(folder_path),
                    'file_count': 0,
                    'files': []
                }

        # Count files in utility folders
        for folder in self.utility_folders:
            folder_path = self.base_path / folder
            if folder_path.exists():
                files = list(folder_path.glob('*'))
                summary['utility_folders'][folder] = {
                    'path': str(folder_path),
                    'file_count': len(files),
                    'files': [f.name for f in files]
                }
            else:
                summary['utility_folders'][folder] = {
                    'path': str(folder_path),
                    'file_count': 0,
                    'files': []
                }

        return summary

    def print_data_summary(self):
        """Print a formatted summary of the data organization."""
        summary = self.get_data_summary()

        print(f"\n📊 Data Organization Summary")
        print(f"Base Path: {summary['base_path']}")
        print(f"\n📁 Raw Data:")
        for folder, info in summary['raw_data'].items():
            print(f"  {folder}: {info['file_count']} files")
            if info['files']:
                for file in info['files'][:3]:  # Show first 3 files
                    print(f"    - {file}")
                if len(info['files']) > 3:
                    print(f"    ... and {len(info['files']) - 3} more")

        print(f"\n🔧 Processed Data:")
        for folder, info in summary['processed_data'].items():
            print(f"  {folder}: {info['file_count']} files")
            if info['files']:
                for file in info['files'][:3]:  # Show first 3 files
                    print(f"    - {file}")
                if len(info['files']) > 3:
                    print(f"    ... and {len(info['files']) - 3} more")

        print(f"\n🌐 External Data:")
        for folder, info in summary['external_data'].items():
            print(f"  {folder}: {info['file_count']} files")
            if info['files']:
                for file in info['files'][:3]:  # Show first 3 files
                    print(f"    - {file}")
                if len(info['files']) > 3:
                    print(f"    ... and {len(info['files']) - 3} more")


def main():
    """Main function for testing the data organizer."""
    organizer = DataOrganizer()

    print("🔧 Ensuring folder structure...")
    success = organizer.ensure_folder_structure()

    if success:
        print("✅ Folder structure ensured successfully!")
        organizer.print_data_summary()
    else:
        print("❌ Failed to ensure folder structure")


if __name__ == "__main__":
    main()
