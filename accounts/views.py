from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *
from .forms import  CreateUserForm

# function to register new users
def registerPage(request):
	if request.user.is_authenticated:
		return redirect('login')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)
				return redirect('login')
		context = {'form':form}
		return render(request, 'register.html', context)

# function to login after registration 
def loginPage(request):
	if request.user.is_authenticated:
		return redirect('login')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				# once logged in you are redirected to scholarship page
				return redirect('scholarships')
			else:
				messages.info(request, 'Username OR password is incorrect')
		context = {}
		return render(request, 'login.html', context)
	
	# function to logout the user
def logoutUser(request):
    if request.method == 'POST':
        return redirect('login')



        

