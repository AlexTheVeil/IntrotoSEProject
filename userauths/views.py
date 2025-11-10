from urllib import request
from django.shortcuts import render, redirect
from userauths.forms import UserLoginForm, UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()
# Create your views here.


def Register_View(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}!")
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1']
                                    )
            login(request, new_user)
            return redirect("core:home")
    else:
        form = UserRegisterForm()
        print("User registration failed")
   
    context = {
        "form": form
    }
    return render(request, 'userauths/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Already Logged In.")
        return redirect("core:home")
    
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("core:home")
            else:
                messages.warning(request, "Invalid email or password.")
                return redirect("userauths:login")
    else:
        form = UserLoginForm()
    
    return render(request, 'userauths/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("userauths:login")