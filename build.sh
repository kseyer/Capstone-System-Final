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

# Create superuser if it doesn't exist (non-interactive)
python manage.py create_superuser || true

# Populate database with initial data
# Using --force to ensure data is populated (will skip if already exists due to get_or_create)
echo "Populating database with initial data..."
python manage.py populate_data --force || {
    echo "Warning: Data population had issues, but continuing..."
    # Try without force as fallback
    python manage.py populate_data --check-empty || true
}
echo "Data population completed."


