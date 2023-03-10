from django.db import models
from django.contrib.auth.models import User
from jsonschema import ValidationError

# Create your models here.

# models to store the data of user roles. Role can be manager or employee. and foreignkey references to user model

class Role(models.Model):
    ROLES = (('manager', 0), ('employee', 1))
    role = models.IntegerField(choices=ROLES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return self.user.username

# Notification models. It has a foreignkey to user model to store the user who is notified
# and message field to store the message of the notification
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    message = models.TextField()

    def __str__(self):
        return self.user.username

# model to store team data. there's one team leader and many team members. team leader is a manager and team members are employees
class Team(models.Model):
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')
    team_members = models.ManyToManyField(User, related_name='team_members')

    def __str__(self):
        return self.team_leader.username

    # validation to make sure that only users with role manager can be team leader
    def clean(self):
        # filter role object to get role of team leader
        role = Role.objects.filter(user=self.team_leader)
        # if role is not manager, raise validation error
        if role[0].role != 0:
            raise ValidationError('Only managers can be team leaders')

# model to store the application for leave. it has a foreignkey to user model to store the user who applied for leave
# and foreignkey to team model to store the team of the user who applied for leave
class LeaveApplication(models.Model):
    STATUS_CHOICES = (('pending', 0), ('approved', 1), ('rejected', 2))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    
    def __str__(self):
        return self.user.username