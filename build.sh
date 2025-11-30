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

# Restore from backup if backup file exists
if [ -f "backups/db_backup_20251120_024926.sqlite3" ]; then
    echo "Backup file found. Restoring from backup..."
    python manage.py restore_from_sqlite --backup-file backups/db_backup_20251120_024926.sqlite3 || {
        echo "Warning: Backup restore had issues, will try sample data instead..."
        python manage.py populate_data --force || true
    }
    echo "Backup restoration completed."
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


