# Legal Document Sources for Testing
## BigQuery AI Hackathon - Legal Document Intelligence Platform

---

## 🎯 **Best Legal Document Sources for Your Project**

### **🥇 Top Recommended Sources**

#### **1. Material Contracts Corpus (MCC) - BEST FOR CONTRACTS**
**Source**: SEC EDGAR Database
**Size**: 1+ million contracts
**Time Period**: 2000-2023
**Document Types**:
- Employment agreements
- Supply contracts
- Licensing agreements
- Merger agreements
- Service contracts

**Access**:
- **Direct**: [SEC EDGAR Database](https://www.sec.gov/edgar)
- **Processed Dataset**: [Material Contracts Corpus](https://arxiv.org/abs/2504.02864)
- **BigQuery**: Available in some public datasets

**Why Perfect for Your Project**:
- ✅ **Real business contracts** with actual legal language
- ✅ **Structured metadata** (company, date, contract type)
- ✅ **Large volume** for testing scalability
- ✅ **Public domain** - no copyright issues
- ✅ **Diverse contract types** for comprehensive testing

---

#### **2. Free Law Project - BEST FOR COURT CASES**
**Source**: Court filings and opinions
**Size**: Millions of documents
**Document Types**:
- Court opinions
- Legal briefs
- Motions
- Judgments
- Oral arguments

**Access**:
- **Website**: [CourtListener.com](https://www.courtlistener.com)
- **API**: [Free Law Project API](https://www.courtlistener.com/api/)
- **Bulk Download**: Available for research

**Why Perfect for Your Project**:
- ✅ **Real court cases** with legal reasoning
- ✅ **Case outcomes** for prediction testing
- ✅ **Legal precedents** for similarity matching
- ✅ **Free access** for research purposes
- ✅ **API available** for easy integration

---

#### **3. Cambridge Law Corpus (CLC) - BEST FOR UK CASES**
**Source**: UK Court System
**Size**: 250,000+ cases
**Time Period**: 16th century to present
**Document Types**:
- UK court cases
- Legal judgments
- Case annotations
- Outcome predictions

**Access**:
- **Research Paper**: [Cambridge Law Corpus](https://arxiv.org/abs/2309.12269)
- **Dataset**: Available for academic research
- **Contact**: Cambridge University

**Why Perfect for Your Project**:
- ✅ **Historical depth** - centuries of legal data
- ✅ **Expert annotations** on case outcomes
- ✅ **High quality** legal reasoning
- ✅ **Diverse time periods** for testing
- ✅ **Academic standard** for validation

---

### **🥈 Secondary Sources**

#### **4. LexGLUE Benchmark Dataset**
**Source**: Multiple legal databases
**Size**: Various sizes per task
**Document Types**:
- Legal text classification
- Case outcome prediction
- Legal question answering
- Contract analysis

**Access**:
- **GitHub**: [LexGLUE Repository](https://github.com/coastalcph/lexglue)
- **Paper**: [LexGLUE Paper](https://arxiv.org/abs/2110.00976)
- **Download**: Direct from GitHub

**Why Useful**:
- ✅ **Benchmark datasets** for validation
- ✅ **Multiple legal tasks** covered
- ✅ **Standardized format** for testing
- ✅ **Academic validation** of results

---

#### **5. MultiLegalPile (Advanced)**
**Source**: 17 jurisdictions, 24 languages
**Size**: 689GB corpus
**Document Types**:
- Court opinions
- Contracts
- Administrative rules
- Legislative records

**Access**:
- **Research Paper**: [MultiLegalPile](https://arxiv.org/abs/2306.02069)
- **Dataset**: Available for research
- **Contact**: Research institutions

**Why Useful**:
- ✅ **Multilingual** legal documents
- ✅ **International scope** for global testing
- ✅ **Comprehensive coverage** of legal types
- ✅ **Large scale** for robust testing

---

## 🚀 **Quick Start Guide**

### **Option 1: SEC Contracts (Recommended for MVP)**

#### **Step 1: Access SEC EDGAR**
```bash
# Download recent contracts
wget -r -np -nH --cut-dirs=3 -R "index.html*" \
  https://www.sec.gov/Archives/edgar/data/
```

#### **Step 2: Process for BigQuery**
```python
import pandas as pd
import requests
from bs4 import BeautifulSoup

def download_sec_contracts(company_cik, num_documents=100):
    """
    Download SEC contracts for testing
    """
    contracts = []

    # SEC EDGAR API endpoint
    base_url = f"https://www.sec.gov/Archives/edgar/data/{company_cik}"

    # Download recent filings
    for filing in recent_filings:
        if filing['form'] in ['8-K', '10-K', '10-Q']:
            contract_data = {
                'company': filing['company'],
                'date': filing['date'],
                'form_type': filing['form'],
                'content': filing['content'],
                'document_type': 'contract'
            }
            contracts.append(contract_data)

    return contracts
```

#### **Step 3: Upload to BigQuery**
```sql
-- Create table for legal documents
CREATE TABLE `your_project.legal_documents` (
  case_id STRING,
  document_id STRING,
  document_type STRING,
  content STRING,
  created_date DATE,
  company_name STRING,
  form_type STRING
);

-- Load sample data
INSERT INTO `your_project.legal_documents`
SELECT
  CONCAT('SEC_', ROW_NUMBER() OVER()) as case_id,
  CONCAT('DOC_', ROW_NUMBER() OVER()) as document_id,
  'contract' as document_type,
  content,
  PARSE_DATE('%Y-%m-%d', date) as created_date,
  company_name,
  form_type
FROM `your_project.sec_contracts_sample`
LIMIT 1000;
```

---

### **Option 2: Court Cases (Recommended for Advanced Features)**

#### **Step 1: Access Free Law Project**
```python
import requests
import json

def download_court_cases(num_cases=500):
    """
    Download court cases from Free Law Project
    """
    cases = []

    # Free Law Project API
    api_url = "https://www.courtlistener.com/api/rest/v3/search/"

    params = {
        'stat_Precedential': 'on',
        'order_by': 'score desc',
        'format': 'json',
        'stat_Errata': 'on'
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    for result in data['results'][:num_cases]:
        case_data = {
            'case_id': result['absolute_url'],
            'case_name': result['caseName'],
            'court': result['court'],
            'date_filed': result['dateFiled'],
            'content': result['text'],
            'outcome': result.get('outcome', 'Unknown'),
            'document_type': 'court_case'
        }
        cases.append(case_data)

    return cases
```

#### **Step 2: Process and Upload**
```python
# Convert to DataFrame
df = pd.DataFrame(cases)

# Upload to BigQuery
df.to_gbq(
    destination_table='your_project.legal_documents',
    project_id='your_project',
    if_exists='append'
)
```

---

## 📊 **Sample Data Structure**

### **Recommended Table Schema**
```sql
CREATE TABLE `your_project.legal_documents` (
  -- Primary identifiers
  case_id STRING NOT NULL,
  document_id STRING NOT NULL,

  -- Document metadata
  document_type STRING,  -- 'contract', 'court_case', 'brief', 'motion'
  title STRING,
  created_date DATE,

  -- Content
  content STRING,  -- Full document text
  summary STRING,  -- AI-generated summary

  -- Legal metadata
  court STRING,    -- For court cases
  jurisdiction STRING,
  case_outcome STRING,  -- For court cases
  legal_issues ARRAY<STRING>,

  -- Business metadata
  company_name STRING,  -- For contracts
  contract_type STRING,  -- For contracts
  parties ARRAY<STRING>,

  -- AI processing metadata
  is_processed BOOLEAN DEFAULT FALSE,
  processing_date TIMESTAMP,
  confidence_score FLOAT64,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

---

## 🎯 **Recommended Data Collection Strategy**

### **Phase 1: MVP Testing (Week 1)**
**Target**: 1,000 documents
**Sources**:
- 500 SEC contracts (recent 10-K, 8-K filings)
- 300 court cases (Free Law Project)
- 200 legal briefs (CourtListener)

**Focus**: Basic document analysis and summarization

### **Phase 2: Advanced Testing (Week 2)**
**Target**: 5,000+ documents
**Sources**:
- 2,000 SEC contracts (diverse types)
- 2,000 court cases (multiple jurisdictions)
- 1,000 legal briefs and motions

**Focus**: Vector search, similarity matching, predictions

---

## 🔧 **Data Processing Pipeline**

### **Step 1: Document Ingestion**
```python
def process_legal_document(raw_document):
    """
    Process raw legal document for BigQuery
    """
    processed = {
        'case_id': generate_case_id(raw_document),
        'document_id': generate_document_id(raw_document),
        'document_type': classify_document_type(raw_document),
        'content': clean_text(raw_document['content']),
        'created_date': parse_date(raw_document['date']),
        'metadata': extract_metadata(raw_document)
    }
    return processed
```

### **Step 2: Quality Control**
```python
def validate_document(document):
    """
    Validate document quality for AI processing
    """
    checks = {
        'has_content': len(document['content']) > 100,
        'is_legal_document': contains_legal_terms(document['content']),
        'is_english': is_english_text(document['content']),
        'has_metadata': document['metadata'] is not None
    }
    return all(checks.values())
```

### **Step 3: BigQuery Upload**
```python
def upload_to_bigquery(documents, table_name):
    """
    Upload processed documents to BigQuery
    """
    df = pd.DataFrame(documents)

    # Upload in batches
    df.to_gbq(
        destination_table=table_name,
        project_id='your_project',
        if_exists='append',
        chunksize=1000
    )
```

---

## 📋 **Sample Document Types for Testing**

### **Contract Types** (from SEC EDGAR)
1. **Employment Agreements** - CEO contracts, executive compensation
2. **Supply Contracts** - Vendor agreements, procurement contracts
3. **Licensing Agreements** - Technology licenses, IP agreements
4. **Merger Agreements** - Acquisition contracts, M&A documents
5. **Service Contracts** - Consulting agreements, service level agreements

### **Court Case Types** (from Free Law Project)
1. **Civil Cases** - Contract disputes, tort cases
2. **Criminal Cases** - Criminal proceedings, appeals
3. **Appellate Cases** - Appeals court decisions
4. **Supreme Court Cases** - High court decisions
5. **Administrative Cases** - Regulatory proceedings

### **Legal Brief Types** (from CourtListener)
1. **Motion Briefs** - Legal motions and responses
2. **Appellate Briefs** - Appeal arguments and responses
3. **Amicus Briefs** - Friend of the court briefs
4. **Trial Briefs** - Trial preparation documents
5. **Settlement Briefs** - Settlement negotiations

---

## 🚨 **Important Legal Considerations**

### **Public Domain Status**
- ✅ **SEC filings** - Public domain, free to use
- ✅ **Court opinions** - Public domain, free to use
- ✅ **Government documents** - Public domain, free to use
- ⚠️ **Some court filings** - May have restrictions
- ❌ **Private contracts** - Not publicly available

### **Usage Guidelines**
1. **Research purposes only** - Don't use for commercial purposes
2. **Respect privacy** - Remove personal information
3. **Cite sources** - Acknowledge data sources
4. **Follow terms of service** - Respect API limits
5. **Academic use** - Many datasets are for research only

---

## 🎯 **Quick Start Commands**

### **Download SEC Contracts**
```bash
# Install required tools
pip install requests beautifulsoup4 pandas

# Download sample contracts
python download_sec_contracts.py --count 100 --output contracts.json
```

### **Download Court Cases**
```bash
# Download court cases
python download_court_cases.py --count 200 --output cases.json
```

### **Upload to BigQuery**
```bash
# Upload to BigQuery
python upload_to_bigquery.py --input contracts.json --table legal_documents
```

---

## 📚 **Additional Resources**

### **GitHub Repositories**
- [Legal ML Datasets](https://github.com/neelguha/legal-ml-datasets)
- [LexGLUE](https://github.com/coastalcph/lexglue)
- [Legal Document Processing](https://github.com/legal-tech-research)

### **Research Papers**
- [Material Contracts Corpus](https://arxiv.org/abs/2504.02864)
- [Cambridge Law Corpus](https://arxiv.org/abs/2309.12269)
- [MultiLegalPile](https://arxiv.org/abs/2306.02069)

### **APIs and Tools**
- [SEC EDGAR API](https://www.sec.gov/edgar/sec-api-documentation)
- [Free Law Project API](https://www.courtlistener.com/api/)
- [CourtListener Search](https://www.courtlistener.com/api/rest/v3/search/)

---

**🎯 Recommendation: Start with SEC contracts (Material Contracts Corpus) for your MVP - they're real, diverse, and perfect for testing your BigQuery AI legal platform!**
