#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Starting Build ==="

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Collect static files (ignore errors for missing files)
echo "Collecting static files..."
python manage.py collectstatic --no-input 2>&1 || echo "Collectstatic warnings ignored"

# Run migrations
echo "Running migrations..."
python manage.py migrate --no-input

echo "=== Build Complete ==="
