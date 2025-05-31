# from django.contrib import admin
# from employee.models import Employee,Attendance,Notice,SalaryDisbursement

# # Register your models here.

# # Register your models here.
# admin.site.register(Employee)
# admin.site.register(Attendance)
# admin.site.register(Notice)

# @admin.register(SalaryDisbursement)
# class SalaryDisbursementAdmin(admin.ModelAdmin):
#     list_display = ('employee', 'get_month_year', 'status', 'salary_release_date')
#     list_filter = ('month', 'year', 'status')
#     search_fields = ('employee__firstName', 'employee__lastName', 'month', 'year')
#     ordering = ['-year', 'month', 'employee']

#     def get_month_year(self, obj):
#         return f"{obj.month}/{obj.year}"
#     get_month_year.short_description = "Month/Year"

# ####################################################################################3

# ##################################################################
# # 20/12/24
# from django.contrib import admin
# from .models import BusinessExpenditure

# class BusinessExpenditureAdmin(admin.ModelAdmin):
#     # Correctly set the ordering, list_display, and list_filter attributes
#     list_display = ('expenditure_name', 'amount', 'expenditure_date')  # Ensure 'expenditure_date' is in list_display
#     ordering = ['expenditure_date']  # Ensure 'expenditure_date' exists as a field in your model
#     list_filter = ['expenditure_date']  # Add 'expenditure_date' to list_filter

# admin.site.register(BusinessExpenditure, BusinessExpenditureAdmin)
# from django.contrib import admin
# from .models import ExpenditureRequest, LeaveRequest, OtherRequest

# # Register models to be visible in the admin interface
# admin.site.register(ExpenditureRequest)
# admin.site.register(LeaveRequest)
# admin.site.register(OtherRequest)

#########################################################################################
#23/12/24 above code is working
#################################################33333



from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib import messages
from employee.models import Employee,Attendance,Notice,SalaryDisbursement
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Notification, ExpenditureRequest, LeaveRequest, OtherRequest, Task, MonthlyDetails
from django.shortcuts import render
from django.contrib.admin import AdminSite
from .monthly_details import MonthlyEmployeeDetails
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django import forms as django_forms
from .forms import EmployeeAdminForm

class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        # Get current month and year
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # Calculate statistics
        employee_count = Employee.objects.all().count()
        notice_count = Notice.objects.filter(
            publishDate__month=current_month,
            publishDate__year=current_year
        ).count()
        task_count = Task.objects.filter(is_completed=False).count()
        
        # Total pending requests (combining all types)
        expenditure_requests = ExpenditureRequest.objects.filter(status='Pending').count()
        leave_requests = LeaveRequest.objects.filter(status='Pending').count()
        other_requests = OtherRequest.objects.filter(status='Pending').count()
        request_count = expenditure_requests + leave_requests + other_requests

        # Get user count
        from django.contrib.auth.models import User
        user_count = User.objects.all().count() 

        # Create or update extra_context
        extra_context = extra_context or {}
        extra_context.update({
            'employee_count': employee_count,
            'notice_count': notice_count,
            'task_count': task_count,
            'request_count': request_count,
            'user_count': user_count,
            'show_auth': True,  # Flag to explicitly show Auth section
            'monthly_details_url': '/admin/monthly-details/',  # Add the monthly details URL
        })
        return super().index(request, extra_context)
        
    def get_urls(self):
        from django.urls import path
        
        # Get original URLs
        urls = super().get_urls()
        
        # Define custom URLs here
        custom_urls = [
            path('monthly-details/', self.admin_view(monthly_details_view), name='monthly_details'),
            path('monthly-details/<int:year>/<int:month>/', self.admin_view(monthly_details_view), name='monthly_details_with_date'),
            path('update-salary-status/', self.admin_view(update_salary_status), name='update_salary_status'),
            path('employee/employee/detail/<str:employee_id>/', self.admin_view(employee_detail_view), name='employee_detail'),
        ]
        
        return custom_urls + urls

# Standalone function for monthly details view
def monthly_details_view(request, year=None, month=None):
    # Get current month and year
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Get filter parameters from request
    filter_month = month or request.GET.get('month', current_month)
    filter_year = year or request.GET.get('year', current_year)
    
    try:
        filter_month = int(filter_month)
        filter_year = int(filter_year)
    except (ValueError, TypeError):
        filter_month = current_month
        filter_year = current_year
    
    # Get all employees
    employees = Employee.objects.all().order_by('firstName')
    
    # Create a list of employee details
    employee_details = []
    for employee in employees:
        details = MonthlyEmployeeDetails(employee, filter_month, filter_year)
        employee_details.append({
            'employee': employee,
            'attendance_count': details.get_attendance_count(),
            'working_hours': details.get_total_working_hours(),
            'approved_leaves': details.get_approved_leaves(),
            'calculated_salary': details.calculate_monthly_salary(),
            'salary_status': details.get_salary_status(),
            'working_days': details.get_working_days_after_leaves(),
        })
    
    # Create month and year choices for dropdown
    month_choices = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    # Create year choices (current year and 2 years back)
    year_choices = [(current_year - i, current_year - i) for i in range(3)]
    
    # Add required variables for admin template with sidebar
    from django.contrib import admin
    from django.contrib.admin.views.main import ERROR_FLAG
    
    # Get all the registered models for the employee app
    app_list = custom_admin_site.get_app_list(request)
    
    context = {
        'title': 'Monthly Employee Details',
        'employee_details': employee_details,
        'month_choices': month_choices,
        'year_choices': year_choices,
        'selected_month': filter_month,
        'selected_year': filter_year,
        'opts': Employee._meta,
        'app_label': Employee._meta.app_label,
        'has_change_permission': True,
        'is_nav_sidebar_enabled': True,
        'available_apps': app_list,
        'error_flag': ERROR_FLAG,
        'has_sidebar': True,
    }
    
    return render(request, 'admin/employee/monthly_details.html', context)

# Function to update salary status
def update_salary_status(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        month = request.POST.get('month')
        year = request.POST.get('year')
        status = request.POST.get('status')
        amount = request.POST.get('amount')
        
        try:
            # Print debug info to console
            print(f"Updating salary status: Employee={employee_id}, Month={month}, Year={year}, Status={status}")
            
            employee = Employee.objects.get(eID=employee_id)
            
            # Convert numeric month to month name
            import calendar
            month_name = calendar.month_name[int(month)]
            
            # Calculate the salary using monthly details to ensure consistency
            details = MonthlyEmployeeDetails(employee, int(month), int(year))
            calculated_salary = details.calculate_monthly_salary()
            
            # Try to get existing record or create a new one
            try:
                salary_record = SalaryDisbursement.objects.get(
                    employee=employee,
                    month=month_name,
                    year=year
                )
                # Update existing record
                salary_record.total_salary = calculated_salary  # Always use calculated salary
                salary_record.status = status
                
                # If status is Paid and wasn't previously, set the release date
                if status == 'Paid' and not salary_record.salary_release_date:
                    salary_record.salary_release_date = timezone.now().date()
                
                salary_record.save()
                print(f"Updated existing record: {salary_record}")
                
            except SalaryDisbursement.DoesNotExist:
                # Create new record
                salary_record = SalaryDisbursement.objects.create(
                    employee=employee,
                    month=month_name,
                    year=year,
                    total_salary=calculated_salary,  # Always use calculated salary
                    status=status
                )
                
                # If status is Paid, set the release date
                if status == 'Paid':
                    salary_record.salary_release_date = timezone.now().date()
                    salary_record.save()
                
                print(f"Created new record: {salary_record}")
            
            from django.contrib import messages
            messages.success(request, f"Salary status for {employee.firstName} {employee.lastName} updated to {status}.")
            
        except Employee.DoesNotExist:
            from django.contrib import messages
            messages.error(request, f"Employee with ID {employee_id} not found.")
            print(f"Employee not found: {employee_id}")
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Error updating salary status: {str(e)}")
            print(f"Error: {str(e)}")
    
    # Redirect back to monthly details page with same month/year
    from django.shortcuts import redirect
    return redirect(f'/admin/monthly-details/{year}/{month}/')

# Helper function to convert numeric month to name
def get_month_name(month_number):
    import calendar
    return calendar.month_name[month_number]

def employee_detail_view(request, employee_id):
    """
    Display detailed information about a specific employee
    """
    employee = get_object_or_404(Employee, eID=employee_id)
    
    # Get attendance information for current month
    today = timezone.now().date()
    month = today.month
    year = today.year
    
    # Get employee's attendance for current month
    attendance_records = Attendance.objects.filter(
        employee=employee, 
        date__month=month,
        date__year=year
    ).order_by('-date')
    
    # Get employee's leave records
    leave_records = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-requestDate')[:5]  # Show 5 most recent leave requests
    
    # Get employee's monthly details for the current month
    monthly_details = MonthlyEmployeeDetails(employee, month, year)
    
    # Get employee's salary disbursement history
    salary_history = SalaryDisbursement.objects.filter(
        employee=employee
    ).order_by('-year', '-month')[:5]  # Show 5 most recent salary disbursements
    
    context = {
        'title': f'Employee Detail: {employee.firstName} {employee.lastName}',
        'employee': employee,
        'attendance_records': attendance_records,
        'leave_records': leave_records,
        'monthly_details': {
            'attendance_count': monthly_details.get_attendance_count(),
            'approved_leaves': monthly_details.get_approved_leaves(),
            'working_days': monthly_details.get_working_days_after_leaves(),
            'calculated_salary': monthly_details.calculate_monthly_salary(),
            'salary_status': monthly_details.get_salary_status()
        },
        'salary_history': salary_history,
        'opts': Employee._meta,
        'has_change_permission': True,
    }
    
    return render(request, 'admin/employee/employee_detail.html', context)

class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm
    list_display = ('eID', 'get_full_name', 'designation', 'email', 'phoneNo', 'joinDate', 'get_user_status')
    list_display_links = ('get_full_name',)
    list_filter = ('designation', 'joinDate')
    search_fields = ('eID', 'firstName', 'lastName', 'email', 'phoneNo')
    ordering = ['eID']
    fieldsets = (
            ('Personal Information', {
                'fields': ('eID', 'firstName', 'middleName', 'lastName', 'dOB', 'addharNo')
            }),
            ('Contact Information', {
                'fields': ('email', 'phoneNo')
            }),
            ('Employment Details', {
                'fields': ('designation', 'salary', 'joinDate')
            }),
            ('User Account', {
                'fields': ('user', 'create_user_account', 'auto_username', 'auto_password'),
                'classes': ('collapse',),
                'description': 'Link this employee to a user account or create a new one'
            }),
        )
    readonly_fields = ('auto_username', 'auto_password')
    actions = ['create_user_accounts']
    
    def get_full_name(self, obj):
        return f"{obj.firstName} {obj.middleName} {obj.lastName}".strip()
    get_full_name.short_description = 'Full Name'

    def get_user_status(self, obj):
        if obj.user:
            return f"Linked to {obj.user.username}"
        return "No user account"
    get_user_status.short_description = "User Account"
    
    def auto_username(self, obj):
        if not obj.pk:  # New employee being created
            return "Will be generated after saving"
        return f"{obj.firstName.lower()}_{obj.lastName.lower()}"
    auto_username.short_description = "Suggested Username"
    
    def auto_password(self, obj):
        if not obj.pk:  # New employee being created
            return "Will be generated after saving"
        return f"{obj.firstName.lower()}@{obj.eID}"
    auto_password.short_description = "Suggested Password"
    
    def save_model(self, request, obj, form, change):
        create_user = form.data.get('create_user_account') == 'on'
        super().save_model(request, obj, form, change)
        
        # If the create_user_account checkbox was checked and the employee doesn't have a user yet
        if create_user and not obj.user:
            username = f"{obj.firstName.lower()}_{obj.lastName.lower()}"
            # Check if username exists and modify if needed
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            # Create password
            password = f"{obj.firstName.lower()}@{obj.eID}"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=obj.email,
                password=password,
                first_name=obj.firstName,
                last_name=obj.lastName
            )
            
            # Link user to employee
            obj.user = user
            obj.save()
            
            # Add success message
            messages.success(
                request, 
                f"Created user account '{username}' with password '{password}' for employee {obj.firstName} {obj.lastName}"
            )
    
    def create_user_accounts(self, request, queryset):
        """Admin action to create user accounts for selected employees"""
        created_count = 0
        already_exists = 0
        
        for employee in queryset:
            if employee.user is not None:
                already_exists += 1
                continue
                
            # Generate username from first and last name
            username = f"{employee.firstName.lower()}_{employee.lastName.lower()}"
            # Check if username exists and modify if needed
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            # Create password
            password = f"{employee.firstName.lower()}@{employee.eID}"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=employee.email,
                password=password,
                first_name=employee.firstName,
                last_name=employee.lastName
            )
            
            # Link user to employee
            employee.user = user
            employee.save()
            created_count += 1
            
        if created_count > 0:
            messages.success(request, f"Created {created_count} user account(s)")
        if already_exists > 0:
            messages.info(request, f"Skipped {already_exists} employee(s) who already have user accounts")
            
    create_user_accounts.short_description = "Create user accounts for selected employees"

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'message', 'created_at', 'get_notification_type')
    list_filter = ('created_at', 'employee')
    search_fields = ('message', 'employee__username', 'employee__first_name', 'employee__last_name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_employee_name(self, obj):
        return f"{obj.employee.firstName} {obj.employee.lastName}"
    get_employee_name.short_description = 'Employee'
    
    def get_notification_type(self, obj):
        message = obj.message.lower()
        if 'expenditure' in message:
            return 'Expenditure Request'
        elif 'leave' in message:
            return 'Leave Request'
        else:
            return 'Other Request'
    get_notification_type.short_description = 'Type'
    
    def get_queryset(self, request):
        # Show notifications from the last 30 days by default
        qs = super().get_queryset(request)
        return qs.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30))

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_employee_name', 'date', 'earliest_login_time', 'latest_logout_time', 'get_working_hours', 'get_status')
    list_filter = ('date', 'eId')
    search_fields = ('eId__firstName', 'eId__lastName', 'eId__eID')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        from django.db.models import Min, Max, F, Q
        
        # Start with the basic queryset
        qs = super().get_queryset(request)
        
        # Get the requested date (if any) from the request
        date_param = request.GET.get('date__day')
        month_param = request.GET.get('date__month')
        year_param = request.GET.get('date__year')
        
        if date_param and month_param and year_param:
            # If specific date is requested, filter by that date
            filtered_date = f"{year_param}-{month_param}-{date_param}"
            qs = qs.filter(date=filtered_date)
        else:
            # By default, show only today's attendance
            today = timezone.now().date()
            qs = qs.filter(date=today)
        
        # Create temporary table to store earliest login and latest logout
        # Group by employee and date
        consolidated_data = {}
        
        # We need to maintain a list of IDs for the final queryset
        ids_to_include = []
        record_data = {}
        
        # Group by employee and date
        for record in qs:
            key = f"{record.eId.eID}_{record.date}"
            
            if key not in consolidated_data:
                # First record for this employee on this day
                consolidated_data[key] = {
                    'record_id': record.id,
                    'earliest_login': record.login_time,
                    'latest_logout': record.logout_time
                }
                ids_to_include.append(record.id)
            else:
                # If we already have a record, check if we need to update min/max times
                current_record = consolidated_data[key]
                
                if record.login_time and (not current_record['earliest_login'] or 
                                        record.login_time < current_record['earliest_login']):
                    current_record['earliest_login'] = record.login_time
                
                if record.logout_time and (not current_record['latest_logout'] or 
                                        record.logout_time > current_record['latest_logout']):
                    current_record['latest_logout'] = record.logout_time
        
        # Store the time data for each record ID
        for key, data in consolidated_data.items():
            record_data[data['record_id']] = {
                'earliest_login': data['earliest_login'],
                'latest_logout': data['latest_logout']
            }
        
        # Store the data for use in display methods
        self._consolidated_data = record_data
        
        # Filter the queryset to include only the representative record for each group
        filtered_qs = qs.filter(id__in=ids_to_include)
        return filtered_qs
    
    def get_employee_name(self, obj):
        return f"{obj.eId.firstName} {obj.eId.lastName}"
    get_employee_name.short_description = 'Employee'
    
    def earliest_login_time(self, obj):
        if obj.id in self._consolidated_data:
            login_time = self._consolidated_data[obj.id]['earliest_login']
            if login_time:
                # Convert to local timezone (IST) before formatting
                from django.utils import timezone
                ist_login_time = timezone.localtime(login_time)
                return ist_login_time.strftime('%I:%M:%S %p (IST)')
        return "Not logged in"
    earliest_login_time.short_description = 'Login Time'
    
    def latest_logout_time(self, obj):
        if obj.id in self._consolidated_data:
            logout_time = self._consolidated_data[obj.id]['latest_logout']
            if logout_time:
                # Convert to local timezone (IST) before formatting
                from django.utils import timezone
                ist_logout_time = timezone.localtime(logout_time)
                return ist_logout_time.strftime('%I:%M:%S %p (IST)')
        return "In Progress"
    latest_logout_time.short_description = 'Logout Time'
    
    def get_working_hours(self, obj):
        if obj.id in self._consolidated_data:
            login_time = self._consolidated_data[obj.id]['earliest_login']
            logout_time = self._consolidated_data[obj.id]['latest_logout']
            
            if login_time and logout_time:
                duration = logout_time - login_time
                hours = duration.total_seconds() / 3600
                return f"{hours:.1f} hours"
        return "In Progress"
    get_working_hours.short_description = 'Working Hours'
    
    def get_status(self, obj):
        if obj.id in self._consolidated_data:
            logout_time = self._consolidated_data[obj.id]['latest_logout']
            if logout_time:
                return "Completed"
        return "In Progress"
    get_status.short_description = 'Status'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_all_link'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('all/', self.admin_site.admin_view(self.all_attendance), name='attendance_all'),
        ]
        return custom_urls + urls
    
    def format_indian_date(self, date_obj):
        """Format a date in DD/MM/YYYY format for Indian style"""
        if date_obj:
            return date_obj.strftime('%d/%m/%Y')
        return ""

    def all_attendance(self, request):
        # Get filter parameters
        period = request.GET.get('period', 'today')
        employee_id = request.GET.get('employee_id')
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        # Base queryset
        qs = Attendance.objects.all()
        
        # Apply employee filter if specified
        if employee_id:
            qs = qs.filter(eId_id=employee_id)
        
        # Apply period filter
        today = timezone.now().date()
        if period == 'today':
            qs = qs.filter(date=today)
            period_name = "Today"
        elif period == 'yesterday':
            yesterday = today - timedelta(days=1)
            qs = qs.filter(date=yesterday)
            period_name = "Yesterday"
        elif period == '7days':
            seven_days_ago = today - timedelta(days=7)
            qs = qs.filter(date__gte=seven_days_ago)
            period_name = "Last 7 Days"
        elif period == '15days':
            fifteen_days_ago = today - timedelta(days=15)
            qs = qs.filter(date__gte=fifteen_days_ago)
            period_name = "Last 15 Days"
        elif period == '1month':
            one_month_ago = today - timedelta(days=30)
            qs = qs.filter(date__gte=one_month_ago)
            period_name = "Last Month"
        elif period == 'monthwise':
            if month and year:
                # Get all days in that month
                qs = qs.filter(date__year=year, date__month=month)
                period_name = f"{datetime(int(year), int(month), 1).strftime('%B %Y')}"
            else:
                qs = qs.filter(date__year=today.year, date__month=today.month)
                period_name = f"{today.strftime('%B %Y')}"
        
        # Using the same approach as in get_queryset to get consolidated records
        consolidated_records = {}
        record_dict = {}
        ids_to_include = []
        
        # Process each record to find earliest login and latest logout per employee per day
        for record in qs:
            key = f"{record.eId.eID}_{record.date}"
            
            if key not in consolidated_records:
                # First record for this employee on this day
                consolidated_records[key] = {
                    'record_id': record.id,
                    'employee': record.eId,
                    'date': record.date,
                    'earliest_login': record.login_time,
                    'latest_logout': record.logout_time,
                    'login_location': record.login_location,
                    'logout_location': record.logout_location,
                }
                ids_to_include.append(record.id)
            else:
                # Update earliest login time if this record has an earlier login
                if record.login_time and (not consolidated_records[key]['earliest_login'] or 
                                       record.login_time < consolidated_records[key]['earliest_login']):
                    consolidated_records[key]['earliest_login'] = record.login_time
                    consolidated_records[key]['login_location'] = record.login_location
                
                # Update latest logout time if this record has a later logout
                if record.logout_time and (not consolidated_records[key]['latest_logout'] or 
                                        record.logout_time > consolidated_records[key]['latest_logout']):
                    consolidated_records[key]['latest_logout'] = record.logout_time
                    consolidated_records[key]['logout_location'] = record.logout_location
        
        # Create a list of consolidated records for the template
        consolidated_list = []
        for data in consolidated_records.values():
            # Calculate working hours
            working_hours = None
            status = "In Progress"
            
            if data['earliest_login'] and data['latest_logout']:
                duration = data['latest_logout'] - data['earliest_login']
                working_hours = duration.total_seconds() / 3600
                status = "Completed"
            
            # Create a dictionary for each consolidated record
            consolidated_list.append({
                'employee': data['employee'],
                'date': data['date'],
                'formatted_date': self.format_indian_date(data['date']),
                'login_time': data['earliest_login'],
                'logout_time': data['latest_logout'],
                'login_location': data['login_location'],
                'logout_location': data['logout_location'],
                'working_hours': working_hours,
                'status': status
            })
        
        # Sort the consolidated list by date (newest first) and then by employee name
        consolidated_list.sort(key=lambda x: (x['date'], x['employee'].firstName), reverse=True)
        
        # Calculate statistics
        total_records = len(consolidated_list)
        completed_sessions = sum(1 for r in consolidated_list if r['status'] == 'Completed')
        in_progress_sessions = total_records - completed_sessions
        
        # Calculate average working hours for completed sessions
        total_hours = sum(r['working_hours'] for r in consolidated_list if r['working_hours'] is not None)
        average_hours = total_hours / completed_sessions if completed_sessions > 0 else 0
        
        # Prepare months for month-wise filter
        months = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        current_year = today.year
        years = range(current_year - 2, current_year + 1)
        
        context = {
            'title': 'All Attendance Records (Consolidated by Employee and Date)',
            'attendance_records': consolidated_list,
            'period': period,
            'period_name': period_name,
            'employee_id': employee_id,
            'current_month': int(month) if month else today.month,
            'current_year': int(year) if year else today.year,
            'months': months,
            'years': years,
            'employees': Employee.objects.all(),
            'total_records': total_records,
            'completed_sessions': completed_sessions,
            'in_progress_sessions': in_progress_sessions,
            'average_hours': average_hours,
            **self.admin_site.each_context(request),
        }
        
        return render(request, 'admin/attendance_all.html', context)

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_recipient', 'publishDate', 'get_time_period')
    list_filter = ('is_global', 'publishDate')
    search_fields = ('title', 'description', 'employee__firstName', 'employee__lastName', 'employee__eID')
    date_hierarchy = 'publishDate'
    
    def get_recipient(self, obj):
        if obj.is_global:
            return "Global Notice"
        return f"{obj.employee.firstName} {obj.employee.lastName} ({obj.employee.eID})"
    get_recipient.short_description = 'Recipient'
    
    def get_time_period(self, obj):
        today = timezone.now()
        pub_date = obj.publishDate
        
        if pub_date >= today - timezone.timedelta(days=7):
            return "Last 7 days"
        elif pub_date >= today - timezone.timedelta(days=15):
            return "Last 15 days"
        elif pub_date >= today - timezone.timedelta(days=30):
            return "Last month"
        return "Older"
    get_time_period.short_description = 'Time Period'
    
    def get_queryset(self, request):
        # Override to handle custom filtering in changelist view
        qs = super().get_queryset(request)
        period = request.GET.get('time_period')
        
        if period == '7days':
            return qs.filter(publishDate__gte=timezone.now() - timezone.timedelta(days=7))
        elif period == '15days':
            return qs.filter(publishDate__gte=timezone.now() - timezone.timedelta(days=15))
        elif period == '1month':
            return qs.filter(publishDate__gte=timezone.now() - timezone.timedelta(days=30))
        return qs
    
    def changelist_view(self, request, extra_context=None):
        # Add time period links to the change list view
        extra_context = extra_context or {}
        extra_context['time_periods'] = [
            {'name': 'All', 'url': request.path},
            {'name': 'Last 7 Days', 'url': f"{request.path}?time_period=7days"},
            {'name': 'Last 15 Days', 'url': f"{request.path}?time_period=15days"},
            {'name': 'Last Month', 'url': f"{request.path}?time_period=1month"},
        ]
        
        return super().changelist_view(request, extra_context)

class SalaryDisbursementAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_month_year', 'status', 'salary_release_date')
    list_filter = ('month', 'year', 'status')
    search_fields = ('employee__firstName', 'employee__lastName', 'month', 'year')
    ordering = ['-year', 'month', 'employee']

    def get_month_year(self, obj):
        return f"{obj.month}/{obj.year}"
    get_month_year.short_description = "Month/Year"

class ExpenditureRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'expenditure_name', 'amount', 'date', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('expenditure_name', 'employee__firstName', 'employee__lastName', 'employee__eID')
    ordering = ('-created_at',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('employee', 'task_details', 'assign_date', 'due_date', 'is_completed')
    search_fields = ['employee__user__username', 'task_details']
    list_filter = ['assign_date', 'due_date']

# Create a Monthly Details Admin view
class MonthlyDetailsAdmin(admin.ModelAdmin):
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(monthly_details_view), name='employee_monthly_details'),
            path('<int:year>/<int:month>/', self.admin_site.admin_view(monthly_details_view), name='employee_monthly_details_with_date'),
        ]
        return custom_urls + urls

# Register all models with the custom admin site
custom_admin_site = CustomAdminSite(name='customadmin')
custom_admin_site.register(Employee, EmployeeAdmin)
custom_admin_site.register(Attendance, AttendanceAdmin)
custom_admin_site.register(Notice, NoticeAdmin)
custom_admin_site.register(Task, TaskAdmin)
custom_admin_site.register(ExpenditureRequest, ExpenditureRequestAdmin)
custom_admin_site.register(LeaveRequest)
custom_admin_site.register(OtherRequest)
custom_admin_site.register(SalaryDisbursement, SalaryDisbursementAdmin)
custom_admin_site.register(Notification, NotificationAdmin)
custom_admin_site.register(MonthlyDetails, MonthlyDetailsAdmin)

# Register Django's built-in User model
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
custom_admin_site.register(User, UserAdmin)

# Create a custom UserAdmin class to make it more prominent
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

# Unregister the previous registration
custom_admin_site.unregister(User)

# Register with the custom admin class
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Group)
