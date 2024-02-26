from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .models import *
from .forms import  CreateUserForm
from userprofile.models import UserProfile  

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
            return redirect('scholarships')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'login.html')

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    context = {'user_profile': user_profile}
    return render(request, 'profile.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')



        

