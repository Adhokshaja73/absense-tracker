from django.db import models
from django.contrib.auth.models import User
from jsonschema import ValidationError

# Create your models here.

# models to store the data of user roles. Role can be manager or employee. and foreignkey references to user model

class Role(models.Model):
    ROLES = (('manager', '0'), ('employee', '1'))
    role = models.IntegerField(choices=ROLES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return self.user.username
    
class Roles(models.Model):
    ROLES = (('Team_lead', 'Team_lead'), ('team_member', 'team_member'))
    role = models.CharField( choices=ROLES, max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rolesfk')

    def __str__(self):
        return self.user.username

# Notification models. It has a foreignkey to user model to store the user who is notified
# and message field to store the message of the notification
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_user')
    message = models.TextField()

    def __str__(self):
        return self.user.username

# model to store team data. there's one team leader and many team members. team leader is a manager and team members are employees
class Team(models.Model):
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')
    team_members = models.ManyToManyField(User, related_name='team_members')
    team_name = models.CharField(verbose_name="Team name",max_length=30)

    def __str__(self):
        return self.team_name

    # validation to make sure that only users with role manager can be team leader
    def clean(self):
        # filter role object to get role of team leader
        role = Roles.objects.filter(user=self.team_leader.id).first()

        # if role is not manager, raise validation error
        if role.role != "Team_lead":
            raise ValidationError('Only managers can be team leaders')

# model to store the application for leave. it has a foreignkey to user model to store the user who applied for leave
# and foreignkey to team model to store the team of the user who applied for leave
class LeaveApplication(models.Model):
    STATUS_CHOICES = (('pending', 0), ('approved', 1), ('rejected', 2))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='la_user')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    
    def __str__(self):
        return self.user.username
    

# ---------------------------- Tickets model -----------------------------


class Ticket_type(models.Model):
    ticket_type_name = models.CharField(max_length=30, verbose_name="Ticket-type name")
    ticket_type_desc = models.TextField(verbose_name="Description")
    ticket_type_active = models.BooleanField(default=True)

    def __str__(self):
        return self.ticket_type_name

class TeamTicket(models.Model):
    STATUS_CHOICES = (('raised', 0), ('processing', 1), ('rejected', 2), ('closed',3))

    ticket_number = models.CharField(max_length=10,null=True, blank=True,verbose_name="Ticket number")

    ticket_type = models.ForeignKey(Ticket_type,on_delete=models.CASCADE, related_name='ticket_type' , verbose_name="Ticket type")
    raised_date = models.DateTimeField(auto_now_add=True, verbose_name="Raised Date")
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_user')
    issue_detail = models.TextField(verbose_name="Issue Details")

    response_date = models.DateTimeField(auto_now_add=False,null=True, blank=True, verbose_name="Response date")
    response_by = models.ForeignKey( User,on_delete=models.CASCADE,null=True, blank=True,verbose_name="Response by")
    comments = models.TextField(null=True, blank=True,verbose_name="comments by Teamlead")

    ticket_status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    closed_date = models.DateTimeField(auto_now_add=False,null=True, blank=True, verbose_name="Closed date")

    def __str__(self):
        return self.ticket_number

