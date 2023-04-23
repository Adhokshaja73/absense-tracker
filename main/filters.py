import django_filters
from .models import *
from django_filters import DateFilter, CharFilter, ChoiceFilter
from django import forms

class TicketFilter(django_filters.FilterSet):
    STATUS_CHOICES = ((0,'raised'), (1,'processing'), (2,'rejected'), (3,'closed'), (4,'Deleted'))
    status = ChoiceFilter(field_name="ticket_status", choices=STATUS_CHOICES,widget=forms.Select(attrs={"class":"form-control","type":"select"}))

    class Meta:
        model = TeamTicket
        fields = {
            'raised_date': [ 'gte', 'lte'],
            'ticket_number': [ 'icontains'],
            'raised_by__username':[ 'icontains']
            }
        

class LeaveFilter(django_filters.FilterSet):
    STATUS_CHOICES = ((1, 'pending'), (2,'approved'), (3, 'rejected'))
    status = ChoiceFilter(field_name="status", choices=STATUS_CHOICES,widget=forms.Select(attrs={"class":"form-control","type":"select"}))

    class Meta:
        model = LeaveApplication
        fields = {
            'applied_date': [ 'gte', 'lte'],
            'start_date': [ 'gte', 'lte' ],
            # 'end_date': [ 'gte', 'lte'],
            'user__username':[ 'icontains']
            }
        
 