#!/usr/bin/env bash
set -euo pipefail

echo "=== Installing Python dependencies ==="
pip install -r backend/requirements.txt

echo "=== Initializing production database (non-blocking if DB not ready) ==="
cd backend && python init_db_production.py || true

echo "=== Build script completed ==="


