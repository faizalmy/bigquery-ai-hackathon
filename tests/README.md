# BigQuery AI Legal Document Intelligence Platform - Test Suite

This directory contains comprehensive end-to-end tests for the BigQuery AI Legal Document Intelligence Platform, organized by competition tracks.

## Test Structure

```
tests/
├── __init__.py
├── README.md
├── run_all_tests.py          # Run all test suites
├── run_track1_tests.py       # Run Track 1 tests only
├── run_track2_tests.py       # Run Track 2 tests only
├── track1/                   # Track 1: Generative AI Functions
│   ├── __init__.py
│   ├── test_ml_generate_text.py
│   ├── test_ai_generate_table.py
│   ├── test_ai_generate_bool.py
│   └── test_ml_forecast.py
├── track2/                   # Track 2: Vector Search Functions
│   ├── __init__.py
│   ├── test_ml_generate_embedding.py
│   └── test_vector_search.py
└── integration/              # Integration Tests
    ├── __init__.py
    └── test_end_to_end_workflow.py
```

## Test Suites

### Track 1: Generative AI Functions

**ML.GENERATE_TEXT** (`test_ml_generate_text.py`)
- Document summarization functionality
- Single and multiple document processing
- Performance benchmarks
- Error handling
- Summary quality validation

**AI.GENERATE_TABLE** (`test_ai_generate_table.py`)
- Legal data extraction functionality
- JSON parsing validation
- Data quality checks
- Performance testing
- Error handling

**AI.GENERATE_BOOL** (`test_ai_generate_bool.py`)
- Urgency detection functionality
- Boolean result consistency
- Urgency distribution analysis
- Performance testing
- Error handling

**ML.FORECAST** (`test_ml_forecast.py`)
- Case outcome prediction functionality
- Forecast quality validation
- Timestamp validation
- Parameter validation
- Performance testing

### Track 2: Vector Search Functions

**ML.GENERATE_EMBEDDING** (`test_ml_generate_embedding.py`)
- Document embedding generation
- Vector quality validation
- Consistency testing
- Performance benchmarks
- Error handling

**VECTOR_SEARCH** (`test_vector_search.py`)
- Semantic similarity search
- Query processing
- Similarity quality validation
- Performance testing
- Legal relevance validation

### Integration Tests

**End-to-End Workflow** (`test_end_to_end_workflow.py`)
- Complete Track 1 workflow
- Complete Track 2 workflow
- Combined Track 1 + Track 2 workflow
- Performance benchmarks
- Error recovery testing
- Data consistency validation
- Scalability testing

## Running Tests

### Run All Tests
```bash
cd tests
python run_all_tests.py
```

### Run Track 1 Tests Only
```bash
cd tests
python run_track1_tests.py
```

### Run Track 2 Tests Only
```bash
cd tests
python run_track2_tests.py
```

### Run Individual Test Suites
```bash
cd tests
python track1/test_ml_generate_text.py
python track1/test_ai_generate_table.py
python track1/test_ai_generate_bool.py
python track1/test_ml_forecast.py
python track2/test_ml_generate_embedding.py
python track2/test_vector_search.py
python integration/test_end_to_end_workflow.py
```

## Test Requirements

### Prerequisites
- BigQuery project configured with service account
- Legal documents loaded in `legal_ai_platform_raw_data.legal_documents`
- Document embeddings in `legal_ai_platform_vector_indexes.document_embeddings`
- AI models created (`gemini_pro`, `text_embedding`, `legal_timesfm`)

### Environment Setup
```bash
# Ensure you're in the project root
cd /Users/faizal/Sites/kaggle/bigquery-ai-hackathon

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Test Coverage

### Functionality Coverage
- ✅ All 6 BigQuery AI functions tested
- ✅ Single and multiple document processing
- ✅ Parameter validation
- ✅ Error handling
- ✅ Performance benchmarks
- ✅ Data quality validation

### Integration Coverage
- ✅ Complete Track 1 workflow
- ✅ Complete Track 2 workflow
- ✅ Combined workflows
- ✅ End-to-end scenarios
- ✅ Error recovery
- ✅ Scalability testing

### Performance Coverage
- ✅ Individual function performance
- ✅ Workflow performance
- ✅ Benchmark validation
- ✅ Timeout handling

## Test Results

### Expected Results
- **Track 1**: 4/4 functions passing (100%)
- **Track 2**: 2/2 functions passing (100%)
- **Integration**: 1/1 workflow passing (100%)
- **Overall**: 7/7 test suites passing (100%)

### Performance Benchmarks
- **ML.GENERATE_TEXT**: < 30 seconds
- **AI.GENERATE_TABLE**: < 30 seconds
- **AI.GENERATE_BOOL**: < 30 seconds
- **ML.FORECAST**: < 30 seconds
- **ML.GENERATE_EMBEDDING**: < 30 seconds
- **VECTOR_SEARCH**: < 30 seconds
- **Complete Workflow**: < 3 minutes

## Troubleshooting

### Common Issues

**BigQuery Connection Errors**
- Verify service account key is configured
- Check project ID and dataset permissions
- Ensure BigQuery API is enabled

**Model Not Found Errors**
- Run model setup: `python src/bigquery_ai_functions.py`
- Verify models exist in `ai_models` dataset
- Check model creation logs

**Data Not Found Errors**
- Ensure legal documents are loaded
- Verify document embeddings exist
- Check table schemas and data

**Performance Issues**
- Check BigQuery quotas and limits
- Verify network connectivity
- Monitor BigQuery job status

### Debug Mode
```bash
# Run tests with debug logging
export LOG_LEVEL=DEBUG
python run_all_tests.py
```

## Test Data

### Test Documents
- Primary test document: `caselaw_000001`
- Test queries: Legal document search terms
- Expected results: Valid legal document processing

### Validation Criteria
- Document IDs must be consistent
- Results must have valid structure
- Performance must meet benchmarks
- Error handling must be graceful

## Contributing

### Adding New Tests
1. Create test file in appropriate track directory
2. Follow existing test patterns and structure
3. Include comprehensive test coverage
4. Add to test runner scripts
5. Update this README

### Test Standards
- Use descriptive test names
- Include setup and teardown
- Validate all result structures
- Test error conditions
- Include performance benchmarks
- Add comprehensive logging

## Competition Compliance

This test suite validates compliance with BigQuery AI Hackathon requirements:

- **Track 1**: All 4 generative AI functions implemented and tested
- **Track 2**: Both vector search functions implemented and tested
- **Integration**: Complete workflows validated
- **Performance**: Benchmarks meet competition standards
- **Quality**: Comprehensive test coverage and validation

---

**Author**: Faizal
**Date**: September 2025
**Competition**: BigQuery AI Hackathon
