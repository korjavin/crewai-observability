# Makefile for the crewAI Scheduling Assistant

# Phony targets do not correspond to files
.PHONY: all install test test-unit test-integration test-coverage lint fmt security-scan build clean help

# Default target
all: help

# Dependency management
install:
	@echo "--> Installing dependencies with Poetry..."
	@poetry install

# Testing commands
test: test-unit test-integration
	@echo "--> Running all tests..."

test-unit:
	@echo "--> Running unit tests..."
	@poetry run pytest tests/unit

test-integration:
	@echo "--> Running integration tests..."
	@poetry run pytest tests/integration

test-coverage:
	@echo "--> Running tests and generating coverage report..."
	@poetry run pytest --cov=src --cov-report=html --cov-report=xml

# Quality and formatting commands
lint:
	@echo "--> Linting with flake8..."
	@poetry run flake8 src tests

fmt:
	@echo "--> Formatting with black..."
	@poetry run black src tests

# Security commands
security-scan:
	@echo "--> Scanning for security vulnerabilities with safety..."
	@poetry run safety check

# Build and clean commands
build:
	@echo "--> No build step required for this project."

clean:
	@echo "--> Cleaning up temporary files..."
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -f .coverage
	@rm -rf htmlcov/
	@rm -f coverage.xml

# Help command
help:
	@echo "Available commands:"
	@echo "  install          - Install project dependencies"
	@echo "  test             - Run all tests (unit and integration)"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage    - Run tests and generate a coverage report"
	@echo "  lint             - Check code for style issues with flake8"
	@echo "  fmt              - Format code with black"
	@echo "  security-scan    - Scan for security vulnerabilities"
	@echo "  build            - (No-op) Placeholder for build process"
	@echo "  clean            - Remove temporary and build files"
