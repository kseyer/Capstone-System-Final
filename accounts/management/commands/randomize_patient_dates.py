"""
Django management command to randomize patient creation dates
This makes the patient list more realistic by spreading dates across 2020-2025
Recent patients (last 7 days) are excluded to keep new registrations authentic
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Randomize patient creation dates (excludes recent registrations)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-recent',
            type=int,
            default=7,
            help='Number of days to consider as recent (default: 7)',
        )
        parser.add_argument(
            '--start-year',
            type=int,
            default=2020,
            help='Start year for randomization (default: 2020)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing',
        )

    def handle(self, *args, **options):
        days_recent = options['days_recent']
        start_year = options['start_year']
        dry_run = options['dry_run']
        
        # Calculate cutoff date for "recent" patients
        cutoff_date = timezone.now() - timedelta(days=days_recent)
        
        # Get patients that are NOT recent (created before cutoff)
        old_patients = User.objects.filter(
            user_type='patient',
            created_at__lt=cutoff_date,
            archived=False
        )
        
        # Get recent patients count for info
        recent_patients = User.objects.filter(
            user_type='patient',
            created_at__gte=cutoff_date,
            archived=False
        )
        
        self.stdout.write(f'Found {old_patients.count()} old patients to randomize')
        self.stdout.write(f'Found {recent_patients.count()} recent patients to preserve')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
            for patient in old_patients[:5]:
                new_date = self._generate_random_date(start_year)
                self.stdout.write(
                    f'Would change {patient.full_name}: {patient.created_at} -> {new_date}'
                )
            if old_patients.count() > 5:
                self.stdout.write(f'... and {old_patients.count() - 5} more')
            return
        
        # Randomize dates for old patients
        updated_count = 0
        for patient in old_patients:
            # Generate random date between start_year and today (but not recent)
            new_date = self._generate_random_date(start_year, cutoff_date)
            patient.created_at = new_date
            patient.save(update_fields=['created_at'])
            updated_count += 1
            
            if updated_count % 50 == 0:
                self.stdout.write(f'Updated {updated_count} patients...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully randomized {updated_count} patient dates'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Preserved {recent_patients.count()} recent patients with original dates'
            )
        )

    def _generate_random_date(self, start_year, end_date=None):
        """Generate a random datetime between start_year and end_date"""
        if end_date is None:
            end_date = timezone.now()
        
        start_date = timezone.make_aware(datetime(start_year, 1, 1))
        
        # Calculate time difference in seconds
        time_between = (end_date - start_date).total_seconds()
        
        # Generate random offset
        random_offset = random.randint(0, int(time_between))
        
        # Generate random date
        random_date = start_date + timedelta(seconds=random_offset)
        
        return random_date
