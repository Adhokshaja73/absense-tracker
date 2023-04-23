from django.urls import path
from . import views

urlpatterns = [

    # ------------------ Account URLS ---------------------------------------------------
    path('create_user_profile/', views.create_user_profile, name='create_user_profile'),
    path('accounts/profile/', views.home, name='home_url'),

    # ------------------ Dashboard and leaves URLS ---------------------------------------------------
    path('', views.home, name='home'),
    path('submit_leave_application/', views.create_leave_application, name='submit_leave_application'),
    path('my_leave_list/', views.my_leave_list, name='my_leave_list'),
    path('approveLeave/', views.approve_leave_application, name='approveLeave'),
    path('leavereport',views.TL_leave_report, name='TL_leave_report_url' ),
    path('teamlist',views.team_list, name='team_list_url' ),

    # ------------------ Ticket URLs ---------------------------------------------------
    path('raise_ticket/', views.raise_ticket, name='raise_ticket'),
    path('my_tickets_list/', views.member_tickets_list, name='my_tickets_list_url'),
    path('rejectticket/<int:ticketid>/', views.reject_ticket, name='reject_ticket_url'),
    path('processticket/<int:ticketid>/', views.process_ticket, name='process_ticket_url'),
    path('ticketreport',views.TL_ticket_report, name='TL_ticket_report_url' ),
]
