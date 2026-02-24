from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Department, Position, Employee, LeaveType, LeaveRequest, 
    PerformanceReview, Attendance, WorkSubmission
)

# Inline to integrate Employee model into the User admin page
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee Information'
    fk_name = 'user'
    fields = (
        'employee_id', 'department', 'position', 'hire_date',
        'employment_type', 'employment_status', 'salary',
        ('date_of_birth', 'profile_picture'),
        'phone', 'address', ('emergency_contact', 'emergency_phone')
    )
    readonly_fields = ('employee_id',)

# Re-register User to use the custom admin configuration
class CustomUserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'get_department', 'get_position',
        'get_employment_status'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups',
        'employee__department', 'employee__position', 'employee__employment_status'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def get_department(self, obj):
        return obj.employee.department.name if hasattr(obj, 'employee') and obj.employee.department else '-'
    get_department.short_description = 'Department'

    def get_position(self, obj):
        return obj.employee.position.title if hasattr(obj, 'employee') and obj.employee.position else '-'
    get_position.short_description = 'Position'

    def get_employment_status(self, obj):
        return obj.employee.get_employment_status_display() if hasattr(obj, 'employee') else '-'
    get_employment_status.short_description = 'Employment Status'

# Unregister the default User model
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register the new CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'employee_count', 'budget', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    def employee_count(self, obj):
        return obj.employee_set.count()
    employee_count.short_description = 'Employees'

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'min_salary', 'max_salary')
    list_filter = ('department',)
    search_fields = ('title', 'description')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id', 'get_full_name', 'department', 'position', 
        'employment_type', 'employment_status', 'hire_date', 'years_of_service'
    )
    list_filter = (
        'employment_status', 'employment_type', 'department', 
        'hire_date', 'created_at'
    )
    search_fields = (
        'employee_id', 'user__first_name', 'user__last_name', 
        'user__username', 'user__email'
    )
    readonly_fields = ('created_at', 'updated_at', 'years_of_service', 'age')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Employment Details', {
            'fields': (
                'department', 'position', 'hire_date', 'employment_type', 
                'employment_status', 'salary'
            )
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'phone', 'address', 'profile_picture'
            ),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'years_of_service', 'age'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
    
    def years_of_service(self, obj):
        return f"{obj.years_of_service} years"
    years_of_service.short_description = 'Service Years'

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'days_allowed', 'description')
    search_fields = ('name',)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'leave_type', 'start_date', 'end_date', 
        'duration', 'status', 'applied_on'
    )
    list_filter = ('status', 'leave_type', 'start_date', 'applied_on')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'reason')
    readonly_fields = ('applied_on', 'approved_on', 'duration')
    
    fieldsets = (
        ('Leave Information', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approved_on')
        }),
        ('System Information', {
            'fields': ('applied_on', 'duration'),
            'classes': ('collapse',)
        }),
    )
    
    def duration(self, obj):
        return f"{obj.duration} days"
    duration.short_description = 'Duration'

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'reviewer', 'review_period_end', 'overall_rating', 
        'average_rating', 'created_at'
    )
    list_filter = ('overall_rating', 'review_period_end', 'created_at')
    search_fields = (
        'employee__user__first_name', 'employee__user__last_name',
        'reviewer__first_name', 'reviewer__last_name'
    )
    readonly_fields = ('created_at', 'average_rating')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('employee', 'reviewer', 'review_period_start', 'review_period_end')
        }),
        ('Ratings', {
            'fields': (
                'overall_rating', 'goals_achievement', 'communication', 
                'teamwork', 'technical_skills'
            )
        }),
        ('Comments', {
            'fields': ('comments', 'recommendations')
        }),
        ('System Information', {
            'fields': ('created_at', 'average_rating'),
            'classes': ('collapse',)
        }),
    )
    
    def average_rating(self, obj):
        return f"{obj.average_rating:.1f}/5"
    average_rating.short_description = 'Average Rating'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 'date', 'check_in', 'check_out', 'hours_worked', 
        'is_present', 'is_late'
    )
    list_filter = ('is_present', 'is_late', 'date')
    search_fields = ('employee__user__first_name', 'employee__user__last_name')
    readonly_fields = ('hours_worked',)
    date_hierarchy = 'date'
    
    def hours_worked(self, obj):
        hours = obj.hours_worked
        if hours:
            return f"{hours:.2f} hours"
        return "0 hours"
    hours_worked.short_description = 'Hours Worked'

# Customize admin site
admin.site.site_header = "Workplace Management System"
admin.site.site_title = "WMS Admin"
admin.site.index_title = "Welcome to Workplace Management System Administration"

@admin.register(WorkSubmission)
class WorkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'work_type', 'subject', 'status', 'submitted_at')
    list_filter = ('status', 'work_type', 'submitted_at')
    search_fields = ('title', 'teacher__first_name', 'teacher__last_name', 'subject')
    readonly_fields = ('submitted_at', 'reviewed_at')
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Submission Information', {
            'fields': ('teacher', 'title', 'work_type', 'subject', 'grade_level', 'description', 'document')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'feedback')
        }),
        ('System Information', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )