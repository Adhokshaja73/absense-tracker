from django.forms import ModelForm
from .models import *

class TicketForm(ModelForm):
    class Meta:
        model = TeamTicket
        fields = ['ticket_type','issue_detail']

