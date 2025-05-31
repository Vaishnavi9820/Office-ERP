from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import Employee
from django.db import transaction

class Command(BaseCommand):
    help = 'Links a user account to an employee record'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get the user with username 'geeta_patil'
                try:
                    user = User.objects.get(username='geeta_patil')
                    self.stdout.write(self.style.SUCCESS(f"Found user: {user.username} (ID: {user.id})"))
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"User with username 'geeta_patil' not found."))
                    return

                # Get the employee record with eID '9'
                try:
                    employee = Employee.objects.get(eID='9')
                    self.stdout.write(self.style.SUCCESS(
                        f"Found employee: {employee.firstName} {employee.lastName} (ID: {employee.eID})"
                    ))
                except Employee.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Employee with eID '9' not found."))
                    return

                # Update the employee record with the user
                employee.user = user
                employee.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully linked user '{user.username}' to employee '{employee.firstName} {employee.lastName}'"
                ))
                
                # Verify the link worked
                updated_employee = Employee.objects.get(eID='9')
                if updated_employee.user and updated_employee.user.id == user.id:
                    self.stdout.write(self.style.SUCCESS("Verification successful: User and employee are now linked!"))
                else:
                    self.stdout.write(self.style.ERROR("Verification failed: User and employee are not linked."))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
