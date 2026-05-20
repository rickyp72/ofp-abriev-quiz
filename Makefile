.DEFAULT_GOAL := help
VENV         := .venv
PYTHON       := $(VENV)/bin/python
PIP          := $(VENV)/bin/pip

.PHONY: help install run test docker-up docker-down clean tf-init tf-plan tf-apply tf-destroy get-public-ip get-ssh-key ssh-to-host

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

tf-init: ## Initialise Terraform (run once)
	cd terraform && terraform init

tf-plan: ## Preview infrastructure changes
	cd terraform && terraform plan

tf-apply: ## Create / update infrastructure on AWS
	cd terraform && terraform apply

tf-destroy: ## Tear down all AWS infrastructure
	cd terraform && terraform destroy

get-public-ip: ## Print the public IP from Terraform
	terraform -chdir=terraform output -raw public_ip

get-ssh-key: ## Save the SSH private key to ~/.ssh/ofp-quiz.pem
	rm -f ~/.ssh/ofp-quiz.pem && terraform -chdir=terraform output -raw private_key > ~/.ssh/ofp-quiz.pem && chmod 400 ~/.ssh/ofp-quiz.pem

ssh-to-host: get-ssh-key ## SSH onto the Lightsail instance
	ssh -i ~/.ssh/ofp-quiz.pem ec2-user@$$(terraform -chdir=terraform output -raw public_ip)