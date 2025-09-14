:::::: {.cell .markdown}
# 🏆 BigQuery AI Hackathon - Legal Document Intelligence Platform

**Competition Entry**: Legal Document Analysis using BigQuery AI Functions

**Tracks**: Track 1 (Generative AI) + Track 2 (Vector Search)

**Author**: Faizal
::::::

:::::: {.cell .markdown}
## 📋 **Section 1: Introduction & Problem Statement**

### **1.1 Competition Overview & Track Selection**

Welcome to our BigQuery AI Hackathon submission! We're excited to present the **Legal Document Intelligence Platform** - a groundbreaking solution that addresses real-world challenges in legal document processing using Google Cloud's cutting-edge BigQuery AI capabilities.

#### **Our Track Selection: Dual-Track Approach**
We've strategically chosen to implement **both Track 1 (Generative AI) and Track 2 (Vector Search)** to create a comprehensive legal document intelligence solution:

- **Track 1 - Generative AI**: Document summarization, data extraction, urgency detection, and outcome prediction
- **Track 2 - Vector Search**: Semantic similarity search, document clustering, and intelligent case matching

This dual-track approach allows us to demonstrate the full power of BigQuery AI while solving complex real-world legal document processing challenges, as documented in our implementation phases (`docs/architecture/implementation_phases.md`).
::::::

:::::: {.cell .markdown}
### **1.2 Problem Statement - Legal Document Processing Challenges**

The legal industry faces a critical challenge: **legal professionals spend significant time on document processing and analysis** rather than on strategic legal work. This inefficiency creates bottlenecks and costs.

#### **Current Pain Points**
1. **Manual Document Summarization**: Lawyers spend hours reading and summarizing lengthy legal documents
2. **Data Extraction Inefficiency**: Critical legal information buried in unstructured text requires manual extraction
3. **Case Similarity Search**: Finding relevant precedents and similar cases is time-consuming and often incomplete
4. **Urgency Detection**: Important deadlines and urgent matters are frequently missed
5. **Outcome Prediction**: Limited ability to predict case outcomes based on historical data

#### **Industry Impact**
- **Time Waste**: Legal professionals spend significant time on document processing
- **Cost Implications**: High costs associated with manual document handling
- **Error Rates**: Manual data extraction prone to human error
- **Missed Opportunities**: Critical legal insights lost due to information overload
::::::

:::::: {.cell .markdown}
### **1.3 Solution Approach - Legal Document Intelligence Platform**

Our **Legal Document Intelligence Platform** leverages BigQuery AI to transform legal document processing through intelligent automation and semantic understanding.

#### **Platform Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Legal Document Intelligence Platform          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────────────┐    ┌─────────────┐ │
│  │   Legal     │    │   Track 1: Gen AI   │    │  Automated  │ │
│  │ Documents   │───▶│   ML.GENERATE_TEXT  │───▶│ Summaries  │ │
│  │ (Input)     │    │   AI.GENERATE_TABLE │    │ & Insights │ │
│  └─────────────┘    │   AI.GENERATE_BOOL  │    └─────────────┘ │
│                     │   AI.FORECAST       │                    │
│  ┌─────────────┐    ┌─────────────────────┐    ┌─────────────┐ │
│  │   Legal     │    │   Track 2: Vector   │    │  Semantic   │ │
│  │ Documents   │───▶│   ML.GENERATE_EMBED │───▶│ Search &   │ │
│  │ (Input)     │    │   VECTOR_SEARCH     │    │ Matching   │ │
│  └─────────────┘    │   VECTOR_DISTANCE   │    └─────────────┘ │
│                     └─────────────────────┘                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Hybrid Intelligence Pipeline                   │ │
│  │         Combining Generative AI + Vector Search             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### **Key Innovation: Hybrid Pipeline**
Our solution combines the power of both tracks to create a comprehensive legal document intelligence system:

1. **Generative AI Processing**: Automatically summarize, extract data, detect urgency, and predict outcomes
2. **Vector Search Intelligence**: Find similar cases, cluster documents, and enable semantic search
3. **Hybrid Integration**: Cross-reference results between tracks for enhanced accuracy and insights
::::::

:::::: {.cell .markdown}
### **1.4 Technical Implementation & Business Impact**

#### **BigQuery AI Functions Implementation**
Our platform leverages the full power of BigQuery AI through these core functions:

**Track 1 - Generative AI Functions:**
- `ML.GENERATE_TEXT`: Document summarization and content generation
- `AI.GENERATE_TABLE`: Structured legal data extraction
- `AI.GENERATE_BOOL`: Urgency detection and priority classification
- `AI.FORECAST`: Case outcome prediction based on historical data

**Track 2 - Vector Search Functions:**
- `ML.GENERATE_EMBEDDING`: Document embedding generation for semantic search
- `VECTOR_SEARCH`: Similarity search and document matching
- `VECTOR_DISTANCE`: Precise similarity calculations
- `CREATE VECTOR INDEX`: Performance optimization for large document collections

#### **Expected Business Impact**
Based on our implementation testing (see `docs/implementation/implementation_completion_report.md`):
- **Processing Speed**: 2,421 documents/minute achieved in testing
- **Vector Search Accuracy**: 56-62% similarity matching for legal documents
- **Error Rate**: 0% in BigQuery AI function execution
- **Scalability**: 1,000+ documents processed successfully

#### **Technical Excellence**
Based on our implementation (see `docs/architecture/implementation_phases.md`):
- **Production-Ready**: Built on existing, tested codebase with validated BigQuery AI functions
- **Scalable Architecture**: Successfully processed 1,000+ legal documents
- **Error Handling**: Comprehensive error management implemented in `src/bigquery_ai_functions.py`
- **Performance**: 2.17s per document for ML.GENERATE_TEXT, 7 forecast points for ML.FORECAST
::::::

:::::: {.cell .markdown}
### **1.5 Next Steps**

In the following sections, we will demonstrate:

1. **Environment Setup**: Complete BigQuery configuration and dependency management
2. **Data Loading**: Legal document dataset preparation and validation
3. **Track 1 Implementation**: Generative AI functions in action
4. **Track 2 Implementation**: Vector search capabilities demonstration
5. **Hybrid Pipeline**: End-to-end document processing workflow
6. **Results & Analysis**: Performance metrics and business impact validation
::::::

:::::: {.cell .markdown}
## ⚙️ **Section 2: Setup & Configuration**

### **2.1 Environment Setup & Dependencies**

Before diving into the technical implementation, let's set up the environment with all required dependencies for our Legal Document Intelligence Platform.

#### **Virtual Environment Setup**
Create and activate a virtual environment for isolated dependency management:
::::::

:::::: {.cell .code}
```python
# Create virtual environment
import subprocess
import sys
import os

# Create virtual environment
print("Creating virtual environment...")
subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
print("✅ Virtual environment created successfully!")

# Show activation instructions
print("\n📋 To activate the virtual environment:")
if os.name == 'nt':  # Windows
    print("venv\\Scripts\\activate")
else:  # macOS/Linux
    print("source venv/bin/activate")

print("\n🔍 To verify activation:")
if os.name == 'nt':  # Windows
    print("where python")
else:  # macOS/Linux
    print("which python")
```
::::::

:::::: {.cell .markdown}
#### **Python Environment Requirements**
Our platform requires Python 3.8+ with specific library versions for optimal BigQuery AI performance:
::::::

:::::: {.cell .code}
```python
# System requirements check
import sys
import platform

print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")
print(f"Virtual Environment: {sys.prefix}")

# Verify Python version compatibility
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8+ is required for BigQuery AI functions")
else:
    print("✅ Python version compatible with BigQuery AI")

# Verify virtual environment is active
if 'venv' in sys.prefix or 'virtualenv' in sys.prefix:
    print("✅ Virtual environment is active")
else:
    print("⚠️  Warning: Virtual environment may not be active")
```
::::::

:::::: {.cell .markdown}
#### **Dependency Installation**
Install all required packages from our existing `requirements.txt`:
::::::

:::::: {.cell .code}
```python
# Install dependencies using virtual environment
import subprocess
import os
import sys

# Determine pip path based on OS
if os.name == 'nt':  # Windows
    pip_path = os.path.join("venv", "Scripts", "pip.exe")
else:  # macOS/Linux
    pip_path = os.path.join("venv", "bin", "pip")

print(f"Using pip: {pip_path}")

try:
    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)

    # Install requirements
    print("Installing dependencies from requirements.txt...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)

    # Verify installation
    print("Verifying installation...")
    result = subprocess.run([pip_path, "list"], capture_output=True, text=True)

    # Check for key packages
    key_packages = ["google-cloud-bigquery", "bigframes", "pandas", "numpy"]
    for package in key_packages:
        if package in result.stdout:
            print(f"✅ {package} installed")
        else:
            print(f"❌ {package} not found")

    print("✅ Dependencies installed successfully!")

except subprocess.CalledProcessError as e:
    print(f"❌ Installation failed: {e}")
    print("Please ensure virtual environment is activated and requirements.txt exists")
```
::::::

:::::: {.cell .markdown}
**Key Dependencies:**
- **google-cloud-bigquery>=3.36.0**: BigQuery client library
- **bigframes>=2.18.0**: BigQuery DataFrames for AI functions
- **pandas>=2.3.2, numpy>=2.3.2**: Data processing
- **matplotlib>=3.10.6, seaborn>=0.13.2, plotly>=5.24.1**: Visualization
- **PyYAML>=6.0.1**: Configuration management
- **datasets>=3.2.0, huggingface-hub>=0.28.1**: Legal data access
::::::

:::::: {.cell .markdown}
### **2.2 BigQuery Configuration & Authentication**

Our platform uses a comprehensive configuration system to manage BigQuery connections and AI model settings.

#### **Configuration Loading**
Load configuration from our existing `config/bigquery_config.yaml`:
::::::

:::::: {.cell .code}
```python
import yaml
import os
from pathlib import Path

# Load configuration
config_path = "config/bigquery_config.yaml"
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

print("✅ Configuration loaded successfully")
print(f"Project ID: {config['project']['id']}")
print(f"Location: {config['project']['location']}")
print(f"Environment: {config['environment']['current']}")
```
::::::

:::::: {.cell .markdown}
#### **Google Cloud Authentication**
Set up authentication using our existing service account:
::::::

:::::: {.cell .code}
```python
# Set up authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'config/service-account-key.json'

# Verify authentication
from google.cloud import bigquery
client = bigquery.Client(project=config['project']['id'])

print(f"✅ Authenticated with project: {client.project}")
print(f"✅ BigQuery client initialized successfully")
```
::::::

:::::: {.cell .markdown}
### **2.3 Library Imports & Basic Setup**

Import essential libraries and configure BigQuery connection:
::::::

:::::: {.cell .code}
```python
# Core BigQuery and AI libraries
import bigframes
import bigframes.pandas as bf
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

# Data processing and utilities
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Additional utilities
import requests
import warnings
warnings.filterwarnings('ignore')

# Configure BigFrames
bf.options.bigquery.project = config['project']['id']
bf.options.bigquery.location = config['project']['location']

print("✅ All libraries imported successfully")
print(f"✅ BigFrames configured for project: {bf.options.bigquery.project}")
```
::::::

:::::: {.cell .markdown}
### **2.4 Connection Verification**

Verify BigQuery connection and check basic setup:
::::::

:::::: {.cell .code}
```python
# Verify BigQuery connection
try:
    # Test basic query
    test_query = "SELECT 1 as test_value"
    result = client.query(test_query).result()
    test_value = next(result).test_value
    print(f"✅ BigQuery connection verified (test value: {test_value})")

    # Check document count
    count_query = f"""
    SELECT COUNT(*) as document_count
    FROM `{config['project']['id']}.legal_ai_platform_raw_data.legal_documents`
    """
    result = client.query(count_query).result()
    doc_count = next(result).document_count
    print(f"✅ Legal documents available: {doc_count:,} documents")

    print("\n🎉 Setup complete! Ready to demonstrate BigQuery AI capabilities.")

except Exception as e:
    print(f"❌ Setup verification failed: {e}")
    raise
```
::::::

:::::: {.cell .markdown}
**Ready to transform legal document processing with BigQuery AI? Let's dive into the technical implementation!** 🚀
::::::
