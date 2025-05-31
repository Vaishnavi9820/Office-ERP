from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('',views.login_user,name="login_user"),
    path('logout/',views.logout_user,name="logout_user"),
    path('signup/',views.signup,name="signup"),
    path('link-user-to-employee/', views.link_user_to_employee, name="link_user_to_employee"),
]   

# # urlpatterns = [
# #     path('',views.employee_login,name="employee_login"),
# #     path('logout',views.employee_logout,name="employee_logout"),
# #     path('signup',views.signup,name="signup"),
# # ]   