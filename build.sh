#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations with error handling for existing tables
# This handles cases where previous deployment attempts partially succeeded
python manage.py migrate || {
    echo "Migration failed, attempting to fix existing tables..."
    python fix_migrations.py || python manage.py migrate
}


