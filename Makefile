-include .env
export

# Runs linters
.PHONY: lint
lint:
	@ruff check --fix
	@ruff format
	@mypy --config-file pyproject.toml .

# Runs the same quality gates as CI, non-mutating (local pre-flight)
.PHONY: check
check:
	@poetry run ruff check .
	@poetry run ruff format --check .
	@poetry run mypy --config-file pyproject.toml .
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
