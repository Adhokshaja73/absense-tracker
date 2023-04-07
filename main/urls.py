from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_user_profile/', views.create_user_profile, name='create_user_profile'),
    path('accounts/profile/', views.home, name='home')

]
