from django.shortcuts import render
from urllib import request
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db.models import Q
from employee.models import Employee
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from employee.models import Employee, Attendance, LeaveRequest
from django.utils.timezone import now
from django.http import JsonResponse
import uuid
import json
from datetime import timedelta
from django.views.decorators.cache import never_cache


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from employee.models import Employee
from django.contrib.auth.models import User

# def login_user(request):
#     if request.method == "POST":
#         user_id = request.POST.get("id")
#         password = request.POST.get("password")
        
#         try:
#             # Check if the provided ID corresponds to an eID in Employee
#             employee = Employee.objects.get(eID=user_id)
#             username = employee.user.username  # Get associated username
#         except Employee.DoesNotExist:
#             username = user_id  # Assume the ID is a username if not an eID
        
#         # Authenticate using username and password
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)
#             return redirect("/ems/dashboard")
#         else:
#             messages.error(request, "Invalid Credentials")
#             return redirect("/")
    
#     return render(request, "employee/Login.html")

# # Create your views here.
# # def login_user(request):
# #     if request.method == "POST":
# #         id = request.POST["id"]
# #         password = request.POST["password"]
# #         user = authenticate(request,username=id,password=password)
# #         if user is not None:
# #             login(request , user)
# #             return redirect("/ems/dashboard")
# #         else:
# #             messages.error(request,"Invalid Credentials")
# #             return redirect("/")

# #     return render(request,"employee/Login.html")


# def logout_user(request):
#     logout(request)
#     return redirect("/")


def signup(request):
    if request.method == "POST":
        id = request.POST["id"]
        password = request.POST["password"]
        cnfpass = request.POST["cnfpass"]
        
        if password == cnfpass:
            if(Employee.objects.filter(eID=id).exists()):
                if(User.objects.filter(username=id).exists()):
                    messages.info(request,"Employee Already Registered")
                    return redirect("/signup")
                else:
                    # Create the user account
                    user = User.objects.create_user(username=id,password=password)
                    user.save()
                    
                    # Link the User to the Employee record
                    employee = Employee.objects.get(eID=id)
                    employee.user = user
                    employee.save()
                    
                    messages.info(request,"Registered Successfully")
                    return redirect("/signup")
            else:
                messages.info(request,"Invalid Employee")
                return redirect("/signup")
        else:
            messages.info(request,"Password Doesn't Match")
            return redirect("/signup")
            
    return render(request,"employee/signup.html")


###################################
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
# from .models import Employee, Attendance
import geocoder
from datetime import datetime
from django.contrib.auth.models import User



from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime


from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
from employee.models import Attendance, Employee
import requests

# Function to fetch location based on IP
def fetch_location():
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            return response.json().get('city', 'Unknown')
        return "Unknown"
    except requests.exceptions.RequestException:
        return "Unknown"

# Login functionality with location tracking
from django.utils.timezone import now  # To handle timezone-aware datetime

# def login_user(request): ###working perfectly
#     if request.method == "POST":
#         user_id = request.POST.get("id")
#         print("user_id:", user_id)
#         password = request.POST.get("password")
#         print("password:", password)
        
#         try:
#             # Check if the provided ID corresponds to an eID in Employee
#             employee = Employee.objects.get(eID=user_id)
#             username = employee.user.username  # Get associated username
#             print("username:", username)
#         except Employee.DoesNotExist:
#             username = user_id  # Assume the ID is a username if not an eID
        
#         # Authenticate using username and password
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)

#             # Fetch and log the login location
#             location = fetch_location()
#             print("location:", location)
#             messages.success(request, f"Logged in from {location}")
            
#             # Log the attendance with login time and location
#             attendance = Attendance.objects.create(
#                 eId=employee,  # Pass the Employee instance, not just the ID
#                 login_time=now(),  # Use timezone-aware datetime
#                 login_location=location
#             )
#             attendance.save()

#             return redirect("/ems/dashboard")
#         else:
#             messages.error(request, "Invalid Credentials")
#             return redirect("/")
    
#     return render(request, "employee/Login.html")




def get_location(request):
    g = geocoder.ip('me')  # Get location based on IP (can be replaced with better method)
    return g.city

# def logout_user(request):
#     if request.user.is_authenticated:
#         employee = Employee.objects.get(user=request.user)
#         attendance = Attendance.objects.filter(employee=employee, logout_time__isnull=True).first()
        
#         if attendance:
#             # Get the logout location from the frontend
#             logout_location = request.POST.get('logout_location', '')
#             attendance.logout_time = datetime.now()
#             attendance.logout_location = logout_location  # Save location
#             attendance.calculate_hours()  # Calculate total working hours
#             attendance.save()
            
        
#         logout(request)
#         messages.success(request, "Logged out successfully")
#         return redirect('login')
    
#     return redirect('login')

from django.utils.timezone import now  # Import timezone-aware datetime

# def logout_user(request): #working but not datewise
#     if request.user.is_authenticated:
#         # Fetch the employee record
#         employee = Employee.objects.get(user=request.user)

#         # Fetch the existing attendance record where logout_time is null
#         attendance = Attendance.objects.filter(eId=employee, logout_time__isnull=True).first()

#         if attendance:
#             # Get the logout location from the frontend (POST request)
#             logout_location = request.POST.get('logout_location', '')

#             # Update only the necessary fields
#             logout_time = now()  # Use timezone-aware datetime
#             attendance.logout_time = logout_time
#             attendance.logout_location = logout_location

#             # Calculate total working hours
#             if attendance.login_time:  # Ensure login_time exists
#                 attendance.total_working_hours = (logout_time - attendance.login_time).total_seconds() / 3600.0

#             # Save the attendance record
#             attendance.save()

#         # Log out the user
#         logout(request)
#         messages.success(request, "Logged out successfully")
#         return redirect('/')

#     return redirect('/')

from django.utils.timezone import now
from datetime import timedelta

# def logout_user(request): #####working perfectly
#     if request.user.is_authenticated:
#         # Get the employee record
#         employee = Employee.objects.get(user=request.user)

    #     # Fetch today's attendance record with no logout time
    #     current_date = now().date()
    #     attendance = Attendance.objects.filter(
    #         eId=employee,
    #         login_time__date=current_date,
    #         logout_time__isnull=True
    #     ).first()

    #     if attendance:
    #         # Get the logout location from the frontend (POST request)
    #         logout_location = request.POST.get('logout_location', '')

    #         # Update the logout details
    #         logout_time = now()
    #         attendance.logout_time = logout_time
    #         print("attendance.logout_time:", attendance.logout_time)
    #         attendance.logout_location = logout_location
    #         print("attendance.logout_location:", attendance.logout_location)

    #         # Calculate total working hours
    #         if attendance.login_time:
    #             attendance.total_working_hours = logout_time - attendance.login_time
    #             print("attendance.total_working_hours:", attendance.total_working_hours)

    #         # Save the attendance record
    #         attendance.save()

    #     # Log out the user
    #     logout(request)
    #     messages.success(request, "Logged out successfully")
    #     return redirect('/')

    # return redirect('/')



from django.utils.timezone import now
import json

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now

from django.utils.timezone import now

def login_user(request):
    # Clear any existing session first, regardless of authentication status
    # This resolves phantom sessions where the user appears logged in but isn't
    if 'sessionid' in request.COOKIES:
        # Create a response object to delete the session cookie
        response = render(request, 'employee/login.html')
        response.delete_cookie('sessionid')
        response.delete_cookie('employeesession')  # Also delete custom cookie if used
        
        # Only show message if user was actually authenticated
        if request.user.is_authenticated:
            logout(request)  # Properly logout the authenticated user
            request.session.flush()
            return response
        
        # Return the response with deleted cookies for non-authenticated users
        return response
        
    if request.method == 'POST':
        user_id = request.POST.get('id')  # User-provided ID
        password = request.POST.get('password')
        login_location = request.POST.get('login_location', 'Web login')  # Location for attendance
        
        # First, check if this is a direct username login
        user = authenticate(request, username=user_id, password=password)
        
        # If username login failed, try employee ID login
        if user is None:
            try:
                # Look up by employee ID
                employee = Employee.objects.get(eID=user_id)
                
                # Check if employee has an associated user account
                if hasattr(employee, 'user') and employee.user is not None:
                    # Try authenticating with employee's user account
                    user = authenticate(request, username=employee.user.username, password=password)
                    
            except Employee.DoesNotExist:
                # No matching employee record
                pass
        
        # At this point, if user is not None, authentication succeeded
        if user is not None:
            # Successfully authenticated - log the user in with a fresh session
            login(request, user)
            
            # Check if user has a linked employee record
            try:
                # Get employee record for the user
                employee = Employee.objects.get(user=user)
                
                # If we get here, employee record exists, proceed with attendance
                try:
                    # Record the attendance
                    current_time = now()
                    
                    # First check if there's an incomplete attendance record for today
                    existing_attendance = Attendance.objects.filter(
                        eId=employee,
                        date=current_time.date(),
                        logout_time__isnull=True
                    ).first()
                    
                    if existing_attendance:
                        # Found an existing incomplete record - use it
                        attendance = existing_attendance
                    else:
                        # Create a new attendance record
                        attendance = Attendance.objects.create(
                            eId=employee,
                            login_time=current_time,
                            login_location=login_location,
                            date=current_time.date(),
                            status='Present'
                        )
                    
                    # Explicitly save to ensure it's recorded
                    attendance.save()
                    
                    # Successful login - redirect to dashboard
                    messages.success(request, f"Welcome {user.username}!")
                    return redirect('/ems/dashboard')
                    
                except Exception as e:
                    print(f"Error with attendance: {str(e)}")
                    # Continue to dashboard even if attendance fails
                    messages.warning(request, f"Welcome {user.username}! Note: Could not record attendance.")
                    return redirect('/ems/dashboard')
                
            except Employee.DoesNotExist:
                # No employee record linked to this user - try to automatically link
                employee_found = False
                
                # Try to find a matching employee record using various methods
                try:
                    # 1. Try to match by username and eID
                    try:
                        employee = Employee.objects.get(eID=user.username)
                        employee_found = True
                    except Employee.DoesNotExist:
                        pass
                    
                    # 2. Try to match by email
                    if not employee_found and user.email:
                        try:
                            employee = Employee.objects.get(email__iexact=user.email)
                            employee_found = True
                        except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                            pass
                    
                    # 3. Try to match by first name and last name
                    if not employee_found and hasattr(user, 'first_name') and hasattr(user, 'last_name') and user.first_name and user.last_name:
                        try:
                            employee = Employee.objects.get(
                                firstName__iexact=user.first_name,
                                lastName__iexact=user.last_name
                            )
                            employee_found = True
                        except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                            pass
                    
                    # 4. Try to match by username parts (assuming username might be in format firstname_lastname)
                    if not employee_found:
                        username_parts = user.username.split('_')
                        if len(username_parts) == 2:
                            try:
                                employee = Employee.objects.get(
                                    firstName__iexact=username_parts[0],
                                    lastName__iexact=username_parts[1]
                                )
                                employee_found = True
                            except (Employee.DoesNotExist, Employee.MultipleObjectsReturned):
                                pass
                    
                    # If we found a matching employee, link it to the user
                    if employee_found:
                        # Make sure the employee isn't already linked to another user
                        if employee.user is None:
                            employee.user = user
                            employee.save()
                            messages.success(request, f"Successfully linked your account to employee record: {employee.firstName} {employee.lastName}")
                            
                            # Record attendance for the newly linked employee
                            try:
                                current_time = now()
                                attendance = Attendance.objects.create(
                                    eId=employee,
                                    login_time=current_time,
                                    login_location=login_location,
                                    date=current_time.date(),
                                    status='Present'
                                )
                                attendance.save()
                            except Exception as e:
                                print(f"Error recording attendance for newly linked employee: {str(e)}")
                            
                            return redirect('/ems/dashboard')
                        elif employee.user.id == user.id:
                            # Already linked to this user (shouldn't happen, but just in case)
                            return redirect('/ems/dashboard')
                        else:
                            # Employee is linked to a different user
                            messages.warning(request, "Found a matching employee record, but it's already linked to another user account.")
                
                except Exception as e:
                    print(f"Error during automatic employee linking: {str(e)}")
                
                # If we get here, we couldn't automatically link - show the linking page
                try:
                    employee_count = Employee.objects.count()
                    all_employees = Employee.objects.filter(user__isnull=True).order_by('firstName')
                    
                    # Try to find potential matches for the user
                    matching_employees = []
                    
                    # Match by username parts
                    username_parts = user.username.split('_')
                    if len(username_parts) == 2:
                        first_name_matches = Employee.objects.filter(
                            firstName__iexact=username_parts[0],
                            user__isnull=True
                        )
                        for emp in first_name_matches:
                            matching_employees.append(emp)
                    
                    # Match by email domain
                    if user.email and '@' in user.email:
                        email_username = user.email.split('@')[0]
                        email_matches = Employee.objects.filter(
                            email__icontains=email_username,
                            user__isnull=True
                        )
                        for emp in email_matches:
                            if emp not in matching_employees:
                                matching_employees.append(emp)
                    
                    # Prepare context for the linking page
                    context = {
                        'authenticated_user': user,
                        'username': user.username,
                        'user_id': user.id,
                        'no_employees': employee_count == 0,
                        'all_employees': all_employees[:20],  # Limit to first 20
                        'matching_employees': matching_employees[:5],  # Show top 5 potential matches
                        'user_email': user.email,
                    }
                    return render(request, 'employee/user_employee_linking.html', context)
                    
                except Exception as e:
                    print(f"Error preparing employee data: {str(e)}")
                    messages.error(request, "Error preparing employee data. Please contact support.")
                    return redirect('login_user')
        else:
            # Authentication failed
            messages.error(request, "Invalid credentials. Please check your ID and password.")
    
    # GET request or failed POST - show login form
    return render(request, 'employee/login.html')



from django.http import JsonResponse
import json
from django.utils.timezone import now

# def logout_user(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         # Parse the JSON body
#         try:
#             data = json.loads(request.body)
#             logout_location = data.get('logout_location', '')
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)

#         # Fetch the employee record
#         employee = Employee.objects.get(user=request.user)

#         # Fetch today's attendance record with no logout time
#         current_date = now().date()
#         attendance = Attendance.objects.filter(
#             eId=employee,
#             login_time__date=current_date,
#             logout_time__isnull=True
#         ).first()

#         if attendance:
#             # Update the logout details
#             logout_time = now()
#             attendance.logout_time = logout_time
#             attendance.logout_location = logout_location
#             if attendance.login_time:
#                 attendance.total_working_hours = logout_time - attendance.login_time

#             # Save the attendance record
#             attendance.save()

#         # Log out the user
#         logout(request)
#         messages.success(request, "Logged out successfully")
#         return redirect('/')

#     # return redirect('/')
#         # return JsonResponse({'success': 'Logged out successfully'})
#     return redirect('/')

    # return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)

from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib import messages
import json

# def logout_user(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         try:
#             # Parse the logout location
#             logout_location = request.POST.get('logout_location', '')
#             print("Logout location received:", logout_location)

#             # Fetch employee and attendance record
#             employee = Employee.objects.get(user=request.user)
#             current_date = now().date()
#             attendance = Attendance.objects.filter(
#                 eId=employee,
#                 login_time__date=current_date,
#                 logout_time__isnull=True
#             ).first()

#             if attendance:
#                 logout_time = now()
#                 attendance.logout_time = logout_time
#                 attendance.logout_location = logout_location
#                 if attendance.login_time:
#                     attendance.total_working_hours = (
#                         logout_time - attendance.login_time
#                     ).total_seconds() / 3600
#                 attendance.save()

#                 print("Attendance record updated:", attendance)

#             # Log out the user
#             logout(request)
#             return JsonResponse({'success': 'Logged out successfully'})
#         except Exception as e:
#             print("Error during logout:", str(e))
#             return JsonResponse({'error': 'An error occurred during logout'}, status=500)

#     return redirect('/')


# from django.shortcuts import redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from employee.models import Attendance, Employee
# from django.http import JsonResponse
# from django.utils.timezone import now

# def logout_user(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         # Get logout location from the POST data
#         logout_location = request.POST.get('logout_location', '')
#         print("Logout location received:", logout_location)

#         try:
#             # Fetch the employee record for the logged-in user
#             employee = Employee.objects.get(user=request.user)
#             print("Employee fetched:", employee)

#             # Fetch today's attendance record with no logout time
#             current_date = now().date()
#             attendance = Attendance.objects.filter(
#                 eId=employee,
#                 login_time__date=current_date,
#                 logout_time__isnull=True
#             ).first()

#             if attendance:
#                 # Update the logout details
#                 logout_time = now()
#                 attendance.logout_time = logout_time
#                 attendance.logout_location = logout_location
#                 print("Logout time:", logout_time)
#                 print("Logout location:", logout_location)

#                 # Calculate total working hours
#                 if attendance.login_time:
#                     attendance.total_working_hours = (logout_time - attendance.login_time).total_seconds() / 3600
#                     print("Total working hours:", attendance.total_working_hours)

#                 # Save the attendance record
#                 attendance.save()
#                 print("Attendance record updated successfully.")
#             else:
#                 print("No attendance record found for today.")

#             # Log out the user
#                 logout(request)
#                 messages.success(request, "Logged out successfully")
#                 return redirect('/')

#         except Employee.DoesNotExist:
#             return JsonResponse({'error': 'No employee record found for the user'}, status=404)
#         except Exception as e:
#             print("An error occurred:", e)
#             return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

#     return redirect('/')


from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from employee.models import Attendance, Employee
from django.http import JsonResponse
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.utils.timezone import now
import json

# def logout_user(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         try:
#             # Parse the logout location
#             logout_location = request.POST.get('logout_location', '')
#             print("Logout location received:", logout_location)

#             # Fetch employee and attendance record
#             employee = Employee.objects.get(user=request.user)
#             current_date = now().date()
#             attendance = Attendance.objects.filter(
#                 eId=employee,
#                 login_time__date=current_date,
#                 logout_time__isnull=True
#             ).first()

#             if attendance:
#                 logout_time = now()
#                 attendance.logout_time = logout_time
#                 attendance.logout_location = logout_location
#                 if attendance.login_time:
#                     attendance.total_working_hours = (
#                         logout_time - attendance.login_time
#                     ).total_seconds() / 3600
#                 attendance.save()

#                 print("Attendance record updated:", attendance)

#             # Log out the user
#             logout(request)
#             return JsonResponse({'success': 'Logged out successfully'})
#         except Exception as e:
#             print("Error during logout:", str(e))
#             return JsonResponse({'error': 'An error occurred during logout'}, status=500)

#     return redirect('/')

# from datetime import datetime
# from django.utils.timezone import make_aware

# def logout_user(request):
#     if request.method == "POST":
#         user = request.user
#         logout_location = request.POST.get('logout_location')
        
#         # Get the latest attendance record for the user
#         attendance = Attendance.objects.filter(eId=user.id).order_by('-id').first()
#         if attendance and attendance.login_time:
#             # Calculate logout_time
#             logout_time = make_aware(datetime.now())
#             attendance.logout_location = logout_location
#             attendance.logout_time = logout_time

#             # Calculate total working hours as a timedelta
#             total_working_time = logout_time - attendance.login_time
#             attendance.total_working_hours = total_working_time  # Django will handle interval conversion

#             try:
#                 attendance.save()
#                 logout(request)
#                 return redirect('login_user')  # Redirect to login after logout
#             except Exception as e:
#                 print(f"Error during logout: {e}")
#                 return HttpResponse("An error occurred during logout.")
#         else:
#             return HttpResponse("No login record found.")



# from django.shortcuts import redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from employee.models import Attendance, Employee
# from django.http import JsonResponse
# from django.utils.timezone import now

# def logout_user(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         # Get logout location from the POST data
#         logout_location = request.POST.get('logout_location', '')
#         print("Logout location received:", logout_location)

#         try:
#             # Fetch the employee record for the logged-in user
#             employee = Employee.objects.get(user=request.user)
#             print("Employee fetched:", employee)

#             # Fetch today's attendance record with no logout time
#             current_date = now().date()
#             attendance = Attendance.objects.filter(
#                 eId=employee,
#                 login_time__date=current_date,
#                 logout_time__isnull=True
#             ).first()

#             if attendance:
#                 # Update the logout details
#                 logout_time = now()
#                 attendance.logout_time = logout_time
#                 attendance.logout_location = logout_location
#                 print("Logout time:", logout_time)
#                 print("Logout location:", logout_location)

#                 # Calculate total working hours
#                 if attendance.login_time:
#                     attendance.total_working_hours = (logout_time - attendance.login_time).total_seconds() / 3600
#                     print("Total working hours:", attendance.total_working_hours)

#                 # Save the attendance record
#                 attendance.save()
#                 print("Attendance record updated successfully.")
#             else:
#                 print("No attendance record found for today.")

#             # Log out the user
#                 logout(request)
#                 messages.success(request, "Logged out successfully")
#                 return redirect('/')

#         except Employee.DoesNotExist:
#             return JsonResponse({'error': 'No employee record found for the user'}, status=404)
#         except Exception as e:
#             print("An error occurred:", e)
#             return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

#     return redirect('/')


# def logout_user(request): #####working perfectly
#     if request.user.is_authenticated:
#         # Get the employee record
#         employee = Employee.objects.get(user=request.user)

#         # Fetch today's attendance record with no logout time
#         current_date = now().date()
#         attendance = Attendance.objects.filter(
#             eId=employee,
#             login_time__date=current_date,
#             logout_time__isnull=True
#         ).first()

#         if attendance:
#             # Get the logout location from the frontend (POST request)
#             logout_location = request.POST.get('logout_location', '')

#             # Update the logout details
#             logout_time = now()
#             attendance.logout_time = logout_time
#             print("attendance.logout_time:", attendance.logout_time)
#             attendance.logout_location = logout_location
#             print("attendance.logout_location:", attendance.logout_location)

#             # Calculate total working hours
#             if attendance.login_time:
#                 attendance.total_working_hours = logout_time - attendance.login_time
#                 print("attendance.total_working_hours:", attendance.total_working_hours)

#             # Save the attendance record
#             attendance.save()

#         # Log out the user
#         logout(request)
#         messages.success(request, "Logged out successfully")
#         return redirect('/')

#     return redirect('/')

from datetime import datetime
from django.utils.timezone import make_aware, now, localtime
from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import logout
from django.contrib import messages

def logout_user(request):
    """
    Handle user logout and redirect to login page
    Supports both GET and POST requests with proper CSRF protection
    """
    try:
        if request.user.is_authenticated:
            try:
                # Get employee record if it exists
                employee = Employee.objects.get(user=request.user)
                
                # Find attendance record for today without logout time
                current_date = now().date()
                attendance = Attendance.objects.filter(
                    eId=employee,
                    date=current_date,
                    logout_time__isnull=True
                ).first()
                
                # If a record exists, update it with logout information
                if attendance:
                    logout_location = request.POST.get('logout_location', '') if request.method == 'POST' else 'Direct logout'
                    
                    # Update logout details with timezone-aware datetime
                    logout_time = now()
                    attendance.logout_location = logout_location
                    attendance.logout_time = logout_time
                    attendance.status = "Completed"
                    
                    # Calculate total working hours
                    if attendance.login_time:
                        total_working_time = logout_time - attendance.login_time
                        attendance.total_working_hours = total_working_time
                    
                    # Save the updated Attendance record
                    attendance.save()
            except Employee.DoesNotExist:
                # User might be an admin without employee record
                pass
            
            # Log out the user
            logout(request)
            
            # Clear session completely
            request.session.flush()
    except Exception as e:
        # Ensure logout happens even if there are errors
        logout(request)
        request.session.flush()
        print(f"Error during logout: {e}")
    
    # Create response with cache-control headers
    response = redirect('login_user')
    response.set_cookie('clear_local_storage', 'true', max_age=10)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

# from django.http import JsonResponse
# from django.shortcuts import redirect
# from django.contrib.auth import logout
# from django.utils.timezone import now
# import json

# def logout_user(request):  ############working to extract logout location but error in database
#     if request.method == 'POST' and request.user.is_authenticated:
#         try:
#             # Parse the logout location
#             logout_location = request.POST.get('logout_location', '')
#             print("Logout location received:", logout_location)

#             # Fetch employee and attendance record
#             employee = Employee.objects.get(user=request.user)
#             current_date = now().date()
#             attendance = Attendance.objects.filter(
#                 eId=employee,
#                 login_time__date=current_date,
#                 logout_time__isnull=True
#             ).first()

#             if attendance:
#                 logout_time = now()
#                 attendance.logout_time = logout_time
#                 attendance.logout_location = logout_location
#                 if attendance.login_time:
#                     attendance.total_working_hours = (
#                         logout_time - attendance.login_time
#                     ).total_seconds() / 3600
#                 attendance.save()

#                 print("Attendance record updated:", attendance)

#             # Log out the user
#             logout(request)
#             return JsonResponse({'success': 'Logged out successfully'})
#         except Exception as e:
#             print("Error during logout:", str(e))
#             return JsonResponse({'error': 'An error occurred during logout'}, status=500)

#     return redirect('/')

def link_user_to_employee(request):
    """
    View to handle linking a user account to an employee record or creating a new employee record.
    This resolves the issue where a user can authenticate but has no linked employee record.
    """
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to perform this action.")
        return redirect('login_user')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, "Missing user ID.")
            return redirect('login_user')
            
        try:
            # Get the user object
            user = User.objects.get(id=user_id)
            
            # Check if we're creating a new employee record
            if request.POST.get('create_new') == 'true':
                # Create a new employee record
                try:
                    # Check if an employee with this eID already exists
                    if Employee.objects.filter(eID=request.POST.get('eID')).exists():
                        messages.error(request, f"An employee with ID {request.POST.get('eID')} already exists.")
                        return redirect('login_user')
                        
                    # Check if an employee with this email already exists
                    if Employee.objects.filter(email__iexact=request.POST.get('email')).exists():
                        messages.error(request, f"An employee with email {request.POST.get('email')} already exists.")
                        return redirect('login_user')
                    
                    employee = Employee(
                        user=user,
                        eID=request.POST.get('eID'),
                        firstName=request.POST.get('firstName'),
                        middleName=request.POST.get('middleName', ''),
                        lastName=request.POST.get('lastName'),
                        phoneNo=request.POST.get('phoneNo'),
                        email=request.POST.get('email'),
                        addharNo=request.POST.get('addharNo'),
                        dOB=request.POST.get('dOB'),
                        designation=request.POST.get('designation'),
                        salary=request.POST.get('salary'),
                        joinDate=request.POST.get('joinDate')
                    )
                    employee.save()
                    
                    messages.success(request, f"Successfully created employee record for {employee.firstName} {employee.lastName} and linked to your account!")
                    
                    # Log in again and redirect to dashboard
                    login(request, user)
                    return redirect('/ems/dashboard')
                    
                except Exception as e:
                    print(f"Error creating employee: {str(e)}")
                    messages.error(request, f"Error creating employee record: {str(e)}")
                    return redirect('login_user')
            else:
                # We're linking to an existing employee record
                employee_id = request.POST.get('employee_id')
                if not employee_id:
                    messages.error(request, "Missing employee ID.")
                    return redirect('login_user')
                
                try:
                    # Get the employee object using eID (case-sensitive)
                    employee = Employee.objects.get(eID=employee_id)
                    print(f"Found employee: {employee.eID} - {employee.firstName} {employee.lastName}")
                    
                    # Check if the employee already has a user account
                    if employee.user is not None and employee.user.id != user.id:
                        messages.error(request, f"Employee {employee.firstName} {employee.lastName} is already linked to another user account.")
                        return redirect('login_user')
                        
                    # Check if the user already has an employee record
                    if Employee.objects.filter(user=user).exists():
                        messages.error(request, "Your account is already linked to an employee record.")
                        return redirect('login_user')
                        
                except Employee.DoesNotExist:
                    messages.error(request, f"Employee with ID {employee_id} not found.")
                    return redirect('login_user')
                except Exception as e:
                    print(f"Error finding employee: {str(e)}")
                    messages.error(request, f"Error finding employee: {str(e)}")
                    return redirect('login_user')
                
                try:
                    # Link the employee to the user
                    employee.user = user
                    employee.save()
                    
                    messages.success(request, f"Successfully linked your account to {employee.firstName} {employee.lastName} (ID: {employee.eID})")
                    
                    # Log in again and redirect to dashboard
                    login(request, user)
                    return redirect('/ems/dashboard')
                    
                except Exception as e:
                    print(f"Error updating employee record: {str(e)}")
                    messages.error(request, f"Error updating employee record: {str(e)}")
                    return redirect('login_user')
            
        except User.DoesNotExist:
            messages.error(request, "User account not found.")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")
        
    return redirect('login_user')


def logout_user(request):
    """
    Handle user logout with proper CSRF protection
    Supports both GET and POST for easier logout functionality
    """
    # Whether GET or POST, process the logout if authenticated
    if request.user.is_authenticated:
        try:
            # Try to get employee record
            employee = Employee.objects.get(user=request.user)
            
            # Record logout time in attendance
            current_date = now().date()
            attendance = Attendance.objects.filter(
                eId=employee,
                date=current_date,
                logout_time__isnull=True
            ).first()
            
            if attendance:
                logout_time = now()
                attendance.logout_time = logout_time
                logout_location = request.POST.get('logout_location', 'Logout via system') if request.method == "POST" else 'Logout via direct link'
                attendance.logout_location = logout_location
                attendance.status = "Completed"
                
                # Calculate working hours
                if attendance.login_time:
                    working_time = logout_time - attendance.login_time
                    attendance.total_working_hours = working_time
                
                attendance.save()
        except Employee.DoesNotExist:
            # User might not have an employee record (e.g., admin)
            pass
        
    # Process the logout
    logout(request)
    
    # Ensure the session is completely cleared
    request.session.flush()
    request.session.clear_expired()
    
    # Delete the session cookie
    if 'sessionid' in request.COOKIES:
        response = redirect('login_user')
        response.delete_cookie('sessionid')
        return response
    
    # Redirect to login page
    messages.success(request, "You have been successfully logged out.")
    return redirect('login_user')
