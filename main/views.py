from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from main.models import *

# Create your views here.
def homePageView(request):
    # return httpresponse to say hello world
    return HttpResponse('Hello, World!') 


# submitLeaveApplication function to take application for leave
# takes only post request
# returns json response which contains status and message which are set based on the result of the function
def submitLeaveApplication(request):
    if request.method == 'POST':
        # get data from post request
        data = request.POST
        # get user from request
        user = request.user
        # get start date from request
        start_date = data.get('start_date')
        # get end date from request
        end_date = data.get('end_date')
        # get reason from request
        reason = data.get('reason')
        # create leave application object
        # get the team object where user is in team 

        leave_application = LeaveApplication.objects.create(user=user, team=team, start_date=start_date, end_date=end_date, reason=reason)
        # save leave application object
        leave_application.save()
        # return json response with status 200 and message 'Leave application submitted successfully'
        return JsonResponse({'status': 200, 'message': 'Leave application submitted successfully'})
    else:
        # return json response with status 400 and message 'Bad request'
        return JsonResponse({'status': 400, 'message': 'Bad request'})