"""
Django management command to automatically link all users to their corresponding employee records
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import Employee
from django.db import transaction

class Command(BaseCommand):
    help = 'Links all user accounts to their corresponding employee records based on matching criteria'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting user-employee linking process..."))
        
        linked_count = 0
        already_linked_count = 0
        no_match_count = 0
        
        # Get all users
        users = User.objects.all()
        self.stdout.write(f"Found {users.count()} user accounts")
        
        # Get all employees
        employees = Employee.objects.all()
        self.stdout.write(f"Found {employees.count()} employee records")
        
        # Track which employees were linked
        linked_employees = set()
        
        with transaction.atomic():
            # First, check existing links
            for employee in employees:
                if employee.user is not None:
                    already_linked_count += 1
                    linked_employees.add(employee.eID)
                    self.stdout.write(f"  ✓ Employee '{employee.firstName} {employee.lastName}' (eID: {employee.eID}) already linked to user '{employee.user.username}'")
            
            # Process each user
            for user in users:
                # Skip if user is superuser or staff (admin users)
                if user.is_superuser or user.is_staff:
                    self.stdout.write(f"  ⚠ Skipping admin user: {user.username}")
                    continue
                
                # Skip if user already has an employee
                if Employee.objects.filter(user=user).exists():
                    continue
                
                # Try to find matching employee by email (most reliable)
                matching_by_email = None
                if user.email:
                    try:
                        matching_by_email = Employee.objects.get(email__iexact=user.email)
                        if matching_by_email.eID in linked_employees:
                            self.stdout.write(f"  ⚠ Employee with email {user.email} already linked to another user")
                            continue
                    except Employee.DoesNotExist:
                        pass
                    except Employee.MultipleObjectsReturned:
                        self.stdout.write(f"  ⚠ Multiple employees with email {user.email}")
                        continue
                
                # Try to find matching employee by name if email match wasn't found
                matching_by_name = None
                if not matching_by_email and user.first_name and user.last_name:
                    try:
                        matching_by_name = Employee.objects.get(
                            firstName__iexact=user.first_name,
                            lastName__iexact=user.last_name
                        )
                        if matching_by_name.eID in linked_employees:
                            self.stdout.write(f"  ⚠ Employee with name {user.first_name} {user.last_name} already linked to another user")
                            continue
                    except Employee.DoesNotExist:
                        pass
                    except Employee.MultipleObjectsReturned:
                        self.stdout.write(f"  ⚠ Multiple employees with name {user.first_name} {user.last_name}")
                        continue
                
                # Get the matching employee (prioritize email match over name match)
                matching_employee = matching_by_email or matching_by_name
                
                if matching_employee:
                    # Link the user to the employee
                    matching_employee.user = user
                    matching_employee.save(update_fields=['user'])
                    linked_employees.add(matching_employee.eID)
                    linked_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✓ Linked user '{user.username}' to employee '{matching_employee.firstName} {matching_employee.lastName}' (eID: {matching_employee.eID})")
                    )
                else:
                    # Special case for geeta_patil (if needed)
                    if user.username == 'geeta_patil':
                        try:
                            geeta_employee = Employee.objects.get(eID='9')
                            if geeta_employee.eID not in linked_employees:
                                geeta_employee.user = user
                                geeta_employee.save(update_fields=['user'])
                                linked_employees.add(geeta_employee.eID)
                                linked_count += 1
                                self.stdout.write(self.style.SUCCESS(
                                    f"  ✓ Linked user '{user.username}' to employee '{geeta_employee.firstName} {geeta_employee.lastName}' (eID: {geeta_employee.eID})")
                                )
                            else:
                                self.stdout.write(f"  ⚠ Employee with eID 9 already linked to another user")
                        except Employee.DoesNotExist:
                            self.stdout.write(f"  ⚠ Could not find employee record for geeta_patil with eID 9")
                    else:
                        # No matching employee found for this user
                        no_match_count += 1
                        self.stdout.write(f"  ✗ No matching employee found for user '{user.username}' ({user.email})")
        
        # Report results
        self.stdout.write(self.style.SUCCESS(f"\nSummary:"))
        self.stdout.write(f"  • {already_linked_count} employees were already linked to users")
        self.stdout.write(f"  • {linked_count} new user-employee links were created")
        self.stdout.write(f"  • {no_match_count} users had no matching employee records")
        
        self.stdout.write(self.style.SUCCESS("\nProcess complete. You can now log in with any user account that has a linked employee record."))
