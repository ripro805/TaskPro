#!/usr/bin/env bash
# Manual build script (Vercel runs api/index.py directly; this is here for parity).
set -euo pipefail
pip install --no-cache-dir -r requirements.txt
python manage.py collectstatic --noinput
