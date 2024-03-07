from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from userprofile.models import UserProfile
from scholarships.models import ApprovedScholarship, Scholarships
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import  Notification

def send_new_scholarship_notification(scholarship_id, user_id):
    scholarship = Scholarships.objects.get(id=scholarship_id)
    message = f"A new scholarship '{scholarship.title}' has been added. Check it out now!"
     # Create a notification for the logged-in user
    userprofile = UserProfile.objects.get(user_id=user_id)
    Notification.objects.create(userprofile=userprofile, message=message)
    # Send notification over WebSockets to the logged-in user only
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "message": message
        }
    )


def send_upcoming_deadline_notifications():
    deadline_threshold = timezone.now() + timedelta(hours=72)
    upcoming_deadlines = Scholarships.objects.filter(application_deadline__lte=deadline_threshold)
    print(f"Upcoming Deadlines: {upcoming_deadlines}") 
    for scholarship in upcoming_deadlines:
        message = f"The application deadline for {scholarship.name} is approaching. Apply now!"  
        if scholarship.applications.exists():
            for application in scholarship.applications.all():
                Notification.objects.create(userprofile=application.userprofile, message=message)
                print(f"Notification sent to user {application.userprofile.user.username}: {message}")
        else:
            print(f"No applications found for scholarship: {scholarship.name}")

            
            
def send_approval_notifications():
    today = timezone.now().date()
    approved_applications = ApprovedScholarship.objects.filter(approval_date__date=today)
    for approved_application in approved_applications:
        scholarship_name = approved_application.original_application.scholarship.name if approved_application.original_application.scholarship else "Unknown Scholarship"
        message = f"Congratulations! Your application for {scholarship_name} has been approved."
        Notification.objects.create(userprofile=approved_application.original_application.userprofile, message=message)
        print(f"Approval notification sent to user {approved_application.original_application.userprofile.user.username}: {message}")

def notifications_view(request):
    notifications = Notification.objects.all() 
    return render(request, 'new_scholarship_notifications.html', {'notifications': notifications})