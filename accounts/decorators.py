from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(*roles):
    """
    Decorator to check if user has required role
    Usage: @role_required('admin', 'director')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            try:
                user_profile = request.user.userprofile
                if user_profile.role in roles or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('accounts:dashboard')
            except:
                messages.error(request, 'Profile not found. Please contact administrator.')
                return redirect('accounts:dashboard')
        
        return wrapper
    return decorator

def director_required(view_func):
    """Decorator for director-only views"""
    return role_required('admin', 'director')(view_func)

def teacher_required(view_func):
    """Decorator for teacher views"""
    return role_required('admin', 'director', 'teacher')(view_func)

def security_required(view_func):
    """Decorator for security views"""
    return role_required('admin', 'director', 'security')(view_func)

def accountant_required(view_func):
    """Decorator for accountant views"""
    return role_required('admin', 'director', 'accountant')(view_func)

def can_manage_fees(view_func):
    """Decorator for fee management views"""
    return role_required('admin', 'director', 'accountant')(view_func)

def can_manage_employees(view_func):
    """Decorator for employee management views"""
    return role_required('admin', 'director', 'hr_manager')(view_func)
