from django.shortcuts import redirect
from django.contrib import messages

def custom_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Login required.")
            return redirect("userauths:login")

        # Use Django's staff flag for admin access. This will allow
        # any user with `is_staff=True` (or superusers) to access
        # the admin panel. Previously this checked a custom flag.
        if not getattr(request.user, "is_staff", False):
            messages.error(request, "You do not have permission to access this panel.")
            return redirect("core:home")

        return view_func(request, *args, **kwargs)
    return wrapper