# Legal Document Intelligence Platform - Makefile
# Common development commands for the BigQuery AI Hackathon project

.PHONY: help setup install test clean deploy

# Default target
help:
	@echo "Legal Document Intelligence Platform - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup              - Complete project setup"
	@echo "  setup-bigquery     - Setup BigQuery project and datasets"
	@echo "  setup-env          - Setup Python virtual environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  install            - Install Python dependencies"
	@echo "  dev                - Start development server"
	@echo "  test               - Run all tests"
	@echo "  test-unit          - Run unit tests"
	@echo "  test-integration   - Run integration tests"
	@echo ""
	@echo "Data Commands:"
	@echo "  process-data       - Process legal documents"
	@echo "  download-data      - Download legal datasets"
	@echo "  validate-data      - Validate data quality"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  deploy-staging     - Deploy to staging environment"
	@echo "  deploy-production  - Deploy to production environment"
	@echo ""
	@echo "Documentation Commands:"
	@echo "  docs               - Generate documentation"
	@echo "  docs-serve         - Serve documentation locally"
	@echo ""
	@echo "Competition Commands:"
	@echo "  prepare-submission - Prepare competition submission"
	@echo "  validate-submission - Validate submission requirements"
	@echo "  generate-demo      - Generate demo materials"
	@echo "  package-submission - Create final submission package"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean              - Clean temporary files"
	@echo "  format             - Format code with black and isort"
	@echo "  lint               - Run linting checks"

# Setup Commands
setup: setup-env install setup-bigquery
	@echo "✅ Complete project setup completed"

setup-env:
	@echo "🔧 Setting up Python virtual environment..."
	python3 -m venv venv
	@echo "✅ Virtual environment created"

setup-bigquery:
	@echo "🔧 Setting up BigQuery project..."
	@echo "⚠️  Please run the BigQuery setup commands manually:"
	@echo "   gcloud projects create legal-ai-platform-{timestamp}"
	@echo "   gcloud config set project legal-ai-platform-{timestamp}"
	@echo "   gcloud services enable bigquery.googleapis.com"
	@echo "   gcloud services enable aiplatform.googleapis.com"
	@echo "   gcloud services enable storage.googleapis.com"

# Development Commands
install:
	@echo "📦 Installing Python dependencies..."
	source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

dev:
	@echo "🚀 Starting development server..."
	source venv/bin/activate && python src/main.py

# Testing Commands
test:
	@echo "🧪 Running all tests..."
	source venv/bin/activate && python -m pytest tests/ -v

test-unit:
	@echo "🧪 Running unit tests..."
	source venv/bin/activate && python -m pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	source venv/bin/activate && python -m pytest tests/integration/ -v

# Data Commands
process-data:
	@echo "📊 Processing legal documents..."
	source venv/bin/activate && python scripts/data/process_documents.py

download-data:
	@echo "📥 Downloading legal datasets..."
	source venv/bin/activate && python scripts/data/download_legal_datasets.py

validate-data:
	@echo "✅ Validating data quality..."
	source venv/bin/activate && python scripts/data/validate_data.py

# Deployment Commands
deploy-staging:
	@echo "🚀 Deploying to staging environment..."
	@echo "⚠️  Staging deployment not implemented yet"

deploy-production:
	@echo "🚀 Deploying to production environment..."
	@echo "⚠️  Production deployment not implemented yet"

# Documentation Commands
docs:
	@echo "📚 Generating documentation..."
	@echo "⚠️  Documentation generation not implemented yet"

docs-serve:
	@echo "📚 Serving documentation locally..."
	@echo "⚠️  Documentation serving not implemented yet"

# Competition Commands
prepare-submission:
	@echo "📋 Preparing competition submission..."
	@echo "⚠️  Submission preparation not implemented yet"

validate-submission:
	@echo "✅ Validating submission requirements..."
	@echo "⚠️  Submission validation not implemented yet"

generate-demo:
	@echo "🎬 Generating demo materials..."
	@echo "⚠️  Demo generation not implemented yet"

package-submission:
	@echo "📦 Creating final submission package..."
	@echo "⚠️  Submission packaging not implemented yet"

# Utility Commands
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "✅ Cleanup completed"

format:
	@echo "🎨 Formatting code..."
	source venv/bin/activate && black src/ tests/ scripts/
	source venv/bin/activate && isort src/ tests/ scripts/
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Running linting checks..."
	source venv/bin/activate && flake8 src/ tests/ scripts/
	source venv/bin/activate && mypy src/
	@echo "✅ Linting completed"
