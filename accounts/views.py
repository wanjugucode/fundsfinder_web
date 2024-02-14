from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .models import *
from .forms import  CreateUserForm
from userprofile.models import UserProfile  # Import your UserProfile model

def register_page(request):
    if request.user.is_authenticated:
        return redirect('login')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                UserProfile.objects.create(user=user)
                messages.success(request, 'Account was created successfully.')
                return redirect('login')
        context = {'form': form}
        return render(request, 'register.html', context)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('scholarships')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            create_user_profile(user)  # Ensure UserProfile instance exists
            return redirect('scholarships')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'login.html')

def create_user_profile(user):
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)
	
	# function to logout the user
def logout_user(request):
    logout(request)
    # Redirect to a page after logout
    return redirect('login') 



        

