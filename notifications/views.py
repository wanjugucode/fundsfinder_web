from datetime import datetime, timedelta
from django.utils import timezone
from userprofile.models import UserProfile
from scholarships.models import ApprovedScholarship, Scholarships
from .models import Notification

def send_new_scholarship_notifications():
    latest_notification_id = Notification.objects.latest('id').id if Notification.objects.exists() else 0
    new_scholarships = Scholarships.objects.filter(id__gt=latest_notification_id)
    if new_scholarships.exists():
        message = f"{new_scholarships.count()} new scholarships have been added. Check them out now!"
        all_userprofiles = UserProfile.objects.all()
        for userprofile in all_userprofiles:
            Notification.objects.create(userprofile=userprofile, message=message)


def send_upcoming_deadline_notifications():
    deadline_threshold = timezone.now() + timedelta(hours=72)
    upcoming_deadlines = Scholarships.objects.filter(application_deadline__lte=deadline_threshold)
    
    print(f"Upcoming Deadlines: {upcoming_deadlines}")  # Debug statement
    
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
