from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

SYSTEM_ADMIN_PASSWORD = "Cranictech"
SYSTEM_ADMIN_TRIGGER = "system administrator"  # Username to trigger sysadmin login

@never_cache
def system_admin_login(request):
    """System Administrator login - password only"""
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if password == SYSTEM_ADMIN_PASSWORD:
            # Get or create system admin user
            sysadmin, created = User.objects.get_or_create(
                username='sysadmin',
                defaults={
                    'is_staff': True,
                    'is_superuser': True,
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'email': 'sysadmin@cranictech.com'
                }
            )
            
            if created:
                sysadmin.set_password(SYSTEM_ADMIN_PASSWORD)
                sysadmin.save()
            
            # Login the system admin
            login(request, sysadmin, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'System Administrator access granted!')
            return redirect('/admin/')
        else:
            messages.error(request, 'Invalid password. Access denied.')
    
    return render(request, 'accounts/sysadmin_login.html')

def check_sysadmin_login(request):
    """Check if username is system administrator trigger"""
    if request.method == 'POST':
        username = request.POST.get('username', '').lower().strip()
        
        # Check if username matches system administrator trigger
        if username == SYSTEM_ADMIN_TRIGGER or username == 'sysadmin' or username == 'system admin':
            # Redirect to system admin login
            return redirect('accounts:sysadmin_login')
    
    return None

@login_required
def system_admin_dashboard(request):
    """System Administrator dashboard with full control"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. System Administrator only.')
        return redirect('accounts:login')
    
    from django.contrib.auth.models import User
    from accounts.models import UserProfile
    from fees.models import Student, FeePayment
    from employees.models import Employee
    
    context = {
        'total_users': User.objects.count(),
        'total_profiles': UserProfile.objects.count(),
        'total_students': Student.objects.count(),
        'total_employees': Employee.objects.count(),
        'total_payments': FeePayment.objects.count(),
    }
    
    return render(request, 'accounts/sysadmin_dashboard.html', context)
