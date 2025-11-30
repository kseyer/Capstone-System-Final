#!/usr/bin/env python
"""
Helper script to fix migration issues when tables already exist.
This is run during the build process to handle partial migrations.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [table_name])
        elif connection.vendor == 'sqlite':
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?;
            """, [table_name])
            return cursor.fetchone() is not None
        else:
            # For other databases, try a generic approach
            tables = connection.introspection.table_names(cursor)
            return table_name in tables
        
        if connection.vendor == 'postgresql':
            return cursor.fetchone()[0]
    return False

def fix_migrations():
    """Fix migrations by fake-applying ones where tables already exist."""
    # Check if treatments table exists
    if table_exists('treatments'):
        print("⚠️  'treatments' table already exists")
        print("   Attempting to fake-apply migration 0013...")
        try:
            call_command('migrate', 'appointments', '0013', '--fake', verbosity=1)
            print("   ✓ Migration 0013 fake-applied successfully")
        except Exception as e:
            print(f"   ⚠️  Could not fake-apply: {e}")
            # Continue anyway - the table exists, so we'll try to migrate normally
    
    # Now run normal migrations
    print("\n🔄 Running normal migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = fix_migrations()
    sys.exit(0 if success else 1)

