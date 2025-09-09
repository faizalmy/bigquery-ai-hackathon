#!/bin/bash

# Cleanup Script for Legal Document Intelligence Platform
# Removes temporary files, cache files, and logs

set -e

echo "🧹 Cleaning up temporary files and cache..."
echo "============================================="

# Remove Python cache files
echo "Removing Python cache files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true

# Remove log files (but keep the directory)
echo "Removing log files..."
find logs/ -name "*.log" -delete 2>/dev/null || true

# Remove any test output files
echo "Removing test output files..."
find . -name "test_*.json" -delete 2>/dev/null || true
find . -name "test_*.csv" -delete 2>/dev/null || true

echo ""
echo "✅ Cleanup completed successfully!"
echo ""
echo "📋 What was cleaned:"
echo "  - Python cache files (*.pyc, __pycache__)"
echo "  - Temporary files (*.tmp, *.temp, *.bak, *~)"
echo "  - Log files (logs/*.log)"
echo "  - Test output files (test_*.json, test_*.csv)"
echo ""
echo "💡 To run this cleanup again: ./scripts/maintenance/cleanup.sh"
