#!/usr/bin/env bash
# One-time patient population script for Render

echo "Running database migrations..."
python manage.py migrate

echo "Populating patient data..."
python manage.py populate_patient_names

echo "Patient population complete!"
