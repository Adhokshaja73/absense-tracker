
from django.urls import path
from . import views
urlpatterns = [
    path('', views.homePageView, name='home' ),
    # url to take application for leave
    path('/submit_leave_application', views.submitLeaveApplication, name='apply'),

]
