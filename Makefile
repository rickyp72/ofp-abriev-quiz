.DEFAULT_GOAL := help
VENV         := .venv
PYTHON       := $(VENV)/bin/python
PIP          := $(VENV)/bin/pip

.PHONY: help install run test docker-up docker-down clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --quiet -r requirements.txt
	$(PIP) install --quiet pytest

install: $(VENV)/bin/activate ## Create venv and install dependencies

run: install ## Run the Flask dev server on http://localhost:8080
	$(PYTHON) app.py

test: install ## Run the test suite
	$(PYTHON) -m pytest tests/ -v

docker-up: ## Build and start the app in Docker
	docker compose up --build -d

docker-down: ## Stop and remove the Docker containers
	docker compose down

clean: ## Remove the virtual environment and cache files
	rm -rf $(VENV) __pycache__ tests/__pycache__ .pytest_cache
