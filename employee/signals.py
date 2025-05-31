# employee/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employee
import logging

# Set up logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def link_user_to_employee(sender, instance, created, **kwargs):
    """
    When a user is created or updated, try to link it to an existing employee record
    based on matching criteria.
    """
    try:
        # Skip if the user is already linked to an employee
        try:
            if hasattr(instance, 'employee'):
                logger.info(f"User {instance.username} already linked to employee {instance.employee.eID}")
                return
        except Employee.DoesNotExist:
            pass
            
        # Try different matching strategies
        employee_found = False
        
        # 1. Try to match by username and eID
        try:
            employee = Employee.objects.get(eID=instance.username)
            employee_found = True
            logger.info(f"Found employee match by eID: {employee.eID}")
        except Employee.DoesNotExist:
            pass
        
        # 2. Try to match by email
        if not employee_found and instance.email:
            try:
                employee = Employee.objects.get(email__iexact=instance.email)
                employee_found = True
                logger.info(f"Found employee match by email: {employee.email}")
            except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                pass
        
        # 3. Try to match by first name and last name
        if not employee_found and instance.first_name and instance.last_name:
            try:
                employee = Employee.objects.get(
                    firstName__iexact=instance.first_name,
                    lastName__iexact=instance.last_name
                )
                employee_found = True
                logger.info(f"Found employee match by name: {employee.firstName} {employee.lastName}")
            except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                pass
        
        # 4. Try to match by username parts (assuming username might be in format firstname_lastname)
        if not employee_found:
            username_parts = instance.username.split('_')
            if len(username_parts) == 2:
                try:
                    employee = Employee.objects.get(
                        firstName__iexact=username_parts[0],
                        lastName__iexact=username_parts[1]
                    )
                    employee_found = True
                    logger.info(f"Found employee match by username parts: {employee.firstName} {employee.lastName}")
                except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                    pass
        
        # If we found a matching employee, link it to the user
        if employee_found:
            # Make sure the employee isn't already linked to another user
            if employee.user is None:
                employee.user = instance
                employee.save()
                logger.info(f"Linked user {instance.username} to employee {employee.eID}")
            elif employee.user.id == instance.id:
                # Already linked to this user (shouldn't happen, but just in case)
                logger.info(f"User {instance.username} already correctly linked to employee {employee.eID}")
            else:
                # Employee is linked to a different user - this is a conflict
                logger.warning(f"Employee {employee.eID} already linked to different user {employee.user.username}")
    except Exception as e:
        logger.error(f"Error in link_user_to_employee signal: {str(e)}")

@receiver(post_save, sender=Employee)
def link_employee_to_user(sender, instance, created, **kwargs):
    """
    When an employee is created or updated, try to link it to an existing user
    based on matching criteria if it doesn't already have a user.
    """
    try:
        # Skip if the employee already has a user
        if instance.user is not None:
            return
            
        user_found = False
        
        # 1. Try to match by eID and username
        try:
            user = User.objects.get(username=instance.eID)
            user_found = True
            logger.info(f"Found user match by username=eID: {user.username}")
        except User.DoesNotExist:
            pass
        
        # 2. Try to match by email
        if not user_found:
            try:
                user = User.objects.get(email__iexact=instance.email)
                user_found = True
                logger.info(f"Found user match by email: {user.email}")
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass
        
        # 3. Try to match by first name and last name
        if not user_found:
            try:
                user = User.objects.get(
                    first_name__iexact=instance.firstName,
                    last_name__iexact=instance.lastName
                )
                user_found = True
                logger.info(f"Found user match by name: {user.first_name} {user.last_name}")
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass
        
        # 4. Try to match by constructing a username from firstName_lastName
        if not user_found:
            constructed_username = f"{instance.firstName.lower()}_{instance.lastName.lower()}"
            try:
                user = User.objects.get(username=constructed_username)
                user_found = True
                logger.info(f"Found user match by constructed username: {user.username}")
            except User.DoesNotExist:
                pass
        
        # If we found a matching user, link it to the employee
        if user_found:
            instance.user = user
            # Use update() to avoid triggering the post_save signal again
            Employee.objects.filter(pk=instance.pk).update(user=user)
            logger.info(f"Linked employee {instance.eID} to user {user.username}")
    except Exception as e:
        logger.error(f"Error in link_employee_to_user signal: {str(e)}")