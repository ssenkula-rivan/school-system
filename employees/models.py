from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def employee_count(self):
        return self.employees.count()

class Position(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"

class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ]
    
    EMPLOYMENT_TYPE = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Employment Details
    hire_date = models.DateField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE, default='full_time')
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='active')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    # System fields
    profile_picture = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['department', 'employment_status']),
            models.Index(fields=['hire_date']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def get_absolute_url(self):
        return reverse('employees:detail', kwargs={'pk': self.pk})
    
    @property
    def age(self):
        if self.date_of_birth:
            return date.today().year - self.date_of_birth.year
        return None
    
    @property
    def years_of_service(self):
        return (date.today() - self.hire_date).days // 365

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    days_allowed = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    applied_on = models.DateTimeField(auto_now_add=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['-applied_on']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def duration(self):
        return (self.end_date - self.start_date).days + 1

class PerformanceReview(models.Model):
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_reviews')
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    goals_achievement = models.IntegerField(choices=RATING_CHOICES)
    communication = models.IntegerField(choices=RATING_CHOICES)
    teamwork = models.IntegerField(choices=RATING_CHOICES)
    technical_skills = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField()
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', '-created_at']),
            models.Index(fields=['-review_period_end']),
            models.Index(fields=['overall_rating']),
        ]
    
    def __str__(self):
        return f"{self.employee} - Review {self.review_period_end.year}"
    
    @property
    def average_rating(self):
        return (self.overall_rating + self.goals_achievement + self.communication + 
                self.teamwork + self.technical_skills) / 5

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    is_present = models.BooleanField(default=True)
    is_late = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', '-date']),
            models.Index(fields=['date']),
            models.Index(fields=['is_present']),
            models.Index(fields=['is_late']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.date}"
    
    @property
    def hours_worked(self):
        if self.check_in and self.check_out:
            from datetime import datetime, timedelta
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            
            # Calculate break time
            break_duration = timedelta(0)
            if self.break_start and self.break_end:
                break_start_dt = datetime.combine(self.date, self.break_start)
                break_end_dt = datetime.combine(self.date, self.break_end)
                break_duration = break_end_dt - break_start_dt
            
            total_time = check_out_dt - check_in_dt - break_duration
            return total_time.total_seconds() / 3600  # Convert to hours
        return 0

class WorkSubmission(models.Model):
    """Teacher work submissions to Director of Studies"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision', 'Needs Revision'),
    ]
    
    WORK_TYPE_CHOICES = [
        ('lesson_plan', 'Lesson Plan'),
        ('assignment', 'Assignment'),
        ('exam', 'Exam/Test'),
        ('report', 'Report'),
        ('curriculum', 'Curriculum Document'),
        ('other', 'Other'),
    ]
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_submissions')
    submitted_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_submissions', help_text='Head of Class or Director who receives this submission')
    
    title = models.CharField(max_length=200)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES)
    description = models.TextField()
    document = models.FileField(upload_to='teacher_submissions/', blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['submitted_to', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['-submitted_at']),
            models.Index(fields=['work_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.teacher.get_full_name()}"
