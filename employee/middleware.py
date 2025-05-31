from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import Attendance

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            
            # If there's no last activity, set it now
            if not last_activity:
                request.session['last_activity'] = timezone.now().isoformat()
                return self.get_response(request)
            
            try:
                last_activity = datetime.fromisoformat(last_activity)
                
                # Check if user has been inactive for more than 90 days
                if timezone.now() > last_activity + timedelta(days=90):
                    # Log out user and update attendance
                    try:
                        attendance = Attendance.objects.filter(
                            eId=request.user.employee,
                            logout_time__isnull=True
                        ).latest('login_time')
                        attendance.logout_time = last_activity
                        attendance.save()
                    except Attendance.DoesNotExist:
                        pass
                    
                    # Clear session and cookies
                    logout(request)
                    response = redirect('login')
                    response.delete_cookie('remember_user')
                    messages.info(request, "Session expired due to inactivity.")
                    return response
                else:
                    # Update last activity timestamp if not on static files
                    if not request.path.startswith('/static/'):
                        request.session['last_activity'] = timezone.now().isoformat()
            except (ValueError, TypeError):
                # If there's any error with the last_activity timestamp, reset it
                request.session['last_activity'] = timezone.now().isoformat()
        
        response = self.get_response(request)
        return response 