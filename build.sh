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

# Restore from JSON backup if it exists (for Render PostgreSQL)
if [ -f "backups/db_backup_for_render.json" ]; then
    echo "JSON backup file found. Restoring from backup..."
    python manage.py load_backup_data --backup-file backups/db_backup_for_render.json || {
        echo "Warning: Backup restore had issues, will try sample data instead..."
        python manage.py populate_data --force || true
    }
    echo "Backup restoration completed."
elif [ -f "backups/db_backup_20251120_024926.sqlite3" ]; then
    echo "SQLite backup file found (not compatible with PostgreSQL)."
    echo "Please convert to JSON format first."
    echo "Populating with sample data instead..."
    python manage.py populate_data --force || true
else
    echo "No backup file found. Populating with sample data..."
    # Populate database with initial data
    # Using --force to ensure data is populated (will skip if already exists due to get_or_create)
    python manage.py populate_data --force || {
        echo "Warning: Data population had issues, but continuing..."
        # Try without force as fallback
        python manage.py populate_data --check-empty || true
    }
    echo "Data population completed."
fi

# Limit patients to 500 to prevent system slowdown
echo "Limiting patients to 500 for optimal performance..."
python manage.py limit_patients --max=500 || {
    echo "Warning: Patient limit command had issues..."
}
echo "Patient limit check completed."

# Randomize patient creation dates (preserve recent registrations)
echo "Randomizing patient creation dates..."
python manage.py randomize_patient_dates || {
    echo "Warning: Date randomization had issues..."
}
echo "Patient date randomization completed."
