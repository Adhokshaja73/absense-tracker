from django.shortcuts import render, redirect, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.db.models import Q
# Create your views here.
# function to return homepage of the user
# first check if user is logged in, if not redirect to login page
# if user is logged in, check if user is team leader or team member
# return the appropriate homepage
@login_required
def home(request):
    # check if user profile exists
    # if not redirect to create_user_profile page
    user_profile = UserProfile.objects.filter(user=request.user)
    form = LeaveApplicationForm()
    if (not user_profile.exists()):
        return redirect('create_user_profile')
    
    # filter user role by user id
    user_role = UserRole.objects.filter(user=request.user)
    # if user role doesnt exist, return error page with message : "User role not defined" page
    if (not user_role.exists()):
        return render(request, 'error_page.html', {'message': 'User role not defined'})
    
    
    else:
        user_role = user_role.get()
        userTeam = Team.objects.filter(Q(team_leader = request.user) | Q(team_members = request.user))
        if(not userTeam.exists()):
            return render(request, 'error_page.html', {'message' : 'Team not assigned'})  
        else:
            print(userTeam)
            userTeam = userTeam[0]
            # get notifications of user
            notifications = Notification.objects.filter(user = request.user).values()
            # get calender events of team 
            calenderEvents = CalenderEvent.objects.filter(team = userTeam).values()
            # get team member profiles
            teamMemberProfiles = []
            for i in  userTeam.team_members.values():
                try:
                    teamMemberProfiles.append(UserProfile.objects.filter(user = i['id']).get())
                    # teamMemberProfiles.append()
                except:
                    pass

            # print(teamMemberProfiles)
            context = {'notifications' : notifications, 'calenderEvents' : calenderEvents, 'team_member_profiles' : teamMemberProfiles, 'leavApplicationForm' : form}

            
            if(user_role.role == 1):
                # for team members send the user_dashboard page with context
                return render(request, 'user_dashboard.html', context)
                
            else:
                # get pending leave applications and add to context
                leaveApplications = LeaveApplication.objects.filter(team = userTeam, status = 1).values()
                context['leaveApplications'] = leaveApplications
                return render(request, 'team_leader_dashboard.html', context)
# function to create userProfile. 
# if request is post then the form is validated and saved
# if request is get then the form is returned in context
@login_required
def create_user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # read the form data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            email = form.cleaned_data['email']
            profilePhoto = form.cleaned_data['profilePicture']
            # create user profile object
            user = request.user
            user_profile = UserProfile(user=user, first_name=first_name, last_name=last_name, phone_number=phone_number, address=address, email=email, profilePicture=profilePhoto)
            user_profile.save()
            return redirect('home')
    else:
        form = UserProfileForm()
    return render(request, 'create_user_profile.html', {'form': form})

# function to create leave application
# if request is post then the form is validated and saved
# if request is get then the form is returned in context
@login_required
def create_leave_application(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            # read the form data
            leave_type = form.cleaned_data['leave_type']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            reason = form.cleaned_data['reason']
            # create leave application object
            user = request.user
            # TODO change this
            team = Team.objects.get(team_members=user)
            leave_application = LeaveApplication(user=user, team=team, leave_type=leave_type, start_date=start_date, end_date=end_date, reason=reason)
    
    else:
        form = LeaveApplicationForm()
    return render(request, 'create_leave_application.html', {'form': form})



# function to approve or reject leave application
# takes only post request
# only the team leader can approve leave application
# only pending leave applications can be approved
# only the team leader of the team to which the leave application belongs can approve the leave application
# parameters : leave application id, status (1 for approve, 0 for reject)
# change status of leave application to approved or rejected
# create notification for user
# create calender event for team if leave application is approved with title saying user name is on leave for the day of the leave application
# returns : json response on status
@login_required
def approve_leave_application(request):
    if request.method == 'POST':
        # check if user is team leader
        user_role = UserRole.objects.filter(user=request.user)
        if (not user_role.exists()):
            return JsonResponse({'status': 'error', 'message': 'User role not defined'})
        else:
            user_role = user_role.get()
            if(user_role.role == 1):
                return JsonResponse({'status': 'error', 'message': 'Only team leader can approve leave application'})
            else:
                # get leave application id and status
                leave_application_id = request.POST.get('leave_application_id')
                status = request.POST.get('status')
                # get leave application
                leave_application = LeaveApplication.objects.filter(id=leave_application_id)
                if(not leave_application.exists()):
                    return JsonResponse({'status': 'error', 'message': 'Leave application not found'})
                else:
                    leave_application = leave_application.get()
                    # check if leave application is pending
                    if(leave_application.status != 1):
                        return JsonResponse({'status': 'error', 'message': 'Leave application is not pending'})
                    else:
                        # check if team leader is the team leader of the team to which the leave application belongs
                        userTeam = Team.objects.filter(Q(team_leader = request.user) | Q(team_members = request.user))
                        if(not userTeam.exists()):
                            return JsonResponse({'status': 'error', 'message': 'Team not assigned'})  
                        else:
                            userTeam = userTeam[0]
                            if(userTeam != leave_application.team):
                                return JsonResponse({'status': 'error', 'message': 'You are not the team leader of the team to which the leave application belongs'})
                            else:
                                # change status of leave application
                                leave_application.status = status
                                leave_application.save()
                                # create notification for user
                                user = leave_application.user
                                # create calender event for team if leave application is approved
                                if(status == 1):
                                    calender_event = CalenderEvent(team=leave_application.team, title=leave_application.user.first_name + " " + leave_application.user.last_name + " is on leave", start_date=leave_application.start_date, end_date=leave_application.end_date)
                                    calender_event.save()
                                    notification = Notification(user=user, message="Your leave application has been approved")
                                    notification.save()

                                    # TODO write code to send email to user

                                    return JsonResponse({'status': 'success', 'message': 'Leave application approved'})
                                else:
                                    notification = Notification(user=user, message="Your leave application has been rejected")
                                    notification.save()
                                    return JsonResponse({'status': 'success', 'message': 'Leave application rejected'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only post request allowed'})
    