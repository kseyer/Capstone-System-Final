from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
import random


class Command(BaseCommand):
    help = 'Redistribute patient created_at dates from 2020-2025 for analytics'

    def handle(self, *args, **options):
        # Get all patients
        patients = User.objects.filter(user_type='patient').order_by('id')
        total_patients = patients.count()
        
        if total_patients == 0:
            self.stdout.write(self.style.WARNING('No patients found in database'))
            return
        
        self.stdout.write(f'Found {total_patients} patients')
        self.stdout.write('Redistributing created_at dates from 2020-2025...\n')
        
        # Define date ranges for each year
        year_ranges = {
            2020: (datetime(2020, 1, 1), datetime(2020, 12, 31)),
            2021: (datetime(2021, 1, 1), datetime(2021, 12, 31)),
            2022: (datetime(2022, 1, 1), datetime(2022, 12, 31)),
            2023: (datetime(2023, 1, 1), datetime(2023, 12, 31)),
            2024: (datetime(2024, 1, 1), datetime(2024, 12, 31)),
            2025: (datetime(2025, 1, 1), datetime(2025, 12, 2)),  # Up to today
        }
        
        # Distribution percentages per year (total should be 100%)
        # More patients in recent years (realistic growth pattern)
        distribution = {
            2020: 10,  # 10% of patients
            2021: 15,  # 15% of patients
            2022: 20,  # 20% of patients
            2023: 25,  # 25% of patients
            2024: 20,  # 20% of patients
            2025: 10,  # 10% of patients (current year, partial)
        }
        
        # Calculate how many patients per year
        year_counts = {}
        for year, percentage in distribution.items():
            year_counts[year] = int(total_patients * percentage / 100)
        
        # Adjust last year to account for rounding
        total_assigned = sum(year_counts.values())
        if total_assigned < total_patients:
            year_counts[2025] += (total_patients - total_assigned)
        
        # Display distribution plan
        self.stdout.write(self.style.SUCCESS('\nDistribution Plan:'))
        for year, count in year_counts.items():
            percentage = (count / total_patients) * 100
            self.stdout.write(f'  {year}: {count} patients ({percentage:.1f}%)')
        
        # Redistribute patients
        updated_count = 0
        patient_index = 0
        
        for year in sorted(year_counts.keys()):
            count = year_counts[year]
            start_date, end_date = year_ranges[year]
            
            self.stdout.write(f'\nProcessing {year}...')
            
            # Get patients for this year
            year_patients = patients[patient_index:patient_index + count]
            
            for patient in year_patients:
                # Generate random date within the year range
                days_between = (end_date - start_date).days
                random_days = random.randint(0, days_between)
                random_date = start_date + timedelta(days=random_days)
                
                # Add random time (between 8 AM and 6 PM for realism)
                random_hour = random.randint(8, 18)
                random_minute = random.randint(0, 59)
                random_datetime = random_date.replace(
                    hour=random_hour,
                    minute=random_minute,
                    second=random.randint(0, 59)
                )
                
                # Make timezone aware
                random_datetime = timezone.make_aware(random_datetime)
                
                # Update patient
                patient.created_at = random_datetime
                patient.save(update_fields=['created_at'])
                
                updated_count += 1
            
            patient_index += count
            self.stdout.write(f'  ✓ Updated {count} patients for {year}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully redistributed {updated_count} patients across 2020-2025'))
        self.stdout.write(self.style.SUCCESS('Analytics dashboard will now show historical trends!'))
