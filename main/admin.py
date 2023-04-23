from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserRole)
admin.site.register(Team)
admin.site.register(UserProfile)
admin.site.register(LeaveApplication)

admin.site.register(TeamTicket)
admin.site.register(Ticket_type)
