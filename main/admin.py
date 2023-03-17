from django.contrib import admin
from .models import TeamTicket, Ticket_type, Roles, Team


admin.site.register(TeamTicket)
admin.site.register(Ticket_type)
admin.site.register(Roles)
admin.site.register(Team)
# Register your models here

