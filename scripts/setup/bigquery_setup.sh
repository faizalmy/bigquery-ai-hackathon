#!/bin/bash

# BigQuery Setup Script for Legal Document Intelligence Platform
# BigQuery AI Hackathon Entry

set -e

echo "🚀 Setting up BigQuery for Legal Document Intelligence Platform"
echo "=============================================================="

# Configuration
PROJECT_ID="legal-ai-platform-$(date +%s)"
SERVICE_ACCOUNT_NAME="legal-ai-service"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="config/service-account-key.json"

echo "📋 Configuration:"
echo "  Project ID: ${PROJECT_ID}"
echo "  Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "  Key File: ${KEY_FILE}"
echo ""

# Step 1: Create Google Cloud Project
echo "1️⃣ Creating Google Cloud Project..."
gcloud projects create ${PROJECT_ID} --name="Legal AI Platform" --set-as-default

# Step 2: Enable Required APIs
echo "2️⃣ Enabling required APIs..."
gcloud services enable bigquery.googleapis.com --project=${PROJECT_ID}
gcloud services enable aiplatform.googleapis.com --project=${PROJECT_ID}
gcloud services enable storage.googleapis.com --project=${PROJECT_ID}
gcloud services enable cloudbuild.googleapis.com --project=${PROJECT_ID}

# Step 3: Create Service Account
echo "3️⃣ Creating service account..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="Legal AI Service Account" \
    --description="Service account for Legal Document Intelligence Platform" \
    --project=${PROJECT_ID}

# Step 4: Grant necessary permissions
echo "4️⃣ Granting permissions..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.admin"

# Step 5: Create and download service account key
echo "5️⃣ Creating service account key..."
mkdir -p config
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

# Step 6: Create BigQuery datasets
echo "6️⃣ Creating BigQuery datasets..."
bq mk --dataset --location=US --project_id=${PROJECT_ID} raw_data
bq mk --dataset --location=US --project_id=${PROJECT_ID} processed_data
bq mk --dataset --location=US --project_id=${PROJECT_ID} ai_models

# Step 7: Create environment file
echo "7️⃣ Creating environment configuration..."
cat > .env << EOF
# BigQuery Configuration
BIGQUERY_PROJECT_ID=${PROJECT_ID}
BIGQUERY_LOCATION=US
GOOGLE_APPLICATION_CREDENTIALS=${PWD}/${KEY_FILE}

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
EOF

echo ""
echo "✅ BigQuery setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update your development.yaml config with project ID: ${PROJECT_ID}"
echo "2. Test the connection: python src/main.py"
echo "3. Create tables using the schema definitions"
echo ""
echo "🔑 Service account key saved to: ${KEY_FILE}"
echo "🌍 Environment variables saved to: .env"
echo "📊 Project ID: ${PROJECT_ID}"
echo ""
echo "⚠️  Remember to add .env to your .gitignore file!"
