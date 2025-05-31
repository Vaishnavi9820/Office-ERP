from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import Employee
from django.db import transaction

class Command(BaseCommand):
    help = 'Links user accounts to employee records based on matching information'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Specific username to link')
        parser.add_argument('--employee-id', type=str, help='Specific employee ID to link')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    def handle(self, *args, **options):
        username = options.get('username')
        employee_id = options.get('employee_id')
        dry_run = options.get('dry_run', False)
        
        if username and employee_id:
            # Link specific user to specific employee
            self.link_specific_user_employee(username, employee_id, dry_run)
        else:
            # Auto-link all unlinked users and employees
            self.auto_link_users_employees(dry_run)

    def link_specific_user_employee(self, username, employee_id, dry_run):
        try:
            with transaction.atomic():
                # Get the specified user
                try:
                    user = User.objects.get(username=username)
                    self.stdout.write(self.style.SUCCESS(f"Found user: {user.username} (ID: {user.id})"))
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"User with username '{username}' not found."))
                    return

                # Get the specified employee record
                try:
                    employee = Employee.objects.get(eID=employee_id)
                    self.stdout.write(self.style.SUCCESS(
                        f"Found employee: {employee.firstName} {employee.lastName} (ID: {employee.eID})"
                    ))
                except Employee.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Employee with eID '{employee_id}' not found."))
                    return

                # If this is a dry run, just show what would happen
                if dry_run:
                    self.stdout.write(self.style.WARNING(
                        f"DRY RUN: Would link user '{user.username}' to employee '{employee.firstName} {employee.lastName}'"
                    ))
                    return

                # Update the employee record with the user
                employee.user = user
                employee.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully linked user '{user.username}' to employee '{employee.firstName} {employee.lastName}'"
                ))
                
                # Verify the link worked
                updated_employee = Employee.objects.get(eID=employee_id)
                if updated_employee.user and updated_employee.user.id == user.id:
                    self.stdout.write(self.style.SUCCESS("Verification successful: User and employee are now linked!"))
                else:
                    self.stdout.write(self.style.ERROR("Verification failed: User and employee are not linked."))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

    def auto_link_users_employees(self, dry_run):
        """Automatically link users to employees based on matching information"""
        try:
            # Get all users without linked employees
            users_without_employees = []
            for user in User.objects.all():
                try:
                    Employee.objects.get(user=user)
                except Employee.DoesNotExist:
                    users_without_employees.append(user)
            
            self.stdout.write(f"Found {len(users_without_employees)} users without linked employee records")
            
            # Get all employees without linked users
            employees_without_users = Employee.objects.filter(user__isnull=True)
            self.stdout.write(f"Found {employees_without_users.count()} employee records without linked users")
            
            links_made = 0
            
            # Try to match users to employees
            for user in users_without_employees:
                # First try exact match on username and eID
                try:
                    employee = employees_without_users.get(eID=user.username)
                    self.link_match(user, employee, "username=eID", dry_run)
                    links_made += 0 if dry_run else 1
                    continue
                except Employee.DoesNotExist:
                    pass
                
                # Try exact match on email
                if user.email:
                    try:
                        employee = employees_without_users.get(email__iexact=user.email)
                        self.link_match(user, employee, "email", dry_run)
                        links_made += 0 if dry_run else 1
                        continue
                    except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                        pass
                
                # Try to match on first name and last name if available
                if hasattr(user, 'first_name') and hasattr(user, 'last_name') and user.first_name and user.last_name:
                    try:
                        employee = employees_without_users.get(
                            firstName__iexact=user.first_name,
                            lastName__iexact=user.last_name
                        )
                        self.link_match(user, employee, "first_name + last_name", dry_run)
                        links_made += 0 if dry_run else 1
                        continue
                    except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                        pass
                
                # Try to match on username parts (assuming username might be in format firstname_lastname)
                username_parts = user.username.split('_')
                if len(username_parts) == 2:
                    try:
                        employee = employees_without_users.get(
                            firstName__iexact=username_parts[0],
                            lastName__iexact=username_parts[1]
                        )
                        self.link_match(user, employee, "username_parts", dry_run)
                        links_made += 0 if dry_run else 1
                        continue
                    except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                        pass
            
            # Summary
            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"DRY RUN: Would have linked {links_made} users to employees"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Successfully linked {links_made} users to employees"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during auto-linking: {str(e)}"))
    
    def link_match(self, user, employee, match_type, dry_run):
        """Helper method to link a user to an employee or log what would happen in dry run mode"""
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"DRY RUN: Would link user '{user.username}' to employee '{employee.firstName} {employee.lastName}' "
                f"(Match: {match_type})"
            ))
        else:
            employee.user = user
            employee.save()
            self.stdout.write(self.style.SUCCESS(
                f"Linked user '{user.username}' to employee '{employee.firstName} {employee.lastName}' "
                f"(Match: {match_type})"
            ))
