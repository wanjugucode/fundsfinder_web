from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.exceptions import ObjectDoesNotExist
from userprofile.models import UserProfile,LoginHistory
from .forms import *
from .models import Scholarships
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate, gettext
from django.http import Http404
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import ExtractWeek
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver






def is_superuser(user):
    return user.is_authenticated and user.is_superuser

def is_admin(user):
    return user.is_authenticated and user.is_superuser


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

    created_at_threshold = timezone.now() - timedelta(hours=24)
    recently_added_scholarships = Scholarships.objects.filter(created_at__gte=created_at_threshold)

    deadline_threshold = timezone.now() + timedelta(hours=72)
    upcoming_deadlines = Scholarships.objects.filter(application_deadline__lte=deadline_threshold)
    approved_applications = ScholarshipApplication.objects.filter(is_approved=True).distinct()  
    total_notifications = upcoming_deadlines.count() + recently_added_scholarships.count() + approved_applications.count()
  
    try:
        user_profile = request.user.userprofile  # Assuming userprofile is related to the User model
    except ObjectDoesNotExist:
        user_profile = None
    # Retrieve the search query parameters from the request
    search_name = request.GET.get('name')
    search_description = request.GET.get('description')
    search_deadline = request.GET.get('deadline')
    search_country = request.GET.get('country')

    # Filtering scholarships based on search criteria
    if search_name:
        scholarships = scholarships.filter(name__icontains=search_name)
    if search_description:
        scholarships = scholarships.filter(description__icontains=search_description)
    if search_country:
        scholarships = scholarships.filter(country__icontains=search_country)
    if search_deadline:
        try:
            search_deadline = datetime.strptime(search_deadline, '%Y-%m-%d').date()
            scholarships = scholarships.filter(application_deadline=search_deadline)
        except ValueError:
            pass
    
    scholarship_data = []
    for scholarship in scholarships:
        scholarship.has_applied = ScholarshipApplication.objects.filter(scholarship=scholarship, userprofile__user=request.user).exists()
        if user_profile:
            scholarship.has_approved = ApprovedScholarship.objects.filter(original_application__scholarship=scholarship, original_application__userprofile=user_profile).exists()
        else:
            scholarship.has_approved = False
        scholarship.has_expired = scholarship.application_deadline.date() < datetime.now().date()
        # Fetch comments and ratings for each scholarship
        comments = ScholarshipComment.objects.filter(scholarship=scholarship)
        ratings = ScholarshipRating.objects.filter(scholarship=scholarship)

        scholarship_data.append({
            'scholarship': scholarship,
            'comments': comments,
            'ratings': ratings,
           
        })

    context = {
        'scholarship_data': scholarship_data,
        'upcoming_deadlines': upcoming_deadlines,
        'recently_added_scholarships': recently_added_scholarships,
        'approved_applications': approved_applications,
        'total_notifications': total_notifications,


    }
    print(context)
    return render(request, 'scholarship_list.html', context)

def index(request):
    trans = translate(language='fr')
    return render(request, 'home.html', {'trans': trans})

def item(request):
    trans = _('hello')
    return render(request, 'item.html', {'trans': trans})

def translate(language):
    cur_language = get_language()
    try:
        activate(language)
        text = gettext('hello')
    finally:
        activate(cur_language)
    return text

@login_required
@user_passes_test(is_admin)
def admin_scholarships_view(request):
    scholarships = Scholarships.objects.all()
    return render(request, "admin_scholarships_view.html", { "scholarships": scholarships})
def landing_page(request):
    return render(request, "landing_page.html")
def support_page(request):
    return render(request, "support.html")

@user_passes_test(is_admin)
@login_required
def edit_scholarship(request, id):  
    scholarship = Scholarships.objects.get(id=id)
    if request.method == "POST":
        form = ScholarshipAdditionForm(request.POST, request.FILES, instance=scholarship)
        if form.is_valid():
            form.save()
            return redirect('admin_scholarships_view') 
       
    else:
        form = ScholarshipAdditionForm(instance=scholarship)
    return render(request, 'edit_scholarship.html', {"form": form})

@user_passes_test(is_admin)
@login_required
def remove_scholarship(request, id):
    scholarship = Scholarships.objects.get(id=id)
    if request.method == "POST":
        scholarship.delete()
        return redirect('admin_scholarships_view')  
    else:
        return render(request, 'remove_scholarship.html', {'scholarship': scholarship})

@login_required
def apply_scholarship(request, scholarship_id):
    scholarship = get_object_or_404(Scholarships, id=scholarship_id)
    if request.method == 'POST':
        form = ScholarshipApplicationForm(request.POST)
        if form.is_valid():
            user_profile = request.user.userprofile
            application = form.save(commit=False)
            application.userprofile = user_profile
            application.scholarship = scholarship
            application.save()
            return redirect('scholarships')  # Redirect to a success page or another appropriate location
    else:
        form = ScholarshipApplicationForm(initial={'scholarship': scholarship_id})
    # Include the logged-in user's username, email, and user profile in the context
    username = request.user.username
    email = request.user.email
    user_profile = request.user.userprofile
    return render(request, 'apply_scholarship.html', {'form': form, 'scholarship': scholarship, 'username': username, 'email': email, 'user_profile': user_profile})

@user_passes_test(is_admin)
def dashboard(request):
    # Fetch count of admin users
    admin_users_count = User.objects.filter(is_staff=True).count()
    # Fetch count of non-admin users
    non_admin_users_count = User.objects.filter(is_staff=False).count()
    # Total users count
    total_users_count = User.objects.count()
    # Fetch list of users with last login time
    today = datetime.now().date()

    week_ago = today - timedelta(days=7)
    logins_per_week = (
        User.objects
        .filter(last_login__date__gte=week_ago)
        .annotate(week=ExtractWeek('last_login'))
        .values('week')
        .annotate(login_count=Count('id'))
        .order_by('week')
    )
    start_of_month = datetime(today.year, today.month, 1).date()
    logins_per_month = User.objects.filter(last_login__date__gte=start_of_month).values('last_login__month').annotate(login_count=Count('id'))

    start_of_year = datetime(today.year, 1, 1).date()
    logins_per_year = User.objects.filter(last_login__date__gte=start_of_year).values('last_login__year').annotate(login_count=Count('id'))
    users_list = User.objects.all()
    context = {
        'admin_users_count': admin_users_count,
        'non_admin_users_count': non_admin_users_count,
        'total_users_count': total_users_count,
        'users_list': users_list,
        'logins_per_week': logins_per_week,
        'logins_per_month': logins_per_month,
        'logins_per_year': logins_per_year,

    }
    return render(request, 'dashboard.html', context)

@login_required
def users_profile(request):
    # Retrieve the login history for the current user
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')

    return render(request, 'user_history.html', {'login_history': login_history})

@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    LoginHistory.objects.create(user=user)



@user_passes_test(is_superuser)
def add_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        action = request.POST.get('action')
        if action == 'add':
            user.is_staff = True
        elif action == 'revoke':
            user.is_staff = False
        user.save()
        return redirect('users')  # Assuming 'dashboard' is the URL name for the dashboard page
    all_users = User.objects.all()  # Get all users
    return render(request, 'add_admin.html', {'all_users': all_users})


def revoke_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        user.is_staff = False
        user.save()
        return redirect('users')  # Assuming 'users' is the URL name for the users page
    all_users = User.objects.all()  # Get all users
    return render(request, 'add_admin.html', {'all_users': all_users})


@user_passes_test(is_superuser)
def users_list(request):
    users = User.objects.all()
    return render(request, 'users_list.html', {'users': users})

@login_required
def applicants_list(request):
    scholarship_applications = ScholarshipApplication.objects.all()
    return render(request, 'applicants_list.html', {'scholarship_applications': scholarship_applications})

@login_required
def scholarship_application_detail(request, id):
    application = get_object_or_404(ScholarshipApplication, id=id)
    return render(request, 'scholarship_application_detail.html', {'application': application})

@login_required
def approve_scholarship(request, id):
    application = get_object_or_404(ScholarshipApplication, id=id)
    if not application.is_approved:
        application.is_approved = True
        application.save()
        ApprovedScholarship.objects.create(original_application=application)
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
def remove_bookmark(request, scholarship_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        scholarship = Scholarships.objects.get(id=scholarship_id)
        bookmark = Bookmark.objects.filter(userprofile=user_profile, scholarship=scholarship)
        if bookmark.exists():
            bookmark.delete()
        else:
            raise Http404("Bookmark not found")
    except Scholarships.DoesNotExist:
        raise Http404("Scholarship does not exist")
    except UserProfile.DoesNotExist:
        raise Http404("User profile does not exist")
    return redirect('bookmarks')

@login_required
def application_history(request):
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')

    return render(request, 'application_history.html', {'login_history': login_history})


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