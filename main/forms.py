from django.forms import ModelForm
from .models import *

# form to create user profile
class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'email', 'profilePicture']

# form to create leave application
class LeaveApplicationForm(ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['start_date', 'end_date', 'reason']