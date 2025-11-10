from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from accounts.models import Account

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created! You can log in now.")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            temp = Account.objects.get(user_ID=1)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "invalid username or password. ")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('login')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('login')
