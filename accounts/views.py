from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .models import *
from .forms import  CreateUserForm

# function to register new users
def register_page(request):
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

def login_page(request):
    if request.user.is_authenticated:
        return redirect('scholarships')  # Redirect logged-in users to scholarships page

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.groups.filter(name='Admin').exists():
                return redirect('admin_scholarships_view')  # Redirect users in admin group to admin scholarship view
            else:
                return redirect('scholarships')  # Redirect users not in admin group to scholarship list
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'login.html')
	
	# function to logout the user
def logout_user(request):
    logout(request)
    # Redirect to a page after logout
    return redirect('login') 



        

