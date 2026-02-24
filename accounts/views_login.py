from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.contrib import messages

class CustomLoginView(auth_views.LoginView):
    """Custom login view that checks for system administrator"""
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').lower().strip()
        
        # Check if username is system administrator trigger
        if username in ['system administrator', 'sysadmin', 'system admin']:
            # Redirect to system admin login
            return redirect('accounts:sysadmin_login')
        
        # Otherwise, proceed with normal login
        return super().post(request, *args, **kwargs)
