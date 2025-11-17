#!/usr/bin/env bash
set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Current directory: $(pwd) ==="
echo "=== Installing Python dependencies ==="
pip install -r backend/requirements.txt

echo "=== Initializing production database (non-blocking if DB not ready) ==="
cd backend && python init_db_production.py || true

echo "=== Build script completed ==="


