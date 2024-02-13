import os
from django.shortcuts import get_object_or_404, render,redirect
from .forms import *
from .models import Scholarships
from django.contrib.auth.decorators import login_required
from datetime import datetime,date
from .models import Scholarships, Bookmark
from userprofile.models import UserProfile  
from .models import ScholarshipApplication

# Create your views here.


@login_required
def add_scholarship(request):
    if request.method == "POST":
        form = ScholarshipAdditionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_scholarships_view') 
        else:
            print(form.errors)
    else:
        form = ScholarshipAdditionForm()

    return render(request, "add_scholarship.html", {"form": form})

@login_required
def scholarships_list(request):
    today = date.today()
    scholarships = Scholarships.objects.all()

    # Retrieve the search query parameters from the request
    search_name = request.GET.get('name')
    search_description = request.GET.get('description')
    search_deadline = request.GET.get('deadline')

    # Filtering scholarships based on search criteria
    if search_name:
        scholarships = scholarships.filter(name__icontains=search_name)
    if search_description:
        scholarships = scholarships.filter(description__icontains=search_description)
    if search_deadline:
        try:
            # Assuming the search query is a date string in YYYY-MM-DD format
            search_deadline = datetime.strptime(search_deadline, '%Y-%m-%d').date()
            scholarships = scholarships.filter(application_deadline=search_deadline)
        except ValueError:
            # Handle invalid date format
            pass
    for scholarship in scholarships:
        scholarship.has_applied = ScholarshipApplication.objects.filter(scholarship=scholarship).exists()
        scholarship.has_approved = ApprovedScholarship.objects.filter(original_application__scholarship=scholarship).exists()
        scholarship.has_expired = scholarship.application_deadline.date() < datetime.now().date()

    return render(request, "scholarship_list.html", {"scholarships": scholarships})
@login_required
def admin_scholarships_view(request):
    scholarships=Scholarships.objects.all()
    return render(request,"admin_scholarships_view.html",{ "scholarship":scholarships})


@login_required
def edit_scholarship(request, id):  
    scholarship = Scholarships.objects.get(id=id)
    if request.method == "POST":
        form = ScholarshipAdditionForm(request.POST, request.FILES, instance=scholarship)
        if form.is_valid():
            form.save()       
    else:
        form = ScholarshipAdditionForm(instance=scholarship)

    return render(request, 'edit_scholarship.html', {"form": form})
@login_required
def remove_scholarship(request, id):
    scholarship = Scholarships.objects.get(id=id)

    if request.method == "POST":
        scholarship.delete()

        return redirect('admin_scholarships_view')  
    else:
        return render(request, 'remove_scholarship.html', {'scholarship': scholarship})
@login_required
def apply_scholarship(request):
    if request.method == 'POST':
        form = ScholarshipApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('scholarships')  
    else:
        form = ScholarshipApplicationForm()

    return render(request, 'apply_scholarship.html', {'form': form})
@login_required
def applicants_list(request):
    scholarship_applications = ScholarshipApplication.objects.all()
    return render(request, 'applicants_list.html', {'scholarship_applications': scholarship_applications})

@login_required
def approve_scholarship(request, id):
    # Get the scholarship application or return a 404 response if not found
    application = get_object_or_404(ScholarshipApplication, id=id)

    # Check if the application is not already approved
    if not application.is_approved:
        # Mark the original application as approved
        application.is_approved = True
        application.save()

        # Create a corresponding entry in the ApprovedScholarship model
        ApprovedScholarship.objects.create(original_application=application)

    # Redirect to the list of applicants after approval
    return redirect('applicants_list')
@login_required
def approved_list(request):
    approved_applications = ApprovedScholarship.objects.all()
    return render(request, 'approved_list.html', {'approved_applications': approved_applications})

@login_required
def bookmark_scholarship(request):
    try:
        scholarship = Scholarships.objects.all()
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Check if the scholarship is already bookmarked by the user
        if user_profile.bookmarks.filter(scholarship=scholarship).exists():
            # Scholarship is already bookmarked, no need to create a new bookmark
            pass
        else:
            # Scholarship is not bookmarked, create a new bookmark
            Bookmark.objects.create(user=user_profile, scholarship=scholarship)
    except Scholarships.DoesNotExist:
        # Handle case where scholarship with given ID does not exist
        pass
    
    # Retrieve all bookmarked scholarships for the user
    bookmarked_scholarships = user_profile.bookmarks.all()

    # Pass the bookmarked scholarships to the template context
    return render(request, 'bookmark.html', {'bookmarked_scholarships': bookmarked_scholarships}) # Assuming 'bookmarks' is the URL name for the bookmarks page
@login_required
def bookmarks(request):
    user_profile = UserProfile.objects.get(user=request.user)
    bookmarked_scholarships = user_profile.bookmarks.all()
    return render(request, 'bookmark.html', {'user_profile': user_profile, 'bookmarked_scholarships': bookmarked_scholarships})


@login_required
def application_history(request):
    # Retrieve the UserProfile instance associated with the current user
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Retrieve all scholarship applications made by the current user
    user_applications = ScholarshipApplication.objects.filter(user=user_profile)
    
    # Optionally, you can order the applications by submission date or any other relevant field
    user_applications = user_applications.order_by('-created_at')

    return render(request, 'application_history.html', {'user_applications': user_applications})

@login_required
def approved_scholarships(request):
    try:
        # Retrieve UserProfile instance associated with the current user
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Retrieve approved scholarships for the current user
        user_approved_scholarships =ScholarshipApplication.objects.filter(
            user=user_profile,  # Filter by user profile
            is_approved=True  # Filter by approval status
        )
    except UserProfile.DoesNotExist:
        # Handle case where UserProfile instance does not exist
        user_approved_scholarships = []

    return render(request, 'approved_application.html', {'approved_scholarships': user_approved_scholarships})