from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.db.models import Q
from django.contrib import messages
import random

from django.core import serializers
from main.filters import  TicketFilter, LeaveFilter

from team_management import settings

from django.core.mail import send_mail

def test(request):
    mail()
    return HttpResponse("Hello, world. You're at the polls index.")


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
        userTeam = Team.objects.filter(Q(team_leader = request.user) | Q(team_members = request.user)).first()
        if(userTeam == None):
            return render(request, 'error_page.html', {'message' : 'Team not assigned'})  
        else:
            
            # userTeam = userTeam[0]
            # get notifications of user
            notifications = Notification.objects.filter(user = request.user).values()
            # get calender events of team 
            calenderEvents = CalenderEvent.objects.filter(team = userTeam).values()

            leaveapplications = LeaveApplication.objects.filter(user = request.user)

            

        
            # get team member profiles
            teamMemberProfiles = []
            for i in  userTeam.team_members.values():
                try:
                    teamMemberProfiles.append(UserProfile.objects.filter(user = i['id']).get())
                    # teamMemberProfiles.append()
                    
                except:
                    pass

            # print(teamMemberProfiles)
            # granted leaves

            # get todays date time
            today = datetime.datetime.now()

            tempgrantedLeaves = LeaveApplication.objects.filter(team=userTeam, status = 2, end_date__gt=today).values()
            # tempgrantedLeaves = LeaveApplication.objects.filter(team=userTeam, status = 2).values()
            grantedLeaves = []

            # print(grantedLeaves.values())
            for each in tempgrantedLeaves.values():
                
               
                tempuser = UserProfile.objects.filter(user = each['user_id']).get()
                
                each['userProfileurl'] = tempuser
                
                grantedLeaves.append(each)
            # print("-----------------------after")
            # print(grantedLeaves.values)
            # print("ended---------------------")
        

            context = {'notifications' : notifications, 'calenderEvents' : calenderEvents, 'team_member_profiles' : teamMemberProfiles, 'leavApplicationForm' : form, 'userteam':userTeam, 'leaveapplications':leaveapplications, 'grantedLeaves':grantedLeaves}

            
            if(user_role.role == 1):
                # for team members send the user_dashboard page with context
                tickets = TeamTicket.objects.filter(team = userTeam, raised_by = request.user)
                context['tickets'] = tickets
                return render(request, 'dashboard/TM_dashboard.html', context)
                
            else:
                # get pending leave applications and add to context
                leaveApplications = LeaveApplication.objects.filter(team = userTeam, status = 1)
                teamtickets = TeamTicket.objects.filter(team = userTeam, ticket_status = 0)
                context['leaveApplications'] = leaveApplications
                context['tickets'] = teamtickets


                for each in leaveApplications:
                    tempprofile = UserProfile.objects.filter(user = each.user).get()

                    each.profileurl=tempprofile
                    
                return render(request, 'dashboard/TL_dashboard.html', context)
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
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            reason = form.cleaned_data['reason']
            # create leave application object
            user = request.user
            # TODO change this
            team =  Team.objects.filter(Q(team_leader = request.user) | Q(team_members = request.user)).first()
            leave_application = LeaveApplication(user=user, team=team,  start_date=start_date, end_date=end_date, reason=reason)
            leave_application.save()
            messages.success(request, 'Leave application created successfully')
            
            return redirect('home')
    else:
        form = LeaveApplicationForm()
        context = {'LeaveApplicationForm': form}
        return render(request, 'leaves/request_leave.html',context)

def my_leave_list(request):
    LeaveApplicationlist = LeaveApplication.objects.filter(user = request.user)
    context = {'LeaveApplicationlist': LeaveApplicationlist}
    return render(request, 'leaves/my_leave_list.html',context)

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
                print(leave_application_id)
                # get leave application
                leave_application = LeaveApplication.objects.filter(id=leave_application_id).first()
               
                if(not leave_application):
                    return JsonResponse({'status': 'error', 'message': 'Leave application not found'})
                else:
                    # leave_application = leave_application.get()
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
                                data  = leave_application.id
                                
                                leave_application.save()
                                # create notification for user
                                user = leave_application.user
                             
                                # create calender event for team if leave application is approved
                                # newleavelist = LeaveApplication.objects.filter(team=userTeam,status = 1)
                                # ser_instance = serializers.serialize('json', [ newleavelist, ])
                             
                                if(status == '2'):
                                    
                                    # calender_event = CalenderEvent(team=leave_application.team, title=leave_application.user.first_name + " " + leave_application.user.last_name + " is on leave", start_date=leave_application.start_date, end_date=leave_application.end_date)
                                    # calender_event.save()
                                    # notification = Notification(user=user, message="Your leave application has been approved")
                                    # notification.save()

                                    # TODO write code to send email to user
                                
                                    # data = serializers.serialize('json', list(newleavelist))
                                    return JsonResponse({"instance": data,'status': 'success', 'message': 'Leave application approved'})
                                else:
                                    
                                    notification = Notification(user=user, message="Your leave application has been rejected")
                                    notification.save()
                                    return JsonResponse({"instance": data,'status': 'success', 'message': 'Leave application rejected'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only post request allowed'})
    
# function

def TL_leave_report(request):
    leaveList = LeaveApplication.objects.filter(team__team_leader=request.user)

    userteam = Team.objects.filter(team_leader=request.user)
    tempfilteredlist = LeaveFilter(request.GET, queryset=LeaveApplication.objects.all())
    
    filteredlist = tempfilteredlist.qs.filter(team__team_leader=request.user)

    context = {'leavelist':leaveList,'filter': tempfilteredlist,'filteredlist':filteredlist}
    return render(request, 'leaves/TL_leave_report.html', context)

# function to send mail
def mail():
    
    stat = send_mail(
        subject='Add an eye-catching subject',
        message='Write an amazing message',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['your_friend@their_email.com'])
    
    print(stat)



# --------------------------------------------------------------------------
# ------------------------------ TICKET VIEWS ------------------------------

# ----- View to generate unique ticket number
def generate_ticket_num():
    ticket_num = random.randint(100000, 999999)
    while TeamTicket.objects.filter(ticket_number=ticket_num).exists():
        ticket_num = random.randint(100000, 999999)

    print(ticket_num)
    return ticket_num


# ----- view to create ticket by team member
def raise_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            # read the form data
            ticket_type = form.cleaned_data['ticket_type']
            issue_detail = form.cleaned_data['issue_detail']
            issue_date = form.cleaned_data['issue_date']
            ticket_num = generate_ticket_num()
            raised_by = request.user
            team = Team.objects.get(team_members=request.user)
            ticket = TeamTicket(ticket_type=ticket_type, issue_detail=issue_detail,
                                 issue_date=issue_date, ticket_number=ticket_num, 
                                 raised_by=raised_by, team=team)
            
            ticket.save()

            messages.success(request, 'Your Ticket has been raised successfully')
            return redirect('home')
    else:
        form = TicketForm()
    return render(request, 'tickets/raise_ticket.html', {'form': form})

def tl_tickets_list(request):
    ticketList = TeamTicket.objects.filter(team__team_leader=request.user)
    context = {'ticketList': ticketList}
    return render(request, 'tickets/TL_tickets_list.html', context)


def member_tickets_list(request):
    myTicketList = TeamTicket.objects.filter(raised_by=request.user)
    context = {'myTicketList': myTicketList}
    print(myTicketList)
    return render(request, 'tickets/my_tickets_list.html', context)

def reject_ticket(request,ticketid):
    ticket = TeamTicket.objects.get(id=ticketid)
    ticket.ticket_status = "2"
    ticket.save()
    print("ticekt rejected")
    return redirect('home')

def process_ticket(request,ticketid):

    ticket = TeamTicket.objects.get(id=ticketid)
    
    tempuser = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        # temp_comments = request.POST['comment']
        temp_comments = request.POST.get('comment')
        ticket.comments=temp_comments
        ticket.response_date= datetime.datetime.now()
        ticket.response_by=tempuser.user
        ticket.ticket_status = 2 
        ticket.save()
        print(ticket.response_by)

        messages.success(request, 'Ticket has been processed successfully')

        # send mail here
        return redirect('home')
    context = {'ticket': ticket, 'tempuser': tempuser}

    print("ticekt accepted")
    return render(request, 'tickets/TL_process_ticket.html', context)

def TL_ticket_report(request):
    ticketList = TeamTicket.objects.filter(team__team_leader=request.user)
    userteam = Team.objects.filter(team_leader=request.user)
    filteredlist = TicketFilter(request.GET, queryset=TeamTicket.objects.all())
    

    context = {'tlist':ticketList,'filter': filteredlist}
    return render(request, 'tickets/TL_ticket_report.html', context)

def team_list(request):
    teamlist = Team.objects.filter(team_leader=request.user).first()
    teamstat = {}
    teamstat['membercount'] = teamlist.team_members.count()
    teamstat['onleavetoday'] = LeaveApplication.objects.filter(team=teamlist, start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today()).count()
    teamstat['onleavemembers'] = LeaveApplication.objects.filter(team=teamlist, start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())
    teamstat['teammembers'] = teamlist.team_members.all()

    memprofile = UserProfile.objects.filter(user__in=teamstat['teammembers'])
    print(teamstat)
    context = {'teamlist': teamlist, 'teamstat': teamstat, 'memprofile': memprofile}
    return render(request, 'dashboard/teamlist.html', context)



