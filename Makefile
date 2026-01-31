.PHONY: install dev test lint format clean help

help:
	@echo "AI Boundary Engine - Development Commands"
	@echo ""
	@echo "  install     Install package"
	@echo "  dev         Install package with dev dependencies"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code"
	@echo "  clean       Clean build artifacts"
	@echo "  example     Run example usage"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=boundary_engine --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/ examples/
	ruff check --fix src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

example:
	python examples/usage_examples.py
