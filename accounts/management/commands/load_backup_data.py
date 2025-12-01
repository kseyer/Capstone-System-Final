"""
Django management command to load backup data from JSON file
This can be triggered automatically on Render deployment
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path


class Command(BaseCommand):
    help = 'Load backup data from JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-file',
            type=str,
            default='backups/db_backup_for_render.json',
            help='Path to the backup JSON file'
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush database before loading (WARNING: deletes all data)'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        flush = options['flush']
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS('Database Restoration from Backup'))
        self.stdout.write("=" * 60)
        
        # Check if backup file exists
        backup_path = Path(backup_file)
        if not backup_path.exists():
            self.stdout.write(self.style.ERROR(f'✗ Backup file not found: {backup_file}'))
            return
        
        self.stdout.write(f"Backup file: {backup_path}")
        self.stdout.write(f"File size: {backup_path.stat().st_size / 1024:.2f} KB")
        self.stdout.write("")
        
        try:
            # Flush database if requested
            if flush:
                self.stdout.write("Clearing existing data...")
                call_command('flush', '--no-input', verbosity=0)
                self.stdout.write(self.style.SUCCESS('✓ Database cleared'))
                self.stdout.write("")
            
            # Run migrations to ensure schema is up to date
            self.stdout.write("Running migrations...")
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            self.stdout.write("")
            
            # Load backup data
            self.stdout.write("Loading backup data...")
            self.stdout.write("This may take a few minutes...")
            self.stdout.write("")
            
            call_command('loaddata', str(backup_path), verbosity=2)
            
            self.stdout.write("")
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.SUCCESS('✓ Database restoration completed successfully!'))
            self.stdout.write("=" * 60)
            
        except Exception as e:
            self.stdout.write("")
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.ERROR('✗ Restoration failed!'))
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            import traceback
            traceback.print_exc()
