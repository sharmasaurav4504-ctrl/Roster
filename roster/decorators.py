from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


def get_user_role(user):
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return 'agent'


def wfm_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if get_user_role(request.user) != 'wfm':
            messages.error(request, 'Access denied. WFM role required.')
            return redirect('roster')
        return view_func(request, *args, **kwargs)
    return wrapper


def supervisor_or_wfm_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        role = get_user_role(request.user)
        if role not in ('wfm', 'supervisor'):
            messages.error(request, 'Access denied. Supervisor or WFM role required.')
            return redirect('roster')
        return view_func(request, *args, **kwargs)
    return wrapper
