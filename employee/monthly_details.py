from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
from calendar import monthrange
from .models import Employee, Attendance, LeaveRequest, SalaryDisbursement

class MonthlyEmployeeDetails:
    """
    A utility class for calculating monthly statistics for employees
    This is not a database model, but a utility for the admin view
    """
    def __init__(self, employee, month=None, year=None):
        self.employee = employee
        
        # If month and year are not provided, use current month and year
        today = timezone.now().date()
        self.month = month if month else today.month
        self.year = year if year else today.year
        
        # Calculate days in month
        self.days_in_month = monthrange(self.year, self.month)[1]
        
        # Get date range for the month
        self.month_start = datetime(self.year, self.month, 1).date()
        if self.month == 12:
            self.month_end = datetime(self.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            self.month_end = datetime(self.year, self.month + 1, 1).date() - timedelta(days=1)
    
    def get_attendance_count(self):
        """Returns the number of days the employee was present in the current month"""
        return Attendance.objects.filter(
            eId=self.employee,
            date__gte=self.month_start,
            date__lte=self.month_end
        ).count()
    
    def get_total_working_hours(self):
        """Returns the total working hours for the month"""
        attendances = Attendance.objects.filter(
            eId=self.employee,
            date__gte=self.month_start,
            date__lte=self.month_end
        )
        
        total_hours = timedelta()
        for attendance in attendances:
            if attendance.total_working_hours:
                total_hours += attendance.total_working_hours
        
        # Convert to hours and minutes as string
        total_seconds = total_hours.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        return f"{hours} hours, {minutes} minutes"
    
    def get_approved_leaves(self):
        """Returns the number of approved leaves in the current month"""
        leaves = LeaveRequest.objects.filter(
            employee=self.employee,
            status='Approved',
            from_date__lte=self.month_end,
            to_date__gte=self.month_start
        )
        
        total_days = 0
        for leave in leaves:
            # Calculate overlap with current month
            leave_start = max(leave.from_date, self.month_start)
            leave_end = min(leave.to_date, self.month_end)
            
            # Calculate days between dates (inclusive)
            delta = (leave_end - leave_start).days + 1
            total_days += delta
        
        return total_days
    
    def get_working_days_after_leaves(self):
        """Returns the number of working days after accounting for approved leaves"""
        present_days = self.get_attendance_count()
        approved_leaves = self.get_approved_leaves()
        return present_days - approved_leaves
    
    def calculate_monthly_salary(self):
        """
        Calculate the salary based on attendance and base salary
        Formula: (Base salary / days in month) * actual working days
        """
        try:
            base_salary = float(self.employee.salary)
            # Calculate working days as present days minus approved leaves
            working_days = self.get_working_days_after_leaves()
            
            if working_days < 0:
                working_days = 0
                
            # Calculate daily rate based on total days in month
            daily_rate = base_salary / self.days_in_month
            monthly_salary = daily_rate * working_days
            
            return round(monthly_salary, 2)
        except (ValueError, ZeroDivisionError):
            # Handle case where salary isn't a valid number
            return 0
    
    def get_salary_status(self):
        """Check if salary has been disbursed for this month"""
        try:
            # Convert numeric month to month name (January, February, etc.)
            import calendar
            month_name = calendar.month_name[self.month]
            
            salary_record = SalaryDisbursement.objects.get(
                employee=self.employee,
                month=month_name,
                year=str(self.year)
            )
            return salary_record.status
        except SalaryDisbursement.DoesNotExist:
            return "Unpaid"
