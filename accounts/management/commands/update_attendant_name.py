"""
Django management command to update attendant name from "Kranchy Reyes" to "Jillian Ynares"
Run: python manage.py update_attendant_name
"""
from django.core.management.base import BaseCommand
from accounts.models import Attendant, User


class Command(BaseCommand):
    help = 'Update attendant name from "Kranchy Reyes" to "Jillian Ynares"'

    def handle(self, *args, **options):
        # Update Attendant model
        try:
            attendant = Attendant.objects.get(
                first_name='Kranchy',
                last_name='Reyes'
            )
            old_name = f"{attendant.first_name} {attendant.last_name}"
            attendant.first_name = 'Jillian'
            attendant.last_name = 'Ynares'
            attendant.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated Attendant: {old_name} -> {attendant.first_name} {attendant.last_name}')
            )
        except Attendant.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Attendant "Kranchy Reyes" not found in Attendant model')
            )
        except Attendant.MultipleObjectsReturned:
            # Update all matching attendants
            attendants = Attendant.objects.filter(
                first_name='Kranchy',
                last_name='Reyes'
            )
            for attendant in attendants:
                attendant.first_name = 'Jillian'
                attendant.last_name = 'Ynares'
                attendant.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated {attendants.count()} Attendant(s): Kranchy Reyes -> Jillian Ynares')
            )
        
        # Update User model if there's a matching attendant user
        try:
            user = User.objects.get(
                user_type='attendant',
                first_name='Kranchy',
                last_name='Reyes'
            )
            old_name = f"{user.first_name} {user.last_name}"
            user.first_name = 'Jillian'
            user.last_name = 'Ynares'
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated User: {old_name} -> {user.first_name} {user.last_name}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('User "Kranchy Reyes" not found in User model')
            )
        except User.MultipleObjectsReturned:
            # Update all matching users
            users = User.objects.filter(
                user_type='attendant',
                first_name='Kranchy',
                last_name='Reyes'
            )
            for user in users:
                user.first_name = 'Jillian'
                user.last_name = 'Ynares'
                user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated {users.count()} User(s): Kranchy Reyes -> Jillian Ynares')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\nAttendant name update complete!')
        )

