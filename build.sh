#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process..."

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --no-input --clear

# Run migrations
echo "Running migrations..."
python3 manage.py migrate --no-input

echo "Build completed successfully!"
