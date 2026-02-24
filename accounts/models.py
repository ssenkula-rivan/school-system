from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('director', 'Director'),
        ('head_of_class', 'Head of Class'),
        ('teacher', 'Teacher'),
        ('security', 'Security'),
        ('bursar', 'Bursar'),
        ('accountant', 'Accountant'),
        ('hr_manager', 'HR Manager'),
        ('receptionist', 'Receptionist'),
        ('librarian', 'Librarian'),
        ('nurse', 'Nurse'),
        ('parent', 'Parent'),
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active_employee = models.BooleanField(default=True)
    
    # For Head of Class and Teachers
    class_name = models.CharField(max_length=100, blank=True, help_text='Class assigned to Head of Class or Teacher (e.g., Grade 1A, Grade 2B)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active_employee']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})
    
    @property
    def is_director(self):
        return self.role == 'director'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_head_of_class(self):
        return self.role == 'head_of_class'
    
    @property
    def is_security(self):
        return self.role == 'security'
    
    @property
    def is_accountant(self):
        return self.role == 'accountant'
    
    @property
    def is_bursar(self):
        return self.role == 'bursar'
    
    @property
    def can_manage_fees(self):
        return self.role in ['admin', 'director', 'bursar', 'accountant']
    
    @property
    def can_manage_employees(self):
        return self.role in ['admin', 'director', 'hr_manager']
    
    @property
    def can_view_reports(self):
        return self.role in ['admin', 'director', 'accountant', 'hr_manager']



# Import audit models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditLog(models.Model):
    """Track all important system actions"""
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment', 'Payment Recorded'),
        ('view', 'Viewed'),
        ('export', 'Exported'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


class LoginLog(models.Model):
    """Track login attempts"""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_logs')
    username_attempted = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.username_attempted} - {self.status} - {self.timestamp}"
