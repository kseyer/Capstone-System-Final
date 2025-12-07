#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Build Process Started ==="

# Upgrade pip
echo "Step 1: Upgrading pip..."
python3 -m pip install --upgrade pip || pip install --upgrade pip

# Install dependencies
echo "Step 2: Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Collect static files (with fallback for missing files)
echo "Step 3: Collecting static files..."
python manage.py collectstatic --no-input --clear || python manage.py collectstatic --no-input

# Run migrations
echo "Step 4: Running database migrations..."
python manage.py migrate --no-input

echo "=== Build Process Completed Successfully ==="
