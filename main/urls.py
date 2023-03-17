
from django.urls import path, include
from . import views
urlpatterns = [

    # ------------------ login urls ----------------------#
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path('', views.homePageView, name='home' ),
    # url to take application for leave
    path('/submit_leave_application', views.submitLeaveApplication, name='apply'),

    # ------------------- dashboard urls----------------------#
    path('admin_dashboard',views.admin_dashboard, name="admin_dashboard_url"),
    path('member_dashboard',views.member_dashboard, name="member_dashboard_url"),

    # ------------------- Team urls----------------------#
    path('admin_teamlist',views.admin_teamlist, name="admin_teamlist_url"),
    path('admin_addmembers',views.admin_addmembers, name="admin_addmembers_url"),

    # ------------------- Leave urls----------------------#
    path('admin_leave_list',views.admin_leavelist, name="admin_leave_list_url"),
    path('member_leave_application',views.member_leaveapplication, name="member_leave_application_url"),
    path('submitLeaveApplication',views.submitLeaveApplication, name="submitLeaveApplication_url"),
    path('approveLeaveApplication',views.approveLeaveApplication, name="approveLeaveApplication_url")  , 
    path('rejectLeaveApplication',views.rejectLeaveApplication, name="rejectLeaveApplication_url"),


    # ------------------- Ticket urls----------------------#
    path('raise_ticket',views.member_raise_ticket, name="member_raise_ticket_url"),
    path('my_ticket_list',views.member_tickets, name="member_tickets_url")
]
