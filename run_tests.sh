#!/bin/bash
# Test runner script with coverage

# Activate virtual environment
source env-libcst/bin/activate

# Run tests with coverage
echo "Running tests with coverage..."
pytest --cov=libcst_analysis_tools --cov-report=html --cov-report=term-missing tests/ "$@"

# Show coverage summary
echo ""
echo "Coverage report generated in htmlcov/index.html"
echo "Open with: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"
