# Data Organization Guide

## Overview

This document describes the organized folder structure for the Legal Document Intelligence Platform's data management system. The structure separates raw downloaded data from processed data and provides clear organization by data source and type.

## Folder Structure

```
data/
├── raw/                          # Raw downloaded data (unprocessed)
│   ├── sec_contracts/           # SEC EDGAR contracts and filings
│   ├── court_cases/             # Court cases from various sources
│   ├── legal_briefs/            # Legal briefs and motions
│   ├── lii_documents/           # Legal Information Institute documents
│   ├── lexglue_datasets/        # LexGLUE benchmark datasets
│   ├── justia_cases/            # Justia case law database
│   └── openlegal_data/          # OpenLegalData repository
├── processed/                    # Processed/cleaned data
│   ├── cleaned_documents/       # Cleaned and normalized documents
│   ├── embeddings/              # Document embeddings for ML
│   ├── extracted_metadata/      # Extracted metadata and annotations
│   └── structured_data/         # Structured data for analysis
├── external/                     # External datasets (third-party)
│   ├── cambridge_law/           # Cambridge Law datasets
│   ├── lexglue/                 # LexGLUE external resources
│   └── public_datasets/         # Other public legal datasets
├── validation/                   # Validation results and reports
└── samples/                      # Sample data for testing
```

## Key Features

### 1. **Organized Raw Data Storage**
- Each data source has its own subfolder within `raw/`
- Files are saved with timestamps for versioning (e.g., `sec_contracts_20240910_143022.json`)
- Automatic folder creation when downloading data

### 2. **Separate Processed Data**
- Clean separation between raw and processed data
- Processed data organized by processing stage
- Ready for machine learning and analysis pipelines

### 3. **Data Organization Utility**
- `DataOrganizer` class provides consistent path management
- Automatic folder structure creation
- Timestamped filename generation
- Data summary and reporting capabilities

## Usage Examples

### Using the DataOrganizer Class

```python
from src.utils.data_organization import DataOrganizer

# Initialize organizer
organizer = DataOrganizer()

# Ensure folder structure exists
organizer.ensure_folder_structure()

# Get paths for specific data types
sec_path = organizer.get_raw_data_path('sec_contracts')
embeddings_path = organizer.get_processed_data_path('embeddings')

# Create timestamped filenames
filename = organizer.create_timestamped_filename('contracts', 'json')
# Result: contracts_20240910_143022.json

# Get data summary
summary = organizer.get_data_summary()
organizer.print_data_summary()
```

### Download Scripts Integration

All download scripts now use the organized structure:

```python
# In download scripts
output_dir = organizer.get_raw_data_path('sec_contracts')
filename = organizer.create_timestamped_filename('sec_contracts', 'json')
output_file = output_dir / filename
```

## File Naming Convention

### Raw Data Files
- Format: `{data_type}_{timestamp}.json`
- Example: `sec_contracts_20240910_143022.json`
- Timestamp format: `YYYYMMDD_HHMMSS`

### Processed Data Files
- Format: `{processing_stage}_{data_type}_{timestamp}.{ext}`
- Example: `cleaned_contracts_20240910_143022.json`
- Example: `embeddings_cases_20240910_143022.pkl`

## Data Flow

1. **Download Phase**: Raw data saved to `data/raw/{source}/`
2. **Processing Phase**: Cleaned data saved to `data/processed/cleaned_documents/`
3. **Analysis Phase**: Embeddings and metadata saved to respective processed folders
4. **Validation Phase**: Results saved to `data/validation/`

## Benefits

### 1. **Clear Separation**
- Raw data is never mixed with processed data
- Easy to identify data source and processing stage
- Prevents accidental overwrites

### 2. **Version Control**
- Timestamped files allow tracking of data versions
- Easy to rollback to previous data versions
- Clear audit trail of data updates

### 3. **Scalability**
- Organized structure supports large datasets
- Easy to add new data sources
- Consistent interface across all scripts

### 4. **Maintainability**
- Clear folder structure is self-documenting
- Easy to locate specific data types
- Simplified backup and archival processes

## Testing

Run the data organization test to verify everything works:

```bash
python3 scripts/data/test_data_organization.py
```

This test will:
- Create the folder structure
- Test path retrieval
- Test filename generation
- Create sample files
- Display data summary

## Migration Notes

### Existing Data
- The old `lii_documents.json` file in `data/raw/` remains for backward compatibility
- New downloads will use the organized structure
- Existing data can be moved to appropriate subfolders as needed

### Script Updates
All download scripts have been updated to use the new structure:
- `download_all_legal_data.py` - Master pipeline
- `download_sec_contracts.py` - SEC contracts
- `download_court_cases.py` - Court cases
- `download_legal_briefs.py` - Legal briefs
- `download_lii_legal_docs.py` - LII documents
- `download_lexglue_datasets.py` - LexGLUE datasets
- `download_justia_cases.py` - Justia cases
- `download_openlegaldata.py` - OpenLegalData

## Future Enhancements

1. **Data Validation**: Add validation rules for each data type
2. **Compression**: Implement compression for large datasets
3. **Indexing**: Add searchable indexes for quick data retrieval
4. **Backup**: Automated backup system for critical data
5. **Monitoring**: Data quality monitoring and alerting

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure write permissions for data directories
2. **Path Issues**: Use `DataOrganizer` class for consistent path handling
3. **Missing Folders**: Run `organizer.ensure_folder_structure()` to create folders

### Getting Help

- Check the test script output for validation
- Use `organizer.print_data_summary()` to see current structure
- Review download script logs for specific errors

---

*This guide is part of the Legal Document Intelligence Platform for the BigQuery AI Hackathon.*
