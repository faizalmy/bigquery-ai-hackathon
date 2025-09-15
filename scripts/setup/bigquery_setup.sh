#!/bin/bash
# BigQuery Setup Script
# Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

set -e  # Exit on any error

echo "🔧 Setting up BigQuery for Legal Document Intelligence Platform..."

# Configuration
PROJECT_ID="faizal-hackathon"
SERVICE_ACCOUNT_NAME="legal-ai-service"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first:"
        echo "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI is installed"
}

# Check if user is authenticated
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "No active gcloud authentication found. Please run:"
        echo "gcloud auth login"
        exit 1
    fi
    print_success "gcloud authentication is active"
}

# Set the project
set_project() {
    print_status "Setting project to ${PROJECT_ID}..."
    gcloud config set project ${PROJECT_ID}
    print_success "Project set to ${PROJECT_ID}"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."

    # Enable BigQuery API
    gcloud services enable bigquery.googleapis.com
    print_success "BigQuery API enabled"

    # Enable BigQuery AI/ML API
    gcloud services enable bigquerymigration.googleapis.com
    print_success "BigQuery AI/ML API enabled"

    # Enable ML API
    gcloud services enable ml.googleapis.com
    print_success "ML API enabled"

    # Enable AI Platform API
    gcloud services enable aiplatform.googleapis.com
    print_success "AI Platform API enabled"
}

# Create service account
create_service_account() {
    print_status "Creating service account..."

    # Check if service account already exists
    if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} &> /dev/null; then
        print_warning "Service account ${SERVICE_ACCOUNT_EMAIL} already exists"
    else
        gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
            --display-name="Legal AI Service Account" \
            --description="Service account for Legal Document Intelligence Platform"
        print_success "Service account created: ${SERVICE_ACCOUNT_EMAIL}"
    fi
}

# Assign roles to service account
assign_roles() {
    print_status "Assigning roles to service account..."

    # BigQuery Admin role
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/bigquery.admin"
    print_success "BigQuery Admin role assigned"

    # BigQuery Data Editor role
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/bigquery.dataEditor"
    print_success "BigQuery Data Editor role assigned"

    # BigQuery Job User role
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/bigquery.jobUser"
    print_success "BigQuery Job User role assigned"

    # ML Developer role
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/ml.developer"
    print_success "ML Developer role assigned"
}

# Download service account key
download_service_account_key() {
    print_status "Downloading service account key..."

    KEY_FILE="config/service-account-key.json"

    if [ -f "${KEY_FILE}" ]; then
        print_warning "Service account key already exists at ${KEY_FILE}"
    else
        gcloud iam service-accounts keys create ${KEY_FILE} \
            --iam-account=${SERVICE_ACCOUNT_EMAIL}
        print_success "Service account key downloaded to ${KEY_FILE}"
    fi
}

# Test BigQuery connection
test_connection() {
    print_status "Testing BigQuery connection..."

    # Test basic BigQuery access
    if gcloud bq ls --project=${PROJECT_ID} &> /dev/null; then
        print_success "BigQuery connection test passed"
    else
        print_error "BigQuery connection test failed"
        exit 1
    fi
}

# Main execution
main() {
    echo "🚀 Starting BigQuery setup for ${PROJECT_ID}..."
    echo ""

    check_gcloud
    check_auth
    set_project
    enable_apis
    create_service_account
    assign_roles
    download_service_account_key
    test_connection

    echo ""
    print_success "🎉 BigQuery setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Run: make setup-bigquery-tables"
    echo "2. Run: make test-bigquery"
    echo "3. Start implementing BigQuery AI functions"
    echo ""
}

# Run main function
main "$@"
