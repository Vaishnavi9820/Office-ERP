# from django.urls import path
# from . import views

# # urlpatterns = [
# #     path('', views.home, name="home"),
# #     path('work', views.work, name="work"),
# #     path('request', views.request, name="request"),
# #     path('notice', views.notice, name="notice"),
# #     path('attendance', views.attendance, name="attendance"),
# # ]   
# urlpatterns = [
#     path('dashboard',views.dashboard,name="dashboard"),
#     path('attendance',views.attendance,name="attendance"),
#     path('notice',views.notice,name="notice"),
#     path('noticedetail/?P<id>/',views.noticedetail,name="noticedetail"),
#     path('assignwork',views.assignWork,name="assignwork"),
#     path('mywork',views.mywork,name="mywork"),
#     path('workdetails/?P<wid>/',views.workdetails,name="workdetails"),
#     path('editAW/', views.assignedworklist, name='assignedworklist'),
#     path('deletework/?P<wid>/',views.deletework,name="deletework"),
#     path('updatework/?P<wid>',views.updatework,name="updatework"),
#     path('make_request/', views.make_request, name='make_request'),
#     # path('makeRequest', views.makeRequest, name="makeRequest"),
#     # path('viewRequest',views.viewRequest,name="viewRequest"),
#     path('requestdetails/?P<rid>/',views.requestdetails,name="requestdetails"),
#     # path('makeRequest', views.makeRequest, name="makeRequest"),
#     # path('make_request/', views.make_request, name='make_request'),
#     path('admin/expenditure_requests/', views.admin_expenditure_requests, name='admin_expenditure_requests'),
#     path('admin/handle_expenditure_request/<int:pk>/', views.handle_expenditure_request, name='handle_expenditure_request'),
#     path('admin/handle_leave_request/<int:pk>/', views.handle_leave_request, name='handle_leave_request'),
#     path('admin/handle_other_request/<int:pk>/', views.handle_other_request, name='handle_other_request'),
#     # path('admin/requests', views.admin_requests, name="admin_requests"),
#     # path('admin/approve_request/<int:request_id>/<str:request_type>/', views.approve_request, name="approve_request"),
#     # path('admin/hold_request/<int:request_id>/<str:request_type>/', views.hold_request, name="hold_request"),
#     # path('admin/delete_request/<int:request_id>/<str:request_type>/', views.delete_request, name="delete_request"),
    
# ]

################################################################
# 23/12/24 above code is working
###############################################################3
from django.urls import path
from . import views
from .views import request_page
# from employee.views import make_request_view, check_request_status

# urlpatterns = [
#     path('', views.home, name="home"),
#     path('work', views.work, name="work"),
#     path('request', views.request, name="request"),
#     path('notice', views.notice, name="notice"),
#     path('attendance', views.attendance, name="attendance"),
# ]   
urlpatterns = [
    # path('',views.login_user,name="login_user"),
    # path('logout',views.logout_user,name="logout_user"),
    # path('signup',views.signup,name="signup"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('attendance',views.attendance,name="attendance"),
    path('attendance-summary/', views.attendance_summary, name='attendance_summary'),
    # path('attendance', views.attendance_summary, name='attendance'),
    path('notice',views.notice,name="notice"),
    path('noticedetail/?P<id>/',views.noticedetail,name="noticedetail"),
    # path('assignwork',views.assignWork,name="assignwork"),
    # path('mywork',views.mywork,name="mywork"),
    # path('workdetails/?P<wid>/',views.workdetails,name="workdetails"),
    path('editAW/', views.assignedworklist, name='assignedworklist'),
    path('deletework/?P<wid>/',views.deletework,name="deletework"),
    # path('updatework/?P<wid>',views.updatework,name="updatework"),
    path('make_request/', views.make_request, name='make_request'),
    # path('makeRequest', views.makeRequest, name="makeRequest"),
    # path('viewRequest',views.viewRequest,name="viewRequest"),
    path('requestdetails/?P<rid>/',views.requestdetails,name="requestdetails"),
    # path('makeRequest', views.makeRequest, name="makeRequest"),
    # path('make_request/', views.make_request, name='make_request'),
    path('admin/expenditure_requests/', views.admin_expenditure_requests, name='admin_expenditure_requests'),
    path('admin/handle_expenditure_request/<int:pk>/', views.handle_expenditure_request, name='handle_expenditure_request'),
    path('admin/handle_leave_request/<int:pk>/', views.handle_leave_request, name='handle_leave_request'),
    path('admin/handle_other_request/<int:pk>/', views.handle_other_request, name='handle_other_request'),
    path('expenditure_requests/', views.make_expenditure_request, name='expenditure_requests'),
    path('user_notifications/',views.user_notifications,name="user_notifications"),
    path('assign_task/', views.assign_task, name='assign_task'),
    path('my_work/', views.my_work, name='my_work'),
    path('workdetails/<int:wid>/', views.work_details, name='workdetails'),  # New URL for work details
    path('mark_task_completed/<int:task_id>/', views.mark_task_completed, name='mark_task_completed'),  # New URL pattern
    path('requests/', request_page, name='request_page'),
    path('all-requests/', views.view_all_requests, name='view_all_requests'),  # New URL for viewing all requests
    # path('make-request/', make_request_view, name='make_request'),
    # path('check-request-status/', check_request_status, name='check_request_status'),


    # path('assignwork/', views.assignWork, name='assignwork'),
    # path('my_work/', views.my_work, name='my_work'),
    # path('admin/requests', views.admin_requests, name="admin_requests"),
    # path('admin/approve_request/<int:request_id>/<str:request_type>/', views.approve_request, name="approve_request"),
    # path('admin/hold_request/<int:request_id>/<str:request_type>/', views.hold_request, name="hold_request"),
    # path('admin/delete_request/<int:request_id>/<str:request_type>/', views.delete_request, name="delete_request"),
    
]