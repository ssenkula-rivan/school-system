from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views_sysadmin import system_admin_login, system_admin_dashboard
from .views_login import CustomLoginView

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # System Administrator
    path('sysadmin/', system_admin_login, name='sysadmin_login'),
    path('sysadmin/dashboard/', system_admin_dashboard, name='sysadmin_dashboard'),

    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             success_url='/accounts/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('employees/', views.employee_list, name='employee_list'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # User Management
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
]
