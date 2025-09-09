#!/usr/bin/env python3
"""
Test Data Organization
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This script tests the data organization utilities to ensure proper folder structure.
"""

import sys
import json
from pathlib import Path

# Add src to path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from utils.data_organization import DataOrganizer

def test_data_organization():
    """Test the data organization functionality."""
    print("🧪 Testing Data Organization...")

    # Initialize data organizer
    organizer = DataOrganizer()

    # Test folder structure creation
    print("\n1. Testing folder structure creation...")
    success = organizer.ensure_folder_structure()
    if success:
        print("✅ Folder structure created successfully!")
    else:
        print("❌ Failed to create folder structure")
        return False

    # Test path retrieval
    print("\n2. Testing path retrieval...")
    try:
        sec_path = organizer.get_raw_data_path('sec_contracts')
        print(f"✅ SEC contracts path: {sec_path}")

        embeddings_path = organizer.get_processed_data_path('embeddings')
        print(f"✅ Embeddings path: {embeddings_path}")

        validation_path = organizer.get_validation_path()
        print(f"✅ Validation path: {validation_path}")

    except Exception as e:
        print(f"❌ Error getting paths: {e}")
        return False

    # Test filename generation
    print("\n3. Testing filename generation...")
    try:
        filename = organizer.create_timestamped_filename('test_data', 'json')
        print(f"✅ Generated filename: {filename}")

        # Verify filename format
        if '_' in filename and filename.endswith('.json'):
            print("✅ Filename format is correct")
        else:
            print("❌ Filename format is incorrect")
            return False

    except Exception as e:
        print(f"❌ Error generating filename: {e}")
        return False

    # Test data summary
    print("\n4. Testing data summary...")
    try:
        summary = organizer.get_data_summary()
        print(f"✅ Data summary generated successfully")
        print(f"   Base path: {summary['base_path']}")
        print(f"   Raw data folders: {len(summary['raw_data'])}")
        print(f"   Processed data folders: {len(summary['processed_data'])}")

    except Exception as e:
        print(f"❌ Error generating data summary: {e}")
        return False

    # Test creating a sample file
    print("\n5. Testing file creation...")
    try:
        test_data = {
            "test": True,
            "message": "This is a test file for data organization",
            "timestamp": "2024-01-01T00:00:00Z"
        }

        # Create test file in sec_contracts folder
        sec_path = organizer.get_raw_data_path('sec_contracts')
        test_filename = organizer.create_timestamped_filename('test_contracts', 'json')
        test_file = sec_path / test_filename

        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        print(f"✅ Test file created: {test_file}")

        # Verify file exists
        if test_file.exists():
            print("✅ Test file exists and is readable")
        else:
            print("❌ Test file was not created")
            return False

    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False

    # Print final summary
    print("\n6. Final data organization summary:")
    organizer.print_data_summary()

    print("\n✅ All data organization tests passed!")
    return True

def main():
    """Main function."""
    print("🚀 Starting Data Organization Tests")
    print("=" * 50)

    success = test_data_organization()

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
