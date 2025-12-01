#!/usr/bin/env python
"""
Database Restoration Script
Restores a Django database backup (JSON format) to a target database

Usage:
    python restore_database.py backups/db_backup_YYYYMMDD_HHMMSS.json
    python restore_database.py backups/db_backup_YYYYMMDD_HHMMSS.json --database-url "postgresql://..."
"""

import os
import sys
import argparse
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    import django
    from django.conf import settings
    
    # Add project directory to path
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Set default settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
    
    django.setup()
    
    return settings

def restore_database(backup_file, database_url=None, flush=False):
    """
    Restore database from JSON backup file
    
    Args:
        backup_file: Path to JSON backup file
        database_url: Target database URL (optional, uses DATABASE_URL env var)
        flush: Whether to clear database before restoring
    """
    # Set DATABASE_URL if provided
    if database_url:
        os.environ['DATABASE_URL'] = database_url
    
    # Setup Django
    try:
        settings = setup_django()
        from django.core.management import call_command
    except Exception as e:
        print(f"✗ Error setting up Django: {e}")
        return False
    
    # Check if backup file exists
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"✗ Backup file not found: {backup_file}")
        return False
    
    print("=" * 60)
    print("Database Restoration")
    print("=" * 60)
    print(f"Backup file: {backup_path}")
    print(f"File size: {backup_path.stat().st_size / (1024 * 1024):.2f} MB")
    print()
    
    # Get database info
    db_config = settings.DATABASES['default']
    db_engine = db_config['ENGINE']
    db_name = db_config.get('NAME', 'Unknown')
    
    print(f"Target database: {db_name}")
    print(f"Database engine: {db_engine}")
    print()
    
    # Confirm before proceeding
    if flush:
        response = input("⚠️  WARNING: This will DELETE all existing data! Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Restoration cancelled.")
            return False
    
    try:
        # Flush database if requested
        if flush:
            print("Clearing existing data...")
            call_command('flush', '--no-input', verbosity=0)
            print("✓ Database cleared")
            print()
        
        # Run migrations to ensure schema is up to date
        print("Running migrations...")
        call_command('migrate', verbosity=1)
        print("✓ Migrations completed")
        print()
        
        # Restore from backup
        print("Restoring data from backup...")
        print("This may take a few minutes depending on data size...")
        print()
        
        call_command('loaddata', str(backup_path), verbosity=2)
        
        print()
        print("=" * 60)
        print("✓ Database restoration completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Restoration failed!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Restore Django database from JSON backup file'
    )
    parser.add_argument(
        'backup_file',
        help='Path to JSON backup file (e.g., backups/db_backup_20251201_014035.json)'
    )
    parser.add_argument(
        '--database-url',
        help='Target database URL (optional, uses DATABASE_URL env var)',
        default=None
    )
    parser.add_argument(
        '--flush',
        action='store_true',
        help='Clear database before restoring (WARNING: Deletes all existing data!)'
    )
    
    args = parser.parse_args()
    
    # Check if backup file exists
    if not Path(args.backup_file).exists():
        print(f"✗ Backup file not found: {args.backup_file}")
        print("\nAvailable backup files:")
        backups_dir = Path('backups')
        if backups_dir.exists():
            for backup in backups_dir.glob('db_backup_*.json'):
                print(f"  - {backup}")
        sys.exit(1)
    
    # Restore database
    success = restore_database(
        args.backup_file,
        database_url=args.database_url,
        flush=args.flush
    )
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()

