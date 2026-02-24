from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Employee, Department, Position, LeaveRequest, PerformanceReview, LeaveType

class UserForm(forms.ModelForm):
    """Form for User model fields"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    """Comprehensive form for Employee model"""
    
    # User fields
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'department', 'position', 'hire_date', 
            'employment_type', 'employment_status', 'salary',
            'date_of_birth', 'phone', 'emergency_contact', 
            'emergency_phone', 'address', 'profile_picture'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing employee, populate user fields
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        
        # Make certain fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['hire_date'].required = True
        
        # Add help text
        self.fields['employee_id'].help_text = "Unique identifier for the employee"
        self.fields['salary'].help_text = "Annual salary in USD"
        self.fields['emergency_contact'].help_text = "Name of emergency contact person"
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
        # Check if username exists (excluding current user if editing)
        user_queryset = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            user_queryset = user_queryset.exclude(pk=self.instance.user.pk)
        
        if user_queryset.exists():
            raise forms.ValidationError("Username already exists.")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Check if email exists (excluding current user if editing)
        user_queryset = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            user_queryset = user_queryset.exclude(pk=self.instance.user.pk)
        
        if user_queryset.exists():
            raise forms.ValidationError("Email already exists.")
        
        return email
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        
        # Handle User creation/update
        if employee.pk:  # Editing existing employee
            user = employee.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
        else:  # Creating new employee
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                password='temp123456'  # Temporary password
            )
            employee.user = user
        
        if commit:
            user.save()
            employee.save()
        
        return employee

class LeaveRequestForm(forms.ModelForm):
    """Form for leave requests"""
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

class PerformanceReviewForm(forms.ModelForm):
    """Form for performance reviews"""
    class Meta:
        model = PerformanceReview
        fields = [
            'employee', 'review_period_start', 'review_period_end',
            'overall_rating', 'goals_achievement', 'communication',
            'teamwork', 'technical_skills', 'comments', 'recommendations'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'review_period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'review_period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'overall_rating': forms.Select(attrs={'class': 'form-select'}),
            'goals_achievement': forms.Select(attrs={'class': 'form-select'}),
            'communication': forms.Select(attrs={'class': 'form-select'}),
            'teamwork': forms.Select(attrs={'class': 'form-select'}),
            'technical_skills': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DepartmentForm(forms.ModelForm):
    """Form for creating/editing departments"""
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who are employees as potential managers
        self.fields['manager'].queryset = User.objects.filter(
            employee__employment_status='active'
        )
        self.fields['manager'].required = False

class PositionForm(forms.ModelForm):
    """Form for creating/editing positions"""
    class Meta:
        model = Position
        fields = ['title', 'department', 'description', 'min_salary', 'max_salary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary:
            if min_salary > max_salary:
                raise forms.ValidationError("Maximum salary must be greater than minimum salary.")
        
        return cleaned_data

class EmployeeSearchForm(forms.Form):
    """Form for employee search and filtering"""
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID, or department...'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Employee.EMPLOYMENT_TYPE,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employment_status = forms.ChoiceField(
        choices=[('', 'All Status')] + Employee.EMPLOYMENT_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )