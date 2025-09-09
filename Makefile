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
	@echo "  setup-bigquery-tables - Create BigQuery tables"
	@echo "  test-bigquery      - Test BigQuery setup"
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
	@echo "  download-data      - Download all legal datasets"
	@echo "  download-sec-contracts - Download SEC contracts"
	@echo "  download-court-cases   - Download court cases"
	@echo "  download-legal-briefs  - Download legal briefs"
	@echo "  validate-data      - Validate data quality"
	@echo "  test-sec-download  - Test SEC contracts download"
	@echo "  demo-data          - Generate demo legal documents"
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
setup: setup-env install setup-bigquery setup-bigquery-tables test-bigquery
	@echo "✅ Complete project setup completed"

setup-env:
	@echo "🔧 Setting up Python virtual environment..."
	python3 -m venv venv
	@echo "✅ Virtual environment created"

setup-bigquery:
	@echo "🔧 Setting up BigQuery project..."
	@echo "Running BigQuery setup script..."
	./scripts/setup/bigquery_setup.sh
	@echo "✅ BigQuery setup completed"

setup-bigquery-tables:
	@echo "🔧 Creating BigQuery tables..."
	source venv/bin/activate && python scripts/setup/create_bigquery_tables.py
	@echo "✅ BigQuery tables created"

test-bigquery:
	@echo "🧪 Testing BigQuery setup..."
	source venv/bin/activate && python scripts/setup/test_bigquery_setup.py
	@echo "✅ BigQuery test completed"

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
	source venv/bin/activate && python tests/integration/test_sec_download.py

# Data Commands
process-data:
	@echo "📊 Processing legal documents..."
	source venv/bin/activate && python3 scripts/data/process_documents.py

download-data:
	@echo "📥 Downloading all legal datasets..."
	source venv/bin/activate && python3 scripts/data/download_all_legal_data.py

download-sec-contracts:
	@echo "🏢 Downloading SEC contracts..."
	source venv/bin/activate && python3 scripts/data/download_sec_contracts.py

download-court-cases:
	@echo "⚖️  Downloading court cases..."
	source venv/bin/activate && python3 scripts/data/download_court_cases.py

download-legal-briefs:
	@echo "📋 Downloading legal briefs..."
	source venv/bin/activate && python3 scripts/data/download_legal_briefs.py

validate-data:
	@echo "✅ Validating data quality..."
	source venv/bin/activate && python3 scripts/data/validate_legal_data.py

test-sec-download:
	@echo "🧪 Testing SEC contracts download..."
	source venv/bin/activate && python3 tests/integration/test_sec_download.py

demo-data:
	@echo "🎭 Generating demo legal documents..."
	source venv/bin/activate && python3 scripts/data/demo_data_download.py

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
	./scripts/maintenance/cleanup.sh
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
