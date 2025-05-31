from django.shortcuts import redirect, render, get_object_or_404
from .forms import *
from employee.models import Employee,Attendance,Notice,workAssignments,Requests, EmployeeNotification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SalaryDisbursement, Employee
from .forms import SalaryDisbursementForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import BusinessExpenditure
from .models import BusinessExpenditure, RequestType, Notification
from django.contrib.auth import logout
from datetime import datetime, date
import calendar
from django.db.models import Count
from django.utils import timezone
import pytz

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Employee, Attendance
import geocoder
from datetime import datetime
from django.contrib.auth.models import User
import json

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
from .models import Attendance, Employee

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
from .models import Attendance, Employee
import requests
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
# from .models import Employee, Attendance
    
def signup(request):
    if request.method == "POST":
        id = request.POST["id"]
        print("id:",id)
        password = request.POST["password"]
        print("password:",password)
        cnfpass = request.POST["cnfpass"]
        
        if password == cnfpass:
            if(Employee.objects.filter(eID=id).exists()):
                if(User.objects.filter(username=id).exists()):
                    messages.info(request,"Employee Already Registered")
                    return redirect("/signup")
                else:
                    user = User.objects.create_user(username=id,password=password)
                    user.save()
                    messages.info(request,"Registered Successfully")
                    return redirect("/signup")
            else:
                messages.info(request,"Invalid Employee")
                return redirect("/signup")
        else:
            messages.info(request,"Password Doesn't Match")
            return redirect("/signup")
            
    return render(request,"employee/signup.html")

def calculate_monthly_salary(employee, month=None, year=None):
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    # Get the number of days in the month
    _, num_days = calendar.monthrange(year, month)
    
    # Get all Sundays in the month
    all_sundays = [
        date(year, month, day)
        for day in range(1, num_days + 1)
        if date(year, month, day).weekday() == SUNDAY
    ]
    
    # Get past Sundays (up to today)
    today = date.today()
    past_sundays = [sunday for sunday in all_sundays if sunday <= today]
    
    # Get all attendance records for the month
    attendance_records = Attendance.objects.filter(
        eId=employee,
        login_time__year=year,
        login_time__month=month
    )
    
    # Get distinct login days for the employee
    distinct_working_days = set(attendance_records.values_list('login_time__date', flat=True).distinct())
    
    # Count present days (weekdays)
    weekdays_present = len(distinct_working_days)
    
    # Calculate total working days including Sundays
    total_working_days = weekdays_present + len(past_sundays)
    
    # Count approved leaves in this month
    leaves_taken = 0
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Approved'
    )
    
    # Debug information for leave calculation
    print(f"Found {approved_leaves.count()} approved leaves for employee {employee.eID}")
    
    for leave in approved_leaves:
        # Create a date range from from_date to to_date
        leave_start = leave.from_date
        leave_end = leave.to_date
        current_date = leave_start
        
        # Debug information for each leave
        print(f"Processing leave: {leave.title} from {leave_start} to {leave_end}")
        
        # Count each day of leave that falls in the current month
        while current_date <= leave_end:
            if current_date.month == month and current_date.year == year:
                # Don't count Sundays as leaves
                if current_date.weekday() != SUNDAY:
                    leaves_taken += 1
                    print(f"  Counting leave day: {current_date} (not a Sunday)")
            current_date += timedelta(days=1)
    
    print(f"Total leaves taken in {month}/{year}: {leaves_taken}")
    
    # Calculate working days after subtracting leaves
    working_days_after_leaves = total_working_days - leaves_taken
    
    # Calculate salary
    base_salary = float(employee.salary)
    daily_rate = base_salary / num_days  # Now includes Sundays in the calculation
    calculated_salary = daily_rate * working_days_after_leaves  # Use working days after leaves
    
    return {
        'total_days': num_days,  # This now includes Sundays
        'present_days': total_working_days,  # Updated to include Sundays
        'weekdays_present': weekdays_present,  # Added for dashboard display
        'sundays': len(past_sundays),  # Added for dashboard display
        'leaves_taken': leaves_taken,  # Added for leave tracking
        'working_days_after_leaves': working_days_after_leaves,  # Added for leave tracking
        'absent_days': num_days - total_working_days,
        'daily_rate': daily_rate,
        'calculated_salary': calculated_salary,
        'base_salary': base_salary
    }

@login_required
def dashboard(request):
    user = request.user
    
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        # Since this is the dashboard, redirect to login if there's no employee record
        logout(request)
        return redirect('login_user')
    
    # Get current month's attendance and salary calculation
    current_month = datetime.now().month
    current_year = datetime.now().year
    salary_info = calculate_monthly_salary(employee, current_month, current_year)
    
    # Get attendance records for the current month
    attendance_records = Attendance.objects.filter(
        eId=employee.eID,  # Use the employee's ID string instead of the object
        login_time__year=current_year,
        login_time__month=current_month
    ).order_by('login_time')
    
    # Get notices
    notices = Notice.objects.all().order_by('-publishDate')[:5]
    
    # Get work assignments
    work_assignments = workAssignments.objects.filter(taskerId=employee.eID).order_by('-assignDate')[:5]
    
    # Get leave details for the current month
    leave_days = []
    
    # Calculate the first and last day of the current month
    first_day = date(current_year, current_month, 1)
    if current_month == 12:
        last_day = date(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(current_year, current_month + 1, 1) - timedelta(days=1)
    
    # Get approved leaves that overlap with the current month
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Approved',
        from_date__lte=last_day,  # Leave starts before or during this month
        to_date__gte=first_day    # Leave ends after or during this month
    )
    
    print(f"Found {approved_leaves.count()} approved leaves for employee {employee.eID} in {current_month}/{current_year}")
    
    for leave in approved_leaves:
        # Create a date range from from_date to to_date, but only for the current month
        leave_start = max(leave.from_date, first_day)
        leave_end = min(leave.to_date, last_day)
        current_date = leave_start
        
        print(f"Processing leave: {leave.title} from {leave_start} to {leave_end}")
        
        # Count each day of leave that falls in the current month
        while current_date <= leave_end:
            # Don't count Sundays as leaves
            if current_date.weekday() != SUNDAY:
                leave_days.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'title': leave.title
                })
                print(f"  Counting leave day: {current_date} (not a Sunday)")
            current_date += timedelta(days=1)
    
    print(f"Total leave days in {current_month}/{current_year}: {len(leave_days)}")
    
    return render(request, 'employee/dashboard.html', {
        'employee': employee,
        'salary_info': salary_info,
        'attendance_records': attendance_records,
        'notices': notices,
        'work_assignments': work_assignments,
        'leave_days': leave_days
    })
    
@login_required(login_url='/')
def attendance(request):
    print("Attendance.objects:",Attendance.objects)
    attendance=Attendance.objects.filter(eId=request.user.username)
    print("attendance::",attendance)
    return render(request,"employee/attendance.html",{"info":attendance})    

from django.db.models import Q
@login_required(login_url='/')
def notice(request):
    # Fetch the logged-in employee
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')
    
    # Get filter period from request
    period = request.GET.get('period', 'all')
    
    # Base queryset: filter notices for the logged-in employee or global notices
    base_query = Notice.objects.filter(Q(employee=employee) | Q(is_global=True))
    
    # Current date for filtering
    current_date = datetime.now()
    
    # Filter notices based on selected period
    if period == '7days':
        # Past 7 days notices
        start_date = current_date - timedelta(days=7)
        notices = base_query.filter(publishDate__gte=start_date)
        period_name = "Past 7 Days"
    elif period == '15days':
        # Past 15 days notices
        start_date = current_date - timedelta(days=15)
        notices = base_query.filter(publishDate__gte=start_date)
        period_name = "Past 15 Days"
    elif period == 'month':
        # Past month notices
        start_date = current_date - timedelta(days=30)
        notices = base_query.filter(publishDate__gte=start_date)
        period_name = "Past Month"
    elif period == 'global':
        # Only global notices
        notices = base_query.filter(is_global=True)
        period_name = "Global Notices"
    elif period == 'personal':
        # Only personal notices
        notices = base_query.filter(employee=employee, is_global=False)
        period_name = "Personal Notices"
    else:
        # All notices
        notices = base_query
        period_name = "All Notices"
    
    # Order notices by publish date (newest first)
    notices = notices.order_by('-publishDate')
    
    # Calculate stats for the dashboard
    total_notices = base_query.count()
    global_notices = base_query.filter(is_global=True).count()
    personal_notices = base_query.filter(employee=employee, is_global=False).count()
    
    # Get notices from past 7 days for stats
    past_7_days = current_date - timedelta(days=7)
    notices_7_days = base_query.filter(publishDate__gte=past_7_days).count()
    
    # Get notices from past 15 days for stats
    past_15_days = current_date - timedelta(days=15)
    notices_15_days = base_query.filter(publishDate__gte=past_15_days).count()
    
    # Get notices from past month for stats
    past_month = current_date - timedelta(days=30)
    notices_month = base_query.filter(publishDate__gte=past_month).count()
    
    # Pass the filtered notices to the template
    context = {
        'notices': notices,
        'period': period,
        'period_name': period_name,
        'total_notices': total_notices,
        'global_notices': global_notices,
        'personal_notices': personal_notices,
        'notices_7_days': notices_7_days, 
        'notices_15_days': notices_15_days,
        'notices_month': notices_month,
    }
    
    return render(request, "employee/notice.html", context)

@login_required(login_url='/')
def noticedetail(request,id):
    noticedetail = Notice.objects.get(Id=id)
    return render(request,"employee/noticedetail.html",{"noticedetail":noticedetail})

from .models import WorkAssignment  # Assuming you have a model for work assignments

def assignedworklist(request):
    # Query for all work assignments or filter as per requirement
    assignments = WorkAssignment.objects.all()
    return render(request, 'assignedworklist.html', {'assignments': assignments})

@login_required(login_url='/')
def viewRequest(request):
    requests = Requests.objects.filter(destinationEmployeeId=request.user.username)
    return render(request,"employee/viewRequest.html",{"requests":requests})

@login_required(login_url='/')
def requestdetails(request,rid):
    requestdetail = Requests.objects.get(id=rid)
    return render(request,"employee/requestdetails.html",{"requestdetail":requestdetail})

@login_required(login_url='/')
def assignedworklist(request):
    works = workAssignments.objects.filter(assignerId=request.user.username).all()
    return render(request,"employee/assignedworklist.html",{"works":works})

@login_required(login_url='/')
def deletework(request, wid):
    obj = get_object_or_404(workAssignments, id=wid)
    obj.delete()
    return render(request,"employee/assignedworklist.html")

def salary_disbursement_view(request):
    if request.method == "POST":
        form = SalaryDisbursementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('salary_disbursement')  # Redirect to the same page or another.
    else:
        form = SalaryDisbursementForm()

    salary_records = SalaryDisbursement.objects.all()

    return render(request, 'salary_disbursement.html', {
        'form': form,
        'salary_records': salary_records,
    })

def update_salary_status(request, disbursement_id, status):
    disbursement = get_object_or_404(SalaryDisbursement, id=disbursement_id)
    disbursement.status = status
    disbursement.save()
    return redirect('salary_disbursement')

from .models import ExpenditureRequest, LeaveRequest, OtherRequest, Notification
from .forms import ExpenditureForm, LeaveForm, OtherRequestForm
from django.contrib.auth.decorators import login_required
from .models import Employee, Attendance, Notice, workAssignments, Requests,BusinessExpenditure
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExpenditureForm, LeaveForm, OtherRequestForm
from .forms import ExpenditureForm, LeaveForm, OtherRequestForm, SalaryDisbursementForm
from .models import Employee, Attendance, Notice, workAssignments, Requests, ExpenditureRequest, LeaveRequest, OtherRequest, Notification, SalaryDisbursement
from django.db.models import Sum, Q

def make_expenditure_request(request):
    template_name = 'employee/make_request.html'
    
    # Check if the user has an associated employee record
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        exp_name = request.POST.get('expenditure_name')
        exp_amount = request.POST.get('amount')
        exp_date = request.POST.get('date')
        expenditure = ExpenditureRequest.objects.create(
            employee=employee,
            expenditure_name=exp_name,
            amount=exp_amount,
            date=exp_date
        )
        # Create initial notification for request submission
        Notification.objects.create(
            employee=employee,
            message=f"Expenditure request submitted: {exp_name} (Rs. {exp_amount})"
        )
        messages.success(request, "Your expenditure request has been submitted successfully!")
        return redirect('make_request')

    return render(request, template_name)

def user_notifications(request):
    template_name = 'employee/notifications.html'
    
    # Check if the user has an associated employee record
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')
        
    notifications = Notification.objects.filter(employee=employee).order_by('-created_at')
    return render(request, template_name, {'notifications': notifications})

@login_required
def admin_expenditure_requests(request):
    if not request.user.is_superuser:
        return redirect('home')

    expenditure_requests = ExpenditureRequest.objects.all()
    context = {
        'expenditure_requests': expenditure_requests
    }
    return render(request, 'admin/expenditure_requests.html', context)

@login_required
def handle_expenditure_request(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    expenditure = ExpenditureRequest.objects.get(id=pk)
    if 'approve' in request.POST:
        expenditure.status = 'Approved'
        Notification.objects.create(
            employee=expenditure.employee,
            message=f"Expenditure request approved: {expenditure.expenditure_name} (Rs. {expenditure.amount})"
        )
    elif 'paid' in request.POST:
        expenditure.status = 'Paid'
        Notification.objects.create(
            employee=expenditure.employee,
            message=f"Expenditure request marked as paid: {expenditure.expenditure_name} (Rs. {expenditure.amount})"
        )
    elif 'unpaid' in request.POST:
        expenditure.status = 'Unpaid'
        Notification.objects.create(
            employee=expenditure.employee,
            message=f"Expenditure request pending payment: {expenditure.expenditure_name} (Rs. {expenditure.amount})"
        )
    elif 'delete' in request.POST:
        expenditure.status = 'Deleted'
        Notification.objects.create(
            employee=expenditure.employee,
            message=f"Expenditure request deleted: {expenditure.expenditure_name} (Rs. {expenditure.amount})"
        )
    expenditure.save()
    return redirect('admin_dashboard')

@login_required
def handle_leave_request(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    leave = LeaveRequest.objects.get(id=pk)
    
    # Ensure days field is calculated correctly
    from_date = leave.from_date
    to_date = leave.to_date
    days = 0
    current_date = from_date
    
    while current_date <= to_date:
        if current_date.weekday() != 6:  # 6 is Sunday
            days += 1
        current_date += timedelta(days=1)
    
    # Update days field if needed
    if leave.days != days:
        leave.days = days
    
    if 'approve' in request.POST:
        leave.status = 'Approved'
        Notification.objects.create(
            employee=leave.employee,
            message=f"Your leave request from {leave.from_date} to {leave.to_date} ({days} days) has been approved"
        )
    elif 'hold' in request.POST:
        leave.status = 'Hold'
        Notification.objects.create(
            employee=leave.employee,
            message=f"Your leave request from {leave.from_date} to {leave.to_date} ({days} days) has been put on hold"
        )
    elif 'delete' in request.POST:
        leave.status = 'Deleted'
        Notification.objects.create(
            employee=leave.employee,
            message=f"Your leave request from {leave.from_date} to {leave.to_date} ({days} days) has been deleted"
        )
    leave.save()

    return redirect('admin_leave_requests')

@login_required
def handle_other_request(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    other = OtherRequest.objects.get(id=pk)
    if 'approve' in request.POST:
        other.status = 'Approved'
        Notification.objects.create(
            employee=other.employee,
            message=f"Your request '{other.title}' has been approved"
        )
    elif 'hold' in request.POST:
        other.status = 'Hold'
        Notification.objects.create(
            employee=other.employee,
            message=f"Your request '{other.title}' has been put on hold"
        )
    elif 'delete' in request.POST:
        other.status = 'Deleted'
        Notification.objects.create(
            employee=other.employee,
            message=f"Your request '{other.title}' has been deleted"
        )
    other.save()

    return redirect('admin_other_requests')

@login_required
def make_request(request):
    template_name = 'employee/make_request.html'
    
    # Initialize forms at the beginning
    expenditure_form = ExpenditureForm()
    leave_form = LeaveForm()
    other_form = OtherRequestForm()
    
    # Check if the user has an associated employee record
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')

    # Get all request types
    request_types = RequestType.objects.all()
    
    # Get user's request history
    expenditure_requests = ExpenditureRequest.objects.filter(employee=employee).order_by('-date')
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-from_date')
    other_requests = OtherRequest.objects.filter(employee=employee).order_by('-date')
    
    # Prepare JSON data for JavaScript
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    # Serialize expenditure requests
    expenditure_data = json.dumps([
        {
            'name': e.expenditure_name,
            'amount': e.amount,
            'date': e.date,
            'status': e.status
        } for e in expenditure_requests
    ], cls=DjangoJSONEncoder)
    
    # Serialize leave requests
    leave_data = json.dumps(
        list(leave_requests.values('title', 'from_date', 'to_date', 'message', 'status')),
        cls=DjangoJSONEncoder
    )
    
    # Serialize other requests
    other_data = json.dumps(
        list(other_requests.values('title', 'date', 'message', 'status')),
        cls=DjangoJSONEncoder
    )
    
    # Calculate statistics
    total_expenditure_count = ExpenditureRequest.objects.filter(employee=employee).count()
    approved_expenditures = ExpenditureRequest.objects.filter(employee=employee, status='Approved').count()
    pending_expenditures = ExpenditureRequest.objects.filter(employee=employee, status='Pending').count()

    total_leaves = LeaveRequest.objects.filter(employee=employee).count()
    approved_leaves = LeaveRequest.objects.filter(employee=employee, status='Approved').count()
    pending_leaves = LeaveRequest.objects.filter(employee=employee, status='Pending').count()

    total_other_requests = OtherRequest.objects.filter(employee=employee).count()
    approved_other_requests = OtherRequest.objects.filter(employee=employee, status='Approved').count()
    pending_other_requests = OtherRequest.objects.filter(employee=employee, status='Pending').count()

    # Update context with all data
    context = {
        'request_types': request_types,
        'expenditure_form': expenditure_form,
        'leave_form': leave_form,
        'other_form': other_form,
        'expenditure_data': expenditure_data,
        'leave_data': leave_data,
        'other_data': other_data,
        'total_expenditure_count': total_expenditure_count,
        'approved_expenditures': approved_expenditures,
        'pending_expenditures': pending_expenditures,
        'total_leaves': total_leaves,
        'approved_leaves': approved_leaves,
        'pending_leaves': pending_leaves,
        'total_other_requests': total_other_requests,
        'approved_other_requests': approved_other_requests,
        'pending_other_requests': pending_other_requests,
    }

    if request.method == 'POST':
        request_type = request.POST.get('form_type')
        
        if request_type == 'expenditure':
            expenditure_form = ExpenditureForm(request.POST)
            if expenditure_form.is_valid():
                expenditure = expenditure_form.save(commit=False)
                expenditure.employee = employee
                expenditure.save()
                
                # Create notification for the admin
                Notification.objects.create(
                    employee=employee,
                    message=f"New expenditure request submitted: {expenditure.expenditure_name} (Rs. {expenditure.amount})"
                )
                
                messages.success(request, "Expenditure request submitted successfully!")
                return redirect('make_request')
            else:
                messages.error(request, "Please correct the errors in the form.")
                
        elif request_type == 'leave':
            leave_form = LeaveForm(request.POST)
            if leave_form.is_valid():
                leave = leave_form.save(commit=False)
                leave.employee = employee
                
                # Calculate the number of days (excluding Sundays)
                from_date = leave.from_date
                to_date = leave.to_date
                days = 0
                current_date = from_date
                
                while current_date <= to_date:
                    if current_date.weekday() != 6:  # 6 is Sunday
                        days += 1
                    current_date += timedelta(days=1)
                
                # Set the days field
                leave.days = days
                
                leave.save()
                
                # Create notification for the admin
                Notification.objects.create(
                    employee=employee,
                    message=f"New leave request submitted: {leave.title} from {leave.from_date} to {leave.to_date} ({days} days)"
                )
                
                messages.success(request, f"Leave request for {days} days submitted successfully!")
                return redirect('make_request')
            else:
                messages.error(request, "Please correct the errors in the form.")
                
        elif request_type == 'other':
            other_form = OtherRequestForm(request.POST)
            if other_form.is_valid():
                other = other_form.save(commit=False)
                other.employee = employee
                other.save()
                
                # Create notification for the admin
                Notification.objects.create(
                    employee=employee,
                    message=f"New request submitted: {other.title}"
                )
                
                messages.success(request, "Request submitted successfully!")
                return redirect('make_request')
            else:
                messages.error(request, "Please correct the errors in the form.")
    
    # Add all data to context
    context.update({
        'expenditure_requests': expenditure_requests,
        'leave_requests': leave_requests,
        'other_requests': other_requests,
    })
    
    return render(request, template_name, context)

from .forms import TaskAssignmentForm
@login_required
def assign_task(request):
    if request.user.is_staff:  # Only admins can assign tasks
        if request.method == "POST":
            form = TaskAssignmentForm(request.POST)
            if form.is_valid():
                form.save()  # Save the task to the database
                return redirect('task_assigned')  # Redirect to a confirmation page or another view
        else:
            form = TaskAssignmentForm()
        return render(request, 'employee/assign_task.html', {'form': form})
    else:
        return redirect('home')  # Redirect non-admin users to home
    
from .models import Task
from employee.models import Task
from datetime import datetime, timedelta

def my_work(request):
    # Check if user is authenticated first
    if not request.user.is_authenticated:
        messages.warning(request, "You are not logged in. Please login to view your work.")
        return redirect('login')  # Redirect to your login URL
        
    # Get the employee associated with the logged-in user
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')
    
    # Get filter period from request
    period = request.GET.get('period', 'all')
    
    # Base queryset: all tasks for this employee
    base_query = Task.objects.filter(employee=employee)
    
    # Current date for filtering
    current_date = datetime.now()
    
    # Filter tasks based on selected period
    if period == '7days':
        # Past 7 days tasks
        start_date = current_date - timedelta(days=7)
        tasks = base_query.filter(assign_date__gte=start_date)
        period_name = "Past 7 Days"
    elif period == 'month':
        # Past month tasks
        start_date = current_date - timedelta(days=30)
        tasks = base_query.filter(assign_date__gte=start_date)
        period_name = "Past Month"
    elif period == 'completed':
        # Only completed tasks
        tasks = base_query.filter(is_completed=True)
        period_name = "Completed Tasks"
    elif period == 'pending':
        # Only pending tasks
        tasks = base_query.filter(is_completed=False)
        period_name = "Pending Tasks"
    else:
        # All tasks
        tasks = base_query
        period_name = "All Tasks"
    
    # Order tasks by assign date (newest first)
    tasks = tasks.order_by('-assign_date')
    
    # Calculate stats for the dashboard
    total_tasks = base_query.count()
    completed_tasks = base_query.filter(is_completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    
    # Get tasks from past 7 days for stats
    past_7_days = current_date - timedelta(days=7)
    tasks_7_days = base_query.filter(assign_date__gte=past_7_days).count()
    
    # Get tasks from past month for stats
    past_month = current_date - timedelta(days=30)
    tasks_month = base_query.filter(assign_date__gte=past_month).count()
    
    # Pass the filtered tasks to the template
    context = {
        'work': tasks,
        'period': period,
        'period_name': period_name,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'tasks_7_days': tasks_7_days,
        'tasks_month': tasks_month,
        'now': current_date,
    }
    
    return render(request, 'employee/my_work.html', context)

# views.py in the employee app
from .models import Task  # Import the Task model
def work_details(request, wid):
    # Fetch the task using the task ID (wid)
    try:
        task = Task.objects.get(id=wid)
    except Task.DoesNotExist:
        return render(request, 'employee/error.html', {'error_message': 'Task not found'})
    return render(request, 'employee/work_details.html', {'task': task})

# views.py
@login_required(login_url='/')
def mark_task_completed(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return redirect('my_work')  # Redirect if task doesn't exist
    if task.employee.user == request.user:  
        task.is_completed = True  # Mark task as completed
        task.save()
    
    return redirect('my_work')  # Redirect to 'my_work' page after completion

####to get the attendance
from django.db.models import Count
from django.db.models import F
from django.utils import timezone
from calendar import monthrange, SUNDAY
from datetime import datetime, timedelta
from .models import Attendance, Employee
from datetime import datetime, date
from django.contrib.auth.decorators import login_required

SUNDAY = 6  # Sunday is the 6th day of the week (0=Monday, 6=Sunday)

def get_past_sundays(year, month):
    """Returns a list of past Sundays in the given month (up to today's date)."""
    today = date.today()
    _, days_in_month = monthrange(year, month)
    
    sundays = [
        date(year, month, day)
        for day in range(1, days_in_month + 1)
        if date(year, month, day).weekday() == SUNDAY and date(year, month, day) <= today
    ]
    return sundays

@login_required
def get_working_days_for_month(request):
    employee = request.user.employee  # Assuming user is linked to Employee
    employee_id = employee.eID  

    # Get selected month and year (default to current)
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))

    # Get total days in the selected month (Fixing issue)
    total_days_in_month = monthrange(year, month)[1]  # Always considers full month

    # Get only past Sundays
    past_sundays = get_past_sundays(year, month)

    # Get distinct working days (days when login_time is recorded)
    distinct_working_days = set(Attendance.objects.filter(
        eId=employee_id,
        login_time__month=month,
        login_time__year=year
    ).values_list('login_time__date', flat=True).distinct())

    # Total working days = Login Days + Past Sundays
    total_working_days = len(distinct_working_days | set(past_sundays))

    # Prepare month name
    month_name = datetime(year, month, 1).strftime('%B')

    # Info dictionary for the template
    info = {
        'month_name': month_name,
        'total_days': total_days_in_month,  # Fixed issue (now shows 28 for Feb)
        'working_days': total_working_days,  # Fixed issue (now shows correct working days)
        'year': year
    }

    return render(request, 'ems/attendance.html', {
        'info': info,
        'month': month,
        'year': year
    })

@login_required
def attendance_summary(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee record not found")
        return redirect('login_user')
    
    # Get Kolkata timezone
    kolkata_tz = pytz.timezone('Asia/Kolkata')
    current_time = timezone.now().astimezone(kolkata_tz)
    
    # Get current month and year in Kolkata time
    current_month = current_time.month
    current_year = current_time.year
    
    # Calculate 12-month history
    months_history = []
    for i in range(12):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        # Get attendance records for this month
        attendance_records = Attendance.objects.filter(
            eId=employee.eID,
            login_time__year=year,
            login_time__month=month
        ).order_by('login_time')
        
        # Calculate statistics for this month
        total_days = calendar.monthrange(year, month)[1]
        distinct_days_with_logins = attendance_records.values_list('login_time__date', flat=True).distinct().count()
        present_days = distinct_days_with_logins
        
        # Calculate leaves for this month
        leaves = LeaveRequest.objects.filter(
            employee=employee,
            status='Approved',
            from_date__year=year,
            from_date__month=month
        ).count()
        
        # Calculate working days
        working_days = total_days - leaves
        
        # Calculate attendance rate
        attendance_rate = (present_days / working_days * 100) if working_days > 0 else 0
        
        # Calculate salary for this month
        salary_info = calculate_monthly_salary(employee, month, year)
        
        # Add to history
        months_history.append({
            'month': month,
            'year': year,
            'present_days': present_days,
            'leaves': leaves,
            'working_days': working_days,
            'attendance_rate': attendance_rate,
            'salary': salary_info['calculated_salary'] if 'calculated_salary' in salary_info else 0
        })
    
    # Get current month's detailed records
    current_records = Attendance.objects.filter(
        eId=employee.eID,
        login_time__year=current_year,
        login_time__month=current_month
    ).order_by('login_time')
    
    # Calculate current month statistics
    total_days = calendar.monthrange(current_year, current_month)[1]
    distinct_days_with_logins = current_records.values_list('login_time__date', flat=True).distinct().count()
    present_days = distinct_days_with_logins
    
    # Calculate leaves for current month
    leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Approved',
        from_date__year=current_year,
        from_date__month=current_month
    ).count()
    
    # Get salary info for current month
    salary_info = calculate_monthly_salary(employee, current_month, current_year)
    
    # Use working_days_after_leaves from salary_info (using dictionary access)
    working_days = salary_info['working_days_after_leaves']
    
    # Calculate attendance rate using working_days_after_leaves
    attendance_rate = (present_days / working_days * 100) if working_days > 0 else 0
    
    # Make sure salary_info is properly converted to a context-friendly format
    context = {
        'employee': employee,
        'attendance_records': current_records,
        'months_history': months_history,
        'current_month': current_month,
        'current_year': current_year,
        'total_days': total_days,
        'present_days': present_days,
        'working_days': working_days,
        'attendance_rate': attendance_rate,
        'salary_info': salary_info,  # This is already a dictionary so it will work in the template
        'timezone': 'Asia/Kolkata'
    }
    return render(request, 'employee/attendance_summary.html', context)

from django.shortcuts import render
from .models import ExpenditureRequest, LeaveRequest, OtherRequest

def request_page(request):
    # Get the logged-in employee
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')
        
    expenditure_requests = list(ExpenditureRequest.objects.filter(employee=employee).values("expenditure_name", "amount", "status"))
    leave_requests = list(LeaveRequest.objects.filter(employee=employee).values("title", "from_date", "to_date", "status"))
    other_requests = list(OtherRequest.objects.filter(employee=employee).values("title", "date", "status"))

    context = {
        "expenditure_requests": expenditure_requests,
        "leave_requests": leave_requests,
        "other_requests": other_requests,
    }
    return render(request, "your_template.html", context)

from django.shortcuts import render
from .models import ExpenditureRequest, LeaveRequest, OtherRequest

def make_request_view(request):
    # Get the logged-in employee
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')

    # Filter requests for the logged-in employee using eID
    expenditure_requests = ExpenditureRequest.objects.filter(employee=employee).values("expenditure_name", "amount", "status")
    leave_requests = LeaveRequest.objects.filter(employee=employee).values("title", "from_date", "to_date", "status")
    other_requests = OtherRequest.objects.filter(employee=employee).values("title", "date", "status")

    context = {
        "expenditure_requests": list(expenditure_requests),
        "leave_requests": list(leave_requests),
        "other_requests": list(other_requests),
    }

    return render(request, "employee/make_request.html", context)

# Add a new view to display all request data
@login_required
def view_all_requests(request):
    # Get the current user
    user = request.user
    
    # Check if the user has an associated employee record
    try:
        employee = user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Your user account is not linked to an employee record. Please contact an administrator.")
        return redirect('dashboard')
    
    # Fetch all request data for the current employee
    expenditure_requests = ExpenditureRequest.objects.filter(employee=employee).order_by('-date')
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-from_date')
    other_requests = OtherRequest.objects.filter(employee=employee).order_by('-date')
    
    # Count statistics
    total_expenditure_requests = expenditure_requests.count()
    total_leave_requests = leave_requests.count()
    total_other_requests = other_requests.count()
    
    # Status counts
    approved_expenditures = expenditure_requests.filter(status='Approved').count()
    approved_leaves = leave_requests.filter(status='Approved').count()
    approved_others = other_requests.filter(status='Approved').count()
    
    # Create context dictionary
    context = {
        'expenditure_requests': expenditure_requests,
        'leave_requests': leave_requests,
        'other_requests': other_requests,
        'total_expenditure_requests': total_expenditure_requests,
        'total_leave_requests': total_leave_requests, 
        'total_other_requests': total_other_requests,
        'approved_expenditures': approved_expenditures,
        'approved_leaves': approved_leaves,
        'approved_others': approved_others,
        'total_requests': total_expenditure_requests + total_leave_requests + total_other_requests,
        'total_approved': approved_expenditures + approved_leaves + approved_others,
    }
    
    return render(request, 'employee/view_all_requests.html', context)

