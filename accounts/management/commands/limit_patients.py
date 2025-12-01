"""
Django management command to limit the number of patients to prevent system slowdown
Run: python manage.py limit_patients --max=700
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from appointments.models import Appointment
from analytics.models import PatientAnalytics, PatientSegment


class Command(BaseCommand):
    help = 'Limit the number of patients to prevent system slowdown'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max',
            type=int,
            default=700,
            help='Maximum number of patients to keep (default: 700)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        max_patients = options['max']
        dry_run = options['dry_run']
        
        self.stdout.write(f'Limiting patients to {max_patients}...')
        
        # Get all patients excluding test users and important users
        test_patient_names = ['Hyro', 'Jenelyn', 'Ellen', 'Ryk', 'Dave', 'Evangeline']
        test_last_names = ['Ybut', 'Sinamay', 'Dio', 'Mamalias', 'Balazuela']
        important_users = ['maria.santos', 'admin', 'owner', 'attendant', 'ken', 'kurtzy', 'jrmurbano']
        
        # Get all patients
        all_patients = User.objects.filter(
            user_type='patient',
            archived=False
        ).exclude(
            first_name__in=test_patient_names
        ).exclude(
            last_name__in=test_last_names
        ).exclude(
            username__in=important_users
        ).order_by('-date_joined')  # Keep most recent patients
        
        current_count = all_patients.count()
        self.stdout.write(f'Current patient count: {current_count}')
        
        if current_count <= max_patients:
            self.stdout.write(
                self.style.SUCCESS(f'Patient count is already within limit ({current_count} <= {max_patients})')
            )
            return
        
        # Calculate how many to remove
        to_remove_count = current_count - max_patients
        self.stdout.write(
            self.style.WARNING(f'Need to remove {to_remove_count} patients')
        )
        
        # Get patients to remove (oldest first, keeping recent ones)
        patients_to_remove = all_patients.reverse()[:to_remove_count]
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN - No changes will be made')
            )
            self.stdout.write(f'Would remove {patients_to_remove.count()} patients:')
            for patient in patients_to_remove[:10]:
                self.stdout.write(f'  - {patient.username} ({patient.full_name})')
            if patients_to_remove.count() > 10:
                self.stdout.write(f'  ... and {patients_to_remove.count() - 10} more')
            return
        
        # Confirm deletion
        self.stdout.write(
            self.style.WARNING(f'This will permanently delete {patients_to_remove.count()} patients and their related data!')
        )
        
        # Delete patients and related data
        with transaction.atomic():
            deleted_count = 0
            for patient in patients_to_remove:
                # Delete related appointments
                appointment_count = Appointment.objects.filter(patient=patient).count()
                
                # Delete related analytics
                PatientAnalytics.objects.filter(patient=patient).delete()
                PatientSegment.objects.filter(patient=patient).delete()
                
                # Delete appointments
                Appointment.objects.filter(patient=patient).delete()
                
                # Delete the patient
                patient.delete()
                deleted_count += 1
                
                if deleted_count % 100 == 0:
                    self.stdout.write(f'Deleted {deleted_count} patients...')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully removed {deleted_count} patients')
            )
        
        # Show final count
        final_count = User.objects.filter(user_type='patient', archived=False).count()
        self.stdout.write(
            self.style.SUCCESS(f'Final patient count: {final_count}')
        )
