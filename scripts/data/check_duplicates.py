#!/usr/bin/env python3
"""
Duplicate Checker for Legal Data Ingestion
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script checks for duplicate companies and other duplicates in the data ingestion scripts.
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import Counter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DuplicateChecker:
    """Checker for duplicates in data ingestion scripts."""

    def __init__(self):
        """Initialize the duplicate checker."""
        self.project_root = Path(__file__).parent.parent.parent
        self.data_scripts_dir = self.project_root / 'scripts' / 'data'

    def find_company_ciks_in_file(self, file_path: Path) -> List[Tuple[str, int]]:
        """
        Find all company CIKs in a file with line numbers.

        Args:
            file_path: Path to the file to check

        Returns:
            List of tuples (cik, line_number)
        """
        ciks = []

        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    # Look for CIK patterns (10-digit numbers in quotes)
                    cik_matches = re.findall(r"'(\d{10})'", line)
                    for cik in cik_matches:
                        ciks.append((cik, line_num))
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")

        return ciks

    def check_duplicates_in_file(self, file_path: Path) -> Dict[str, List[int]]:
        """
        Check for duplicate CIKs in a single file.

        Args:
            file_path: Path to the file to check

        Returns:
            Dictionary mapping CIK to list of line numbers where it appears
        """
        ciks = self.find_company_ciks_in_file(file_path)
        cik_locations = {}

        for cik, line_num in ciks:
            if cik not in cik_locations:
                cik_locations[cik] = []
            cik_locations[cik].append(line_num)

        # Filter to only show duplicates
        duplicates = {cik: lines for cik, lines in cik_locations.items() if len(lines) > 1}

        return duplicates

    def check_all_data_scripts(self) -> Dict[str, Dict[str, List[int]]]:
        """
        Check all data scripts for duplicates.

        Returns:
            Dictionary mapping file names to their duplicate CIKs
        """
        all_duplicates = {}

        # Find all Python files in the data scripts directory
        python_files = list(self.data_scripts_dir.glob('*.py'))

        for file_path in python_files:
            duplicates = self.check_duplicates_in_file(file_path)
            if duplicates:
                all_duplicates[file_path.name] = duplicates

        return all_duplicates

    def get_company_name(self, cik: str) -> str:
        """Get company name from CIK."""
        company_names = {
            '0000320193': 'Apple Inc.',
            '0000789019': 'Microsoft Corporation',
            '0001018724': 'Amazon.com Inc.',
            '0001652044': 'Google (Alphabet Inc.)',
            '0001318605': 'Tesla Inc.',
            '0001067983': 'Berkshire Hathaway',
        }
        return company_names.get(cik, f'Company {cik}')

    def print_duplicate_report(self, all_duplicates: Dict[str, Dict[str, List[int]]]):
        """Print a comprehensive duplicate report."""
        print("\n" + "=" * 60)
        print("🔍 DUPLICATE COMPANY CIK CHECK REPORT")
        print("=" * 60)

        if not all_duplicates:
            print("✅ No duplicate company CIKs found in any data scripts!")
            return

        total_duplicates = 0
        for file_name, duplicates in all_duplicates.items():
            print(f"\n📄 File: {file_name}")
            print("-" * 40)

            for cik, line_numbers in duplicates.items():
                company_name = self.get_company_name(cik)
                print(f"   🔴 CIK: {cik} ({company_name})")
                print(f"      Found on lines: {', '.join(map(str, line_numbers))}")
                print(f"      Duplicate count: {len(line_numbers)}")
                total_duplicates += len(line_numbers) - 1  # -1 because one is original

        print(f"\n📊 Summary:")
        print(f"   Total duplicate instances: {total_duplicates}")
        print(f"   Files with duplicates: {len(all_duplicates)}")

        print(f"\n💡 Recommendations:")
        print(f"   1. Remove duplicate CIKs from the affected files")
        print(f"   2. Use the remove_duplicate_companies() function")
        print(f"   3. Consider using a centralized company list")

    def check_cross_file_duplicates(self) -> Dict[str, List[str]]:
        """
        Check for CIKs that appear in multiple files.

        Returns:
            Dictionary mapping CIK to list of files where it appears
        """
        cik_files = {}

        # Find all Python files in the data scripts directory
        python_files = list(self.data_scripts_dir.glob('*.py'))

        for file_path in python_files:
            ciks = self.find_company_ciks_in_file(file_path)
            unique_ciks = set(cik for cik, _ in ciks)

            for cik in unique_ciks:
                if cik not in cik_files:
                    cik_files[cik] = []
                cik_files[cik].append(file_path.name)

        # Filter to only show CIKs that appear in multiple files
        cross_file_duplicates = {cik: files for cik, files in cik_files.items() if len(files) > 1}

        return cross_file_duplicates

    def print_cross_file_report(self, cross_file_duplicates: Dict[str, List[str]]):
        """Print cross-file duplicate report."""
        print("\n" + "=" * 60)
        print("🔄 CROSS-FILE DUPLICATE CIK REPORT")
        print("=" * 60)

        if not cross_file_duplicates:
            print("✅ No CIKs found in multiple files!")
            return

        print(f"Found {len(cross_file_duplicates)} CIKs that appear in multiple files:")
        print()

        for cik, files in cross_file_duplicates.items():
            company_name = self.get_company_name(cik)
            print(f"🔴 CIK: {cik} ({company_name})")
            print(f"   Files: {', '.join(files)}")
            print()

    def run_full_check(self):
        """Run complete duplicate check."""
        print("🔍 Checking for duplicate company CIKs in data ingestion scripts...")

        # Check for duplicates within files
        all_duplicates = self.check_all_data_scripts()
        self.print_duplicate_report(all_duplicates)

        # Check for cross-file duplicates
        cross_file_duplicates = self.check_cross_file_duplicates()
        self.print_cross_file_report(cross_file_duplicates)

        # Summary
        total_within_file_duplicates = sum(len(duplicates) for duplicates in all_duplicates.values())
        total_cross_file_duplicates = len(cross_file_duplicates)

        print("\n" + "=" * 60)
        print("📊 FINAL SUMMARY")
        print("=" * 60)
        print(f"Files with within-file duplicates: {len(all_duplicates)}")
        print(f"Total duplicate CIK instances: {total_within_file_duplicates}")
        print(f"CIKs appearing in multiple files: {total_cross_file_duplicates}")

        if total_within_file_duplicates == 0 and total_cross_file_duplicates == 0:
            print("\n🎉 All checks passed! No duplicates found.")
        else:
            print(f"\n⚠️  Found duplicates that should be cleaned up.")

def main():
    """Main function to run duplicate check."""
    checker = DuplicateChecker()
    checker.run_full_check()

if __name__ == "__main__":
    main()
