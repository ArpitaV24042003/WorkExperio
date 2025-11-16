#!/usr/bin/env bash
set -euo pipefail

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Initializing production database (non-blocking if DB not ready) ==="
python backend/init_db_production.py || true

echo "=== Build script completed ==="


