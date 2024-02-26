from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from notifications.models import Notification
from .forms import *
from .models import Scholarships
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime,date
from .models import *
from userprofile.models import UserProfile  


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
            search_deadline = datetime.strptime(search_deadline, '%Y-%m-%d').date()
            scholarships = scholarships.filter(application_deadline=search_deadline)
        except ValueError:
            pass
    
    scholarship_data = []
    for scholarship in scholarships:
        scholarship.has_applied = ScholarshipApplication.objects.filter(scholarship=scholarship).exists()
        scholarship.has_approved = ApprovedScholarship.objects.filter(original_application__scholarship=scholarship).exists()
        scholarship.has_expired = scholarship.application_deadline.date() < datetime.now().date()
        # Fetch comments and ratings for each scholarship
        comments = ScholarshipComment.objects.filter(scholarship=scholarship)
        ratings = ScholarshipRating.objects.filter(scholarship=scholarship)
        scholarship_data.append({
            'scholarship': scholarship,
            'comments': comments,
            'ratings': ratings
        })

    user_profile = None
    if hasattr(request.user, 'userprofile'):
        user_profile = request.user.userprofile

    context = {
        'scholarship_data': scholarship_data,
        'notifications': Notification.objects.filter(userprofile=user_profile)
    }
    return render(request, 'scholarship_list.html', context)


@login_required
def admin_scholarships_view(request):
    scholarships = Scholarships.objects.all()
    return render(request, "admin_scholarships_view.html", { "scholarships": scholarships})

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
            # Retrieve the UserProfile instance associated with the logged-in user
            user_profile = request.user.userprofile  # Assuming 'userprofile' is the ForeignKey field linking User and UserProfile
            # Create a new instance of ScholarshipApplication with the form data
            application = form.save(commit=False)
            # Associate the application with the user's profile
            application.userprofile = user_profile  # Assuming 'userprofile' is the ForeignKey field in ScholarshipApplication

            # Save the application only if a scholarship is selected in the form
            if application.scholarship:
                application.save()
                return redirect('scholarships')  # Redirect to a success page or another appropriate location
            else:
                # Add error handling for case where no scholarship is selected
                form.add_error('scholarship', 'Please select a scholarship.')
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

def bookmark_scholarship(request, scholarship_id):
    try:
        # Retrieve the scholarship based on the provided scholarship_id
        scholarship = get_object_or_404(Scholarships, id=scholarship_id)
        user_profile = UserProfile.objects.get(user=request.user)
        # Check if the scholarship is already bookmarked by the user
        if user_profile.bookmarks.filter(scholarship=scholarship).exists():
            # Scholarship is already bookmarked, no need to create a new bookmark
            pass
        else:
            # Scholarship is not bookmarked, create a new bookmark
            Bookmark.objects.create(userprofile=user_profile, scholarship=scholarship)
    except Scholarships.DoesNotExist:
        # Handle case where scholarship with given ID does not exist
        pass
    # Redirect back to the bookmarks page
    return redirect('bookmarks')

@login_required
def bookmarks(request):
    user_profile = UserProfile.objects.get(user=request.user)
    bookmarked_scholarships = user_profile.bookmarks.all()
    return render(request, 'bookmark.html', {'user_profile': user_profile, 'bookmarked_scholarships': bookmarked_scholarships})

@login_required
def application_history(request):
    try:
        # Retrieve all scholarship applications
        all_applications = ScholarshipApplication.objects.all()

        # Optionally, you can order the applications by submission date or any other relevant field
        all_applications = all_applications.order_by('-created_at')

        # Get the user object associated with the current user profile
        user = request.user

        return render(request, 'application_history.html', {'user_applications': all_applications, 'user': user})
    except ScholarshipApplication.DoesNotExist:
        # Handle case where no scholarship applications exist
        return HttpResponse("No scholarship applications found.")

@login_required
def approved_scholarships(request):
    try:
        # Retrieve UserProfile instance associated with the current user
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Retrieve approved scholarships for the current user
        user_approved_scholarships =ScholarshipApplication.objects.filter(
            userprofile=user_profile,  # Filter by user profile
            is_approved=True  # Filter by approval status
        )
    except UserProfile.DoesNotExist:
        # Handle case where UserProfile instance does not exist
        user_approved_scholarships = []

    return render(request, 'approved_application.html', {'approved_scholarships': user_approved_scholarships})

def add_comment(request, scholarship_id):
    scholarship = Scholarships.objects.get(id=scholarship_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            ScholarshipComment.objects.create(user=request.user, scholarship=scholarship, comment=comment)
            return redirect('scholarships')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})

def add_rating(request, scholarship_id):
    scholarship = Scholarships.objects.get(id=scholarship_id)
    if request.method == 'POST':
        form = RatingForm(request.POST, request.FILES)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            ScholarshipRating.objects.create(user=request.user, scholarship=scholarship, rating=rating)
            return redirect('scholarships')
    else:
        form = RatingForm()
    return render(request, 'add_rating.html', {'form': form})

@login_required
def edit_comment(request, comment_id):
    try:
        comment = ScholarshipComment.objects.get(id=comment_id)
        # Check if the user is the owner of the comment
        if comment.user == request.user:
            if request.method == 'POST':
                form = CommentForm(request.POST, instance=comment)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Comment updated successfully.')
                    return redirect('scholarships')
            else:
                form = CommentForm(instance=comment)
            return render(request, 'edit_comment.html', {'form': form})
        else:
            messages.error(request, 'You do not have permission to edit this comment.')
    except ScholarshipComment.DoesNotExist:
        messages.error(request, 'Comment does not exist.')
    
    return redirect('scholarships')

@login_required
def delete_comment(request, comment_id):
    try:
        comment = ScholarshipComment.objects.get(id=comment_id)
        # Check if the user is the owner of the comment
        if comment.user == request.user:
            comment.delete()
            messages.success(request, 'Comment deleted successfully.')
        else:
            messages.error(request, 'You do not have permission to delete this comment.')
    except ScholarshipComment.DoesNotExist:
        messages.error(request, 'Comment does not exist.')
    
    return redirect('scholarships')
@login_required
def edit_rating(request, rating_id):
    rating = get_object_or_404(ScholarshipRating, id=rating_id)
    if rating.user == request.user:
        if request.method == 'POST':
            form = RatingForm(request.POST)
            if form.is_valid():
                rating.rating = form.cleaned_data['rating']
                rating.save()
                messages.success(request, 'Rating updated successfully.')
                return redirect('scholarships')
        else:
            form = RatingForm(initial={'rating': rating.rating})
        return render(request, 'edit_rating.html', {'form': form})
    else:
        messages.error(request, 'You do not have permission to edit this rating.')
        return redirect('scholarships')
    


@login_required
def delete_rating(request, rating_id):
    try:
        rating = ScholarshipRating.objects.get(id=rating_id)
        # Check if the user is the owner of the rating
        if rating.user == request.user:
            rating.delete()
            messages.success(request, 'Rating deleted successfully.')
        else:
            messages.error(request, 'You do not have permission to delete this Rating.')
    except ScholarshipRating.DoesNotExist:
        messages.error(request, 'Rating does not exist.')
    
    return redirect('scholarships')
@login_required
def report_inaccuracy(request, scholarship_id):
    scholarship = Scholarships.objects.get(id=scholarship_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            ReportInaccuracy.objects.create(user=request.user, scholarship=scholarship, description=description)
            messages.success(request, 'Thank you for your report. We will investigate.')
            return redirect('scholarships')
    else:
        form = ReportForm()
    return render(request, 'report_inaccuracy.html', {'form': form})

def view_report(request, scholarship_id):
    scholarship = get_object_or_404(Scholarships, id=scholarship_id)
    reports = ReportInaccuracy.objects.filter(scholarship=scholarship)
    return render(request, 'view_report.html', {'scholarship': scholarship,'reports': reports})