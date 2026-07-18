# cumplo-common

## Overview
Shared domain library that centralizes core logic for the Cumplo API project. Published as a
private package to Google Cloud Artifact Registry and consumed by the Cumplo Cloud Run
services (orchestrator, herald, spotter, tailor, accountant).

## Build & Test
- Install deps: `poetry install`
- Run tests: `poetry run pytest`
- Auto-fix lint + format: `make format`
- Verify code quality (CI gate): `make lint`
- Full local CI simulation (lint + tests): `make check`
- Build artifacts: `make build`

Python 3.13, Poetry 2.4.x. Tests need no secrets — `tests/conftest.py` injects a test Fernet key.

## Releasing (CI/CD)
Releases are automated. **The version lives in exactly one place: `pyproject.toml`.**
`cumplo_common/__init__.py` derives `__version__` from installed metadata — never hardcode it.

To cut a release:
1. On your branch: `make bump PART=patch|minor|major` (bumps `pyproject.toml`).
2. Open a PR, get it reviewed and merged (see Git workflow below).
3. On merge to `master`, `.github/workflows/release.yml` builds and publishes **only if that
   version isn't already in the registry** (idempotent — non-release merges safely no-op),
   then creates the matching bare-numeric git tag + GitHub Release.

- `.github/workflows/ci.yml` runs `make lint` (ruff / basedpyright / docformatter) + pytest on every PR (required check).
- Auth to Artifact Registry is **keyless** via Workload Identity Federation (repo-scoped OIDC
  → `cumplo-pypi` service account). No keys or secrets are stored in GitHub.
- Registry: `cumplo-pypi` (Python) in `us-central1`, project `cumplo-scraper`.

## Git workflow
- Branch prefixes: `feat/`, `fix/`, `chore/`, `ci/`. Conventional-commit subjects (`feat:`, `fix:`, …).
- `master` is protected by the `not-cumplo-audit-gate` ruleset: every change needs a **PR +
  code-owner review** (`@cnsfeir-reviewer`); only org admins can bypass. **Never push to
  `master` directly** — it is rejected. Open a PR.

## Gotchas
- **Published versions are immutable.** Artifact Registry refuses to overwrite an existing
  version — always `make bump` before releasing; you can't republish a number.
- **twine must stay ≥ 6.1.** Poetry 2.x emits Metadata-Version 2.4 wheels that older twine
  can't parse (fails with a misleading "missing Name, Version"). Don't downgrade it.
- **Manual publish is rarely needed** (CI handles it). If you must: `gcloud auth
  application-default login`, then `make build && make publish`.
- The devcontainer builds with a gitignored `cumplo_pypi_credentials.json` SA key to *pull*
  the package locally; CI does not use it (WIF instead).

## Before committing
- [ ] Run `make format`, then `make lint` and ensure it passes.
- [ ] Version bumped (`make bump`) if this change should trigger a release.
- [ ] No secrets or credential files committed.
