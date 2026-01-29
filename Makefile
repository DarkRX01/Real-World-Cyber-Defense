# Cyber Defense - Development Makefile
# Usage: make <target>

.PHONY: help install install-dev test lint format build clean run

# Default target
help:
	@echo "Cyber Defense - Development Commands"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run unit tests"
	@echo "  lint         Run linter (ruff)"
	@echo "  format       Format code with ruff"
	@echo "  typecheck    Run type checker (mypy)"
	@echo "  build        Build Windows EXE"
	@echo "  clean        Remove build artifacts"
	@echo "  run          Run the application"
	@echo ""

# Install production dependencies
install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

# Install development dependencies
install-dev:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt

# Run tests
test:
	python -m pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Run linter
lint:
	python -m ruff check .

# Format code
format:
	python -m ruff format .
	python -m ruff check --fix .

# Type checking
typecheck:
	python -m mypy app_main.py threat_engine.py background_service.py

# Build Windows EXE
build:
	python build-safe-exe.py

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -f *.spec
	rm -f version_info.txt
	rm -f test-exe.bat

# Run the application
run:
	python app_main.py

# Run the test script
check:
	python test-app.py

# Create source distribution
dist:
	python -m build --sdist

# All checks (lint, typecheck, test)
all-checks: lint typecheck test
	@echo "All checks passed!"
