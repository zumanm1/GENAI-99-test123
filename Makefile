.PHONY: install test run clean lint format

# Virtual environment and dependencies
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

# Development dependencies
install-dev:
	pip install pytest pytest-asyncio httpx

# Run tests
test:
	pytest tests/ -v

# Run the application
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f test.db

# Lint code
lint:
	flake8 app/ tests/

# Format code
format:
	black app/ tests/

# Database migrations
migrate:
	python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Run development server with database setup
dev: migrate run

# Check code quality
check: lint test

# Build production
build:
	docker build -t network-automation-platform .

# Help
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  test        - Run tests"
	@echo "  run         - Run the application"
	@echo "  clean       - Clean up temporary files"
	@echo "  lint        - Lint code"
	@echo "  format      - Format code"
	@echo "  migrate     - Run database migrations"
	@echo "  dev         - Run development server with DB setup"
	@echo "  check       - Run lint and tests"
	@echo "  build       - Build Docker image"
