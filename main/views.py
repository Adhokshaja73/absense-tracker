from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from main.models import *
from main.forms import *

from django.contrib.auth import login, authenticate,logout #add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm #add this

# --------------------  LOGIN and password reset views --------------------


def register_request(request):
	...

def login_request(request):
    temp = Roles.objects.all()
    print(temp)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                temprole = Roles.objects.filter(user=request.user.id).first()
                temp = Roles.objects.all()
                 #add this   
                print(temp)
                print(temprole)
                print(temprole.role)
                if temprole is None:
                    messages.info(request, f"You Dont have a role assigned! please contact your manager")
                    logout(request)
                    

                if temprole.role == 'Team_lead':      
                    messages.info(request, f"You are now logged in as {username}.Your role is Team lead ")
                    return redirect("admin_dashboard_url")
                elif temprole.role == 'team_member':
                    messages.info(request, f"You are now logged in as {username}.Your role is Team member")
                    return redirect("member_dashboard_url")
                
                    
        
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})


@login_required
def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")

# ----------------------- TEAM VIEWS -----------------------------
@login_required
def admin_teamlist(request):
    tempteam = Team.objects.filter(team_leader=request.user.id).first()
    print(tempteam)
    context = {'tempteam':tempteam}
    return render(request, 'team/admin_teamlist.html',context)

@login_required
def admin_addmembers(request):
    templist = User.objects.filter(id__in=Roles.objects.filter(role='team_member').values_list('user_id', flat=True))
    print(templist)
    context = {'templist':templist}
    return render(request, 'team/admin_addmembers.html',context)





# ------------------------DASHBOARD views ----------------------------
@login_required
def member_dashboard(request):
    return render(request, 'member_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')

def homePageView(request):
    
    return render(request,"index.html")


# ----------------------- LEAVES VIEWS -----------------------
@login_required
def admin_leavelist(request):
    templist = LeaveApplication.objects.filter(team_id__team_leader=request.user.id)
    print(templist) 
    context = {'templist':templist}

    return render(request, 'leaves/admin_leavelist.html',context)   


@login_required
def member_leaveapplication(request):
    return render(request, 'leaves/member_leaveapplication.html')

# FUNCTION TO TAKE APPLICATION FOR LEAVE

# submitLeaveApplication function to take application for leave
# and creates a notification for the team leader of the team of the user who applied for leave
# takes only post request
# returns json response which contains status and message which are set based on the result of the function

# required data to be sent in post request
# team_id: id of the team of the user who applied for leave
# start_date: start date of the leave
# end_date: end date of the leave
# reason: reason for the leave
@login_required
def submitLeaveApplication(request):
    if request.method == 'POST':
        # get data from post request
        data = request.POST
        # get user from request
        user = request.user
        # get team id from request
        team_id = data.get('team_id')
        # get team object from team id
        team = Team.objects.get(id=team_id)
        # get start date from request
        start_date = data.get('start_date')
        # get end date from request
        end_date = data.get('end_date')
        # get reason from request
        reason = data.get('reason')
        # create leave application object
        leave_application = LeaveApplication.objects.create(user=user, team=team, start_date=start_date, end_date=end_date, reason=reason)
        # save leave application object
        leave_application.save()
        # create notification object
        notification = Notification.objects.create(user=team.team_leader, message='You have a new leave application')
        # save notification object
        notification.save()
        # return json response with status 200 and message 'Leave application submitted successfully'
        return JsonResponse({'status': 200, 'message': 'Leave application submitted successfully'})
    else:
        # return json response with status 400 and message 'Bad request'
        return JsonResponse({'status': 400, 'message': 'Bad request'})



# FUNCTION TO APPROVE LEAVE APPLICATION

# approves leave application submitted by team members. Aprover must be a team leader of the team of the user who applied for leave
# and creates a notification for the user who applied for leave
# takes only post request
# returns json response which contains status and message which are set based on the result of the function 
# required data to be sent in post request
# leave_application_id: id of the leave application to be approved
def approveLeaveApplication(request):
    if request.method == 'POST':
        # get data from post request
        data = request.POST
        # get user from request
        user = request.user
        # get leave application id from request
        leave_application_id = data.get('leave_application_id')
        # get leave application object from leave application id
        leave_application = LeaveApplication.objects.get(id=leave_application_id)
        # get team object from leave application object
        team = leave_application.team
        # get team leader from team object
        team_leader = team.team_leader
        # check if user is team leader
        if user == team_leader:
            # set status of leave application to approved
            leave_application.status = 1
            # save leave application object
            leave_application.save()
            # create notification object
            notification = Notification.objects.create(user=leave_application.user, message='Your leave application has been approved')
            # save notification object
            notification.save()
            # return json response with status 200 and message 'Leave application approved successfully'
            return JsonResponse({'status': 200, 'message': 'Leave application approved successfully'})
        else:
            # return json response with status 400 and message 'You are not authorized to approve this leave application'
            return JsonResponse({'status': 400, 'message': 'You are not authorized to approve this leave application'})
    else:
        # return json response with status 400 and message 'Bad request'
        return JsonResponse({'status': 400, 'message': 'Bad request'})


# FUNCTION TO REJECT LEAVE APPLICATION
# rejects leave application submitted by team members. Aprover must be a team leader of the team of the user who applied for leave
# and creates a notification for the user who applied for leave
# takes only post request
# returns json response which contains status and message which are set based on the result of the function
# required data to be sent in post request
# leave_application_id: id of the leave application to be rejected
def rejectLeaveApplication(request):
    if request.method == 'POST':
        # get data from post request
        data = request.POST
        # get user from request
        user = request.user
        # get leave application id from request
        leave_application_id = data.get('leave_application_id')
        # get leave application object from leave application id
        leave_application = LeaveApplication.objects.get(id=leave_application_id)
        # get team object from leave application object
        team = leave_application.team
        # get team leader from team object
        team_leader = team.team_leader
        # check if user is team leader
        if user == team_leader:
            # set status of leave application to rejected
            leave_application.status = 2
            # save leave application object
            leave_application.save()
            # create notification object
            notification = Notification.objects.create(user=leave_application.user, message='Your leave application has been rejected')
            # save notification object
            notification.save()
            # return json response with status 200 and message 'Leave application rejected successfully'
            return JsonResponse({'status': 200, 'message': 'Leave application rejected successfully'})
        else:
            # return json response with status 400 and message 'You are not authorized to reject this leave application'
            return JsonResponse({'status': 400, 'message': 'You are not authorized to reject this leave application'})
    else:
        # return json response with status 400 and message 'Bad request'
        return JsonResponse({'status': 400, 'message': 'Bad request'})


# Create calender event function
# creates a calender event for all members of a team and creates a notification for all members of the team
# and sends an email to all members of the team
# can be called by other functions in the server only internal
# takes team object, start date, end date, title, description, location, and email subject as arguments
# returns true if successful and false if not
def createCalenderEvent(team, start_date, end_date, title, description, location, email_subject):
    # get all members of the team
    members = team.members.all()
    # loop through all members
    for member in members:
        # create calender event object
        calender_event = CalenderEvent.objects.create(user=member, start_date=start_date, end_date=end_date, title=title, description=description, location=location)
        # save calender event object
        calender_event.save()
        # create notification object
        notification = Notification.objects.create(user=member, message='You have a new calender event')
        # save notification object
        notification.save()
        # get email of the member
        email = member.email
        # get first name of the member
        first_name = member.first_name
        # get last name of the member
        last_name = member.last_name
        # get full name of the member
        full_name = first_name + ' ' + last_name
        # get email body
        email_body = 'Hi ' + full_name + ',\n\n' + description + '\n\n' + 'Start Date: ' + start_date + '\n' + 'End Date: ' + end_date + '\n' + 'Location: ' + location + '\n\n' + 'Regards,\n' + 'Team Management System'
        # send email
        # send_mail(email_subject, email_body, '


# ======================== TICKET VIEWS =================================================#

# view 01 - member raise ticket
def member_raise_ticket(request):
    form = TicketForm()

    if request.method == 'POST':
        tempform = form(request.POST)
        tempdata = tempform.dave(commit=False)
        tempdata.ticket_number = "232231"
        tempdata.raised_by = request.user
        tempdata.ticket_status = 0
        
        tempdata.save()

    context = {'form':form}
    return render(request, "member/member_raise_ticket.html", context)

# view 02 - member_tickets_list
def member_tickets(request):
    myticketsList  = TeamTicket.objects.filter(raised_by=request.user.id)

    context = {"tlist":myticketsList}
    return render(request, "member/member_tickets.html", context)