#!/usr/bin/env bash
# init_repo.sh — scaffold the israel-semicon-db project structure

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Top-level directories
mkdir -p "$ROOT/src/db"
mkdir -p "$ROOT/src/pipelines"
mkdir -p "$ROOT/src/matching"
mkdir -p "$ROOT/src/api/routes"
mkdir -p "$ROOT/notebooks"
mkdir -p "$ROOT/tests"
mkdir -p "$ROOT/scripts/output"

# __init__.py in every src subfolder so Python treats them as packages
touch "$ROOT/src/__init__.py"
touch "$ROOT/src/db/__init__.py"
touch "$ROOT/src/pipelines/__init__.py"
touch "$ROOT/src/matching/__init__.py"
touch "$ROOT/src/api/__init__.py"
touch "$ROOT/src/api/routes/__init__.py"

# Stub source files
touch "$ROOT/src/db/base.py"
touch "$ROOT/src/db/session.py"
touch "$ROOT/src/db/models.py"
touch "$ROOT/src/pipelines/iia_pipeline.py"
touch "$ROOT/src/pipelines/registrar_scraper.py"
touch "$ROOT/src/pipelines/patent_pipeline.py"
touch "$ROOT/src/matching/entity_resolver.py"
touch "$ROOT/src/api/main.py"

# Placeholder notebook and test
touch "$ROOT/notebooks/session_0_1.ipynb"
touch "$ROOT/tests/__init__.py"
touch "$ROOT/tests/test_placeholder.py"

# Keep scripts/output in git via .gitkeep (output/ is gitignored)
touch "$ROOT/scripts/output/.gitkeep"

echo "Repo structure created"
