# BigQuery Setup Guide
## Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This guide will help you set up BigQuery for your Legal Document Intelligence Platform.

## 🚀 Quick Setup

### Prerequisites
- Google Cloud SDK installed and authenticated
- Python virtual environment activated
- Project dependencies installed

### Step 1: Run the Setup Script

```bash
# Make sure you're in the project root directory
cd /Users/faizal/Sites/kaggle/bigquery-ai-hackathon

# Run the BigQuery setup script
./scripts/setup/bigquery_setup.sh
```

This script will:
- Create a new Google Cloud project
- Enable required APIs (BigQuery, AI Platform, Storage)
- Create a service account with necessary permissions
- Download service account credentials
- Create BigQuery datasets
- Generate environment configuration

### Step 2: Create Tables

```bash
# Create all BigQuery tables based on your schema definitions
python scripts/setup/create_bigquery_tables.py
```

### Step 3: Test the Setup

```bash
# Test your BigQuery connection and setup
python scripts/setup/test_bigquery_setup.py
```

## 📋 Manual Setup (Alternative)

If you prefer to set up BigQuery manually or need to customize the setup:

### 1. Create Google Cloud Project

```bash
# Create a new project (replace with your preferred project ID)
gcloud projects create legal-ai-platform-$(date +%s) --name="Legal AI Platform"

# Set as default project
gcloud config set project legal-ai-platform-$(date +%s)
```

### 2. Enable Required APIs

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create legal-ai-service \
    --display-name="Legal AI Service Account" \
    --description="Service account for Legal Document Intelligence Platform"

# Grant permissions
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:legal-ai-service@$(gcloud config get-value project).iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:legal-ai-service@$(gcloud config get-value project).iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### 4. Download Service Account Key

```bash
# Create config directory
mkdir -p config

# Download service account key
gcloud iam service-accounts keys create config/service-account-key.json \
    --iam-account=legal-ai-service@$(gcloud config get-value project).iam.gserviceaccount.com
```

### 5. Create BigQuery Datasets

```bash
# Create datasets
bq mk --dataset --location=US raw_data
bq mk --dataset --location=US processed_data
bq mk --dataset --location=US ai_models
```

### 6. Create Environment File

Create a `.env` file in your project root:

```bash
# BigQuery Configuration
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_LOCATION=US
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🗄️ Database Schema

Your BigQuery setup includes the following datasets and tables:

### Datasets
- **raw_data**: Raw legal documents and data ingestion
- **processed_data**: Processed and cleaned legal documents
- **ai_models**: AI model configurations and metadata

### Tables

#### raw_data.legal_documents
- `document_id` (STRING, REQUIRED): Unique identifier
- `source_system` (STRING, NULLABLE): Source system
- `document_type` (STRING, NULLABLE): Document type
- `raw_content` (STRING, REQUIRED): Raw document content
- `metadata` (JSON, NULLABLE): Document metadata
- `ingestion_timestamp` (TIMESTAMP, REQUIRED): Ingestion time

#### processed_data.legal_documents
- `document_id` (STRING, REQUIRED): Unique identifier
- `document_type` (STRING, NULLABLE): Document type
- `cleaned_content` (STRING, REQUIRED): Cleaned content
- `extracted_metadata` (JSON, NULLABLE): Extracted metadata
- `quality_score` (FLOAT64, NULLABLE): Quality score (0-1)
- `processed_timestamp` (TIMESTAMP, REQUIRED): Processing time

#### processed_data.document_embeddings
- `document_id` (STRING, REQUIRED): Unique identifier
- `embedding` (ARRAY<FLOAT64>, REQUIRED): Document embedding vector
- `model_name` (STRING, REQUIRED): Embedding model name
- `created_timestamp` (TIMESTAMP, REQUIRED): Creation time

## 🧪 Testing Your Setup

### Test Connection
```python
from src.config import load_config
from src.utils.bigquery_client import BigQueryClient

config = load_config()
bq_client = BigQueryClient(config)

if bq_client.test_connection():
    print("✅ BigQuery connection successful!")
else:
    print("❌ BigQuery connection failed")
```

### Test Query
```python
# Simple test query
query = "SELECT 1 as test_value"
job = bq_client.execute_query(query)
if job:
    for row in job.result():
        print(f"Test result: {row.test_value}")
```

## 🔧 Configuration

### Environment Variables
- `BIGQUERY_PROJECT_ID`: Your Google Cloud project ID
- `BIGQUERY_LOCATION`: BigQuery location (default: US)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file
- `ENVIRONMENT`: Environment name (development/staging/production)

### Configuration Files
- `config/environments/development.yaml`: Development environment config
- `config/bigquery/dataset_schemas.json`: Dataset schemas
- `config/bigquery/table_schemas.json`: Table schemas

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   Error: Could not automatically determine credentials
   ```
   **Solution**: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to your service account key file path.

2. **Project Not Found**
   ```
   Error: Project 'your-project-id' not found
   ```
   **Solution**: Verify your project ID and ensure you have access to the project.

3. **Permission Denied**
   ```
   Error: Permission denied
   ```
   **Solution**: Ensure your service account has the necessary BigQuery permissions.

4. **API Not Enabled**
   ```
   Error: BigQuery API has not been used
   ```
   **Solution**: Enable the BigQuery API in your Google Cloud project.

### Getting Help

1. Check the logs in `logs/legal_ai_platform.log`
2. Run the test script: `python scripts/setup/test_bigquery_setup.py`
3. Verify your configuration: `python src/main.py`

## 🎯 Next Steps

After successful BigQuery setup:

1. **Start Data Ingestion**: Begin loading legal documents into the `raw_data` dataset
2. **Process Documents**: Use your AI models to process and clean documents
3. **Create Embeddings**: Generate document embeddings for vector search
4. **Build Analytics**: Create dashboards and reports using BigQuery

## 📚 Resources

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Python Client](https://googleapis.dev/python/bigquery/latest/)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)

---

**🎉 Congratulations! Your BigQuery setup is complete and ready for the Legal Document Intelligence Platform!**
