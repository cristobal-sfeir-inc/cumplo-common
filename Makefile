-include .env
export

# Verifies code quality — check-only, no fixes (same command as CI)
.PHONY: lint
lint:
	@poetry run ruff check --no-fix .
	@poetry run ruff format --check .
	@poetry run basedpyright
	@poetry run docformatter --check --recursive .

# Applies all auto-fixes (ruff + docformatter)
.PHONY: format
format:
	@poetry run ruff format .
	@poetry run ruff check --fix .
	@poetry run docformatter --in-place --recursive .

# Runs the full local CI gate (lint + tests)
.PHONY: check
check:
	@make lint
	@poetry run pytest

# Bumps the version (single source of truth: pyproject.toml). Usage: make bump PART=patch|minor|major
PART ?= patch
.PHONY: bump
bump:
	@poetry version $(PART)
	@echo "Bumped to $$(poetry version -s) — commit, open a PR; publish happens automatically on merge to master."


# Builds the library
.PHONY: build
build:
	@rm -rf dist
	@poetry build

# Starts the API server
.PHONY: publish
publish:
	@poetry run twine upload --verbose --repository-url https://us-central1-python.pkg.dev/cumplo-scraper/cumplo-pypi/ dist/*

# Logs into Google Cloud
.PHONY: login
login:
	@gcloud config configurations activate $(PROJECT_ID)
	@gcloud auth application-default login

.PHONY: unit
unit:
	@set -o allexport; source .env; set +o allexport
	@pytest tests/unit
