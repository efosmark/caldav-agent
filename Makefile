.PHONY: help venv install lint test clean

help:
	@echo "Available targets:"
	@echo "  venv     - Create virtual environment"
	@echo "  install  - Install dependencies"
	@echo "  lint     - Run linter (flake8)"
	@echo "  test     - Run tests (pytest)"
	@echo "  clean    - Remove build artifacts"

venv:
	python3 -m venv .venv

install: venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

lint:
	venv/bin/flake8 .

test:
	venv/bin/pytest

clean:
	rm -rf .venv __pycache__ .pytest_cache *.pyc *.pyo .mypy_cache dist build