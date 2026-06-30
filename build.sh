#!/usr/bin/env bash
# Render build script.
# Runs on every deploy: installs deps, builds static files, applies DB migrations.
set -o errexit

echo "==> Upgrading pip"
pip install --upgrade pip

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Build complete"