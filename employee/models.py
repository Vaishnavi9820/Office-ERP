from pyexpat import model
from django.db import models
from pickle import TRUE
from turtle import title
from datetime import datetime
from django.contrib.auth.models import User  # Assuming Employee is related to Django's User model
# from .models import Employee  
designations_opt = (
    ('Team Leader','Team Leader'),
    ('Project Manager','Project Manager'),
    ('Senior Developer','Senior Developer'),
    ('Junior Developer','Junior Developer'),
    ('Intern','Intern'),
    ('QA Tester','QA Tester')
)

months = (
    ('January','January'),
    ('February','February'),
    ('March','March'),
    ('April','April'),
    ('May','May'),
    ('June','June'),
    ('July','July'),
    ('August','August'),
    ('September','September'),
    ('October','October'),
    ('November','November'),
    ('December','December')
)

days = (('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),
('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),
('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31'))

# Create your models here.

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    eID = models.CharField(primary_key=True,max_length=20)
    # username = models.CharField(max_length=50)
    firstName = models.CharField(max_length=50)
    middleName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    phoneNo = models.CharField(max_length=12,unique=True)
    email = models.EmailField(max_length=70,unique=True)
    addharNo = models.CharField(max_length=20,unique=True)
    dOB = models.DateField()
    designation = models.CharField(max_length=50,choices=designations_opt)
    salary = models.CharField(max_length=20)
    joinDate = models.DateField()

    def __str__(self):  
        return "%s %s %s " % (self.eID, self.firstName, self.lastName)
    
from django.db import models
from datetime import timedelta

class Attendance(models.Model):
    eId = models.ForeignKey(Employee, on_delete=models.CASCADE)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    login_location = models.CharField(max_length=255, null=True, blank=True)
    logout_location = models.CharField(max_length=255, null=True, blank=True)
    total_working_hours = models.DurationField(default=timedelta)
    date = models.DateField(auto_now_add=True)  # Add date field with auto_now_add
    status = models.CharField(max_length=20, default='Present')  # Add status field with default

    def calculate_hours(self):
        """Calculate the total working hours between login and logout times."""
        if self.login_time and self.logout_time:
            self.total_working_hours = self.logout_time - self.login_time
        else:
            self.total_working_hours = timedelta()

    def save(self, *args, **kwargs):
        # Ensure the date field is filled from login_time if it exists
        if self.login_time and not self.date:
            self.date = self.login_time.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.eId} - {self.login_time.date() if self.login_time else self.date}"


from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# class Attendance(models.Model):
#     employee = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField(auto_now_add=True)
#     login_time = models.DateTimeField(null=True, blank=True)
#     logout_time = models.DateTimeField(null=True, blank=True)
#     login_location = models.CharField(max_length=255, null=True, blank=True)
#     logout_location = models.CharField(max_length=255, null=True, blank=True)
#     total_working_hours = models.DurationField(default=timedelta)
#     total_working_days = models.IntegerField(default=0)

    # def calculate_working_hours(self):
    #     """Calculate total working hours based on login and logout time."""
    #     if self.login_time and self.logout_time:
    #         return self.logout_time - self.login_time
    #     return timedelta()

    # def save(self, *args, **kwargs):
    #     self.total_working_hours = self.calculate_working_hours()
    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.employee.username} - {self.date}"
    

class Notice(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE,default=1)
    Id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    publishDate = models.DateTimeField()
    is_global = models.BooleanField(default=False)

    def __str__(self):
        return self.title 
    

class workAssignments(models.Model):
    Id = models.CharField(max_length=20)
    assignerId = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="assignerId")
    work = models.TextField()
    assignDate = models.DateTimeField()
    dueDate = models.DateTimeField()
    taskerId = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="taskerId") 
class SalaryDisbursement(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Hold', 'Hold'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    month = models.CharField(
        max_length=20,
        choices=[
            ('January', 'January'), ('February', 'February'), ('March', 'March'),
            ('April', 'April'), ('May', 'May'), ('June', 'June'),
            ('July', 'July'), ('August', 'August'), ('September', 'September'),
            ('October', 'October'), ('November', 'November'), ('December', 'December')
        ],
        default=datetime.now().strftime('%B')  # Default to current month
    )
    year = models.PositiveIntegerField(default=datetime.now().year)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    salary_release_date = models.DateField(null=True, blank=True)  # For "Paid" option

    class Meta:
        unique_together = ('employee', 'month', 'year')
        ordering = ['-year', 'month', 'employee']

    def __str__(self):
        return f"{self.employee.firstName} - {self.month} {self.year} ({self.status})"

from django.db import models
class BusinessExpenditure(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    expenditure_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expenditure_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('approved', 'Approved'), ('pending', 'Pending'), ('rejected', 'Rejected')])

    def __str__(self):
        return f"Expenditure {self.expenditure_name} by {self.employee}"

    def __str__(self):
        return f"Expenditure {self.expenditure_name} by {self.employee}"

class RequestType(models.Model):
    TYPE_CHOICES = [
        ('expenditure', 'Expenditure Request'),
        ('leave', 'Leave Request'),
        ('other', 'Other Request'),
    ]
    
    name = models.CharField(max_length=50, choices=TYPE_CHOICES)
    
    def __str__(self):
        return self.name

from django.utils.timezone import now  # Import this
class Requests(models.Model):
    EXPENDITURE = 'expenditure'
    LEAVE = 'leave'
    OTHER = 'other'
    
    REQUEST_TYPE_CHOICES = [
        (EXPENDITURE, 'Expenditure Request'),
        (LEAVE, 'Leave Request'),
        (OTHER, 'Other Request'),
    ]

    requester = models.ForeignKey('Employee', on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    

    # For expenditure requests
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('pending', 'Pending')], null=True, blank=True)

    # For leave requests
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    
    # Additional fields and methods as needed
    def __str__(self):
        return f"{self.request_type} request by {self.requester}"

class ExpenditureRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Deleted', 'Deleted'),
    )

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    expenditure_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for history


    def __str__(self):
        return f"Expenditure Request {self.id} by {self.employee.firstName} {self.employee.lastName} ({self.employee.eID})"

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Deleted', 'Deleted'),
        ('Hold', 'Hold'),
    )

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    from_date = models.DateField()
    to_date = models.DateField()
    days = models.IntegerField(default=0)  # New field to store number of days
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName} - {self.title} ({self.from_date} to {self.to_date})"
    
class OtherRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Deleted', 'Deleted'),
        ('Hold', 'Hold'),
    )

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for history


    def __str__(self):
        return f"Other Request {self.id} - {self.title} by {self.employee.firstName} {self.employee.lastName} ({self.employee.eID})"

class Notification(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.employee.firstName} {self.employee.lastName} ({self.employee.eID})"

class EmployeeNotification(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.employee.firstName} {self.employee.lastName} ({self.employee.eID})"

class WorkAssignment(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    task_title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=[('Assigned', 'Assigned'), ('Completed', 'Completed'), ('Pending', 'Pending')])

    def __str__(self):
        return self.task_title
    
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    # employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE,default=1)
    task_details = models.TextField()
    assign_date = models.DateTimeField()
    due_date = models.DateTimeField()
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task for {self.employee.firstName} {self.employee.lastName} ({self.assign_date})"

# Proxy model for Monthly Details view
class MonthlyDetails(Employee):
    class Meta:
        proxy = True
        verbose_name = 'Monthly Detail'
        verbose_name_plural = 'Monthly Details'
