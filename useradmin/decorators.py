from django.shortcuts import redirect
from django.contrib import messages

def custom_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Login required.")
            return redirect("userauths:login")

        if not getattr(request.user, "is_custom_admin", False):
            messages.error(request, "You do not have permission to access this panel.")
            return redirect("core:home")

        return view_func(request, *args, **kwargs)
    return wrapper