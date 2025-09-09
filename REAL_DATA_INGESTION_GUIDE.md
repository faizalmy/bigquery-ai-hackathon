# Real Legal Data Ingestion Guide
## Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This guide explains how to download and work with real legal documents from actual sources instead of hardcoded examples.

## 🎯 **Real Data Sources**

### **1. SEC EDGAR Database** 🏢
- **Source**: U.S. Securities and Exchange Commission
- **Content**: Real business contracts, 10-K filings, 8-K filings
- **Companies**: Apple, Microsoft, Amazon, Google, Tesla, etc.
- **Document Types**: Employment agreements, supply contracts, licensing agreements

### **2. Free Law Project** ⚖️
- **Source**: CourtListener.com API
- **Content**: Real court cases, legal briefs, motions
- **Coverage**: Federal, Circuit, Bankruptcy, Appellate courts
- **Document Types**: Court opinions, legal briefs, motions, responses

### **3. Legal Briefs Database** 📋
- **Source**: Free Law Project RECAP database
- **Content**: Real legal briefs and motions
- **Types**: Motion briefs, appellate briefs, trial briefs, responses

---

## 🚀 **Quick Start**

### **Download All Real Data**
```bash
# Download all types of legal documents
make download-data
```

### **Download Specific Data Types**
```bash
# Download SEC contracts only
make download-sec-contracts

# Download court cases only
make download-court-cases

# Download legal briefs only
make download-legal-briefs
```

### **Validate Data Quality**
```bash
# Validate downloaded data
make validate-data
```

---

## 📊 **Data Download Scripts**

### **1. SEC Contracts Downloader** (`scripts/data/download_sec_contracts.py`)

**Features**:
- Downloads real contracts from SEC EDGAR database
- Extracts contract exhibits (EX-10, EX-99, etc.)
- Processes popular companies (Apple, Microsoft, Amazon, etc.)
- Handles rate limiting and error recovery

**Usage**:
```bash
python scripts/data/download_sec_contracts.py
```

**Output**:
- Real SEC contracts uploaded to BigQuery
- Local backup saved to `data/raw/sec_contracts.json`

### **2. Court Cases Downloader** (`scripts/data/download_court_cases.py`)

**Features**:
- Downloads real court cases from Free Law Project API
- Extracts legal issues and case outcomes
- Filters by court type and date range
- Processes case metadata and content

**Usage**:
```bash
python scripts/data/download_court_cases.py
```

**Output**:
- Real court cases uploaded to BigQuery
- Local backup saved to `data/raw/court_cases.json`

### **3. Legal Briefs Downloader** (`scripts/data/download_legal_briefs.py`)

**Features**:
- Downloads real legal briefs from Free Law Project
- Classifies brief types (motion, appellate, trial, etc.)
- Extracts legal arguments and case information
- Handles various brief formats

**Usage**:
```bash
python scripts/data/download_legal_briefs.py
```

**Output**:
- Real legal briefs uploaded to BigQuery
- Local backup saved to `data/raw/legal_briefs.json`

### **4. Master Data Pipeline** (`scripts/data/download_all_legal_data.py`)

**Features**:
- Orchestrates all data downloaders
- Downloads 200+ SEC contracts, 150+ court cases, 100+ briefs
- Provides comprehensive progress tracking
- Generates detailed ingestion reports

**Usage**:
```bash
python scripts/data/download_all_legal_data.py
```

**Output**:
- All document types uploaded to BigQuery
- Individual backup files for each type
- Comprehensive ingestion report

---

## 🔍 **Data Validation**

### **Validation Script** (`scripts/data/validate_legal_data.py`)

**Features**:
- Validates document content quality
- Checks for legal content indicators
- Measures document completeness
- Generates quality scores and reports

**Usage**:
```bash
python scripts/data/validate_legal_data.py
```

**Validation Criteria**:
- Minimum content length (500 characters)
- Minimum word count (100 words)
- Legal content indicators
- Required metadata fields
- Duplicate content detection

---

## 📈 **Real Data Analysis**

### **Analysis Example** (`examples/real_data_usage_example.py`)

**Features**:
- Demonstrates working with real legal documents
- Shows document statistics and trends
- Searches by company, outcome, or document type
- Retrieves full document content

**Usage**:
```bash
python examples/real_data_usage_example.py
```

**Analysis Capabilities**:
- Document statistics by type and source
- Company-specific contract searches
- Court case outcome analysis
- Legal brief type classification
- Full document content retrieval

---

## 🗄️ **BigQuery Schema**

### **Raw Data Table** (`raw_data.legal_documents`)

```sql
CREATE TABLE `project.raw_data.legal_documents` (
  document_id STRING NOT NULL,
  source_system STRING,
  document_type STRING,
  raw_content STRING NOT NULL,
  metadata JSON,
  ingestion_timestamp TIMESTAMP NOT NULL
);
```

### **Document Types**:
- **contract**: SEC EDGAR contracts and exhibits
- **court_case**: Court opinions and decisions
- **legal_brief**: Legal briefs and motions

### **Source Systems**:
- **SEC_EDGAR**: U.S. Securities and Exchange Commission
- **FREE_LAW_PROJECT**: Free Law Project API

---

## 📋 **Sample Queries**

### **Get Document Statistics**
```sql
SELECT
  document_type,
  source_system,
  COUNT(*) as document_count,
  AVG(LENGTH(raw_content)) as avg_content_length
FROM `project.raw_data.legal_documents`
GROUP BY document_type, source_system
ORDER BY document_count DESC;
```

### **Search Apple Contracts**
```sql
SELECT
  document_id,
  JSON_EXTRACT_SCALAR(metadata, '$.company_name') as company_name,
  JSON_EXTRACT_SCALAR(metadata, '$.form_type') as form_type,
  JSON_EXTRACT_SCALAR(metadata, '$.filing_date') as filing_date
FROM `project.raw_data.legal_documents`
WHERE document_type = 'contract'
AND LOWER(JSON_EXTRACT_SCALAR(metadata, '$.company_name')) LIKE '%apple%'
ORDER BY JSON_EXTRACT_SCALAR(metadata, '$.filing_date') DESC
LIMIT 10;
```

### **Find Affirmed Court Cases**
```sql
SELECT
  document_id,
  JSON_EXTRACT_SCALAR(metadata, '$.case_name') as case_name,
  JSON_EXTRACT_SCALAR(metadata, '$.court') as court,
  JSON_EXTRACT_SCALAR(metadata, '$.outcome') as outcome
FROM `project.raw_data.legal_documents`
WHERE document_type = 'court_case'
AND LOWER(JSON_EXTRACT_SCALAR(metadata, '$.outcome')) LIKE '%affirmed%'
ORDER BY JSON_EXTRACT_SCALAR(metadata, '$.date_filed') DESC
LIMIT 10;
```

---

## 🎯 **Data Collection Targets**

### **Phase 1: MVP Testing**
- **SEC Contracts**: 200 documents
- **Court Cases**: 150 documents
- **Legal Briefs**: 100 documents
- **Total**: 450+ real legal documents

### **Phase 2: Advanced Testing**
- **SEC Contracts**: 500+ documents
- **Court Cases**: 300+ documents
- **Legal Briefs**: 200+ documents
- **Total**: 1000+ real legal documents

---

## 🔧 **Configuration**

### **Rate Limiting**
- SEC EDGAR: 100ms between requests
- Free Law Project: 100ms between requests
- Respectful API usage

### **Error Handling**
- Automatic retry logic
- Graceful failure handling
- Comprehensive logging
- Progress tracking

### **Data Quality**
- Content length validation
- Legal content detection
- Metadata completeness
- Duplicate detection

---

## 📚 **Usage Examples**

### **1. Download and Analyze SEC Contracts**
```bash
# Download SEC contracts
make download-sec-contracts

# Analyze the data
python examples/real_data_usage_example.py
```

### **2. Download All Data and Validate**
```bash
# Download all legal documents
make download-data

# Validate data quality
make validate-data

# View results in BigQuery console
```

### **3. Search for Specific Documents**
```python
from examples.real_data_usage_example import RealDataAnalyzer
from src.config import load_config

config = load_config()
analyzer = RealDataAnalyzer(config)

# Search for Apple contracts
contracts = analyzer.search_contracts_by_company("Apple", limit=10)

# Search for affirmed cases
cases = analyzer.search_court_cases_by_outcome("Affirmed", limit=10)
```

---

## 🚨 **Important Notes**

### **Legal Compliance**
- ✅ All data sources are public domain
- ✅ SEC filings are publicly available
- ✅ Court opinions are public records
- ✅ Respectful API usage with rate limiting

### **Data Quality**
- Real documents may contain formatting issues
- Some documents may be incomplete
- Metadata extraction may not be 100% accurate
- Content validation helps identify quality issues

### **Performance**
- Downloads may take 10-30 minutes
- BigQuery uploads are batched for efficiency
- Local backups are created for all downloads
- Progress tracking shows real-time status

---

## 🎉 **Success Metrics**

After running the real data ingestion:

- ✅ **200+ SEC contracts** from real companies
- ✅ **150+ court cases** from actual courts
- ✅ **100+ legal briefs** from real cases
- ✅ **All data validated** for quality
- ✅ **BigQuery integration** working
- ✅ **Real document analysis** possible

---

**🎯 You now have access to real legal documents for testing your BigQuery AI legal platform!**

The hardcoded examples have been replaced with actual legal documents from authoritative sources, giving you authentic data to work with for your hackathon project.
