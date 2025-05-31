from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import Employee
from datetime import date

class Command(BaseCommand):
    help = 'Creates an employee record for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to create employee record for')
        parser.add_argument('--eid', type=str, help='Employee ID', required=True)
        parser.add_argument('--first-name', type=str, help='First name', required=True)
        parser.add_argument('--last-name', type=str, help='Last name', required=True)
        parser.add_argument('--email', type=str, help='Email address', required=True)
        parser.add_argument('--phone', type=str, help='Phone number', required=True)
        parser.add_argument('--designation', type=str, help='Designation', required=True)
        parser.add_argument('--salary', type=str, help='Salary', required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['username'])
            
            # Check if employee record already exists
            if hasattr(user, 'employee'):
                self.stdout.write(self.style.WARNING(f'Employee record already exists for user {user.username}'))
                return

            # Create employee record
            employee = Employee.objects.create(
                user=user,
                eID=options['eid'],
                firstName=options['first_name'],
                middleName='',  # Optional
                lastName=options['last_name'],
                email=options['email'],
                phoneNo=options['phone'],
                designation=options['designation'],
                salary=options['salary'],
                joinDate=date.today(),  # Set to today's date
                dOB=date.today(),  # Set to today's date as placeholder
                addharNo='000000000000'  # Set a placeholder value
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created employee record for user {user.username}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {options["username"]} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating employee record: {str(e)}')) 