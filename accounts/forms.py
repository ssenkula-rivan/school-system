from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Department

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    phone = forms.CharField(max_length=15, required=False)
    class_name = forms.CharField(max_length=100, required=False, help_text='Required for Teachers and Heads of Class (e.g., Grade 1A, Grade 2B)')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Add help text
        self.fields['role'].help_text = 'Select your role in the school'
        self.fields['username'].help_text = 'Your login username (unique)'
        
        # Add JavaScript to show/hide class_name field based on role
        self.fields['role'].widget.attrs['onchange'] = 'toggleClassField()'
        self.fields['class_name'].widget.attrs['id'] = 'id_class_name'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        class_name = cleaned_data.get('class_name')
        
        # Require class_name for teachers and heads of class
        if role in ['teacher', 'head_of_class'] and not class_name:
            self.add_error('class_name', 'Class name is required for Teachers and Heads of Class.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Auto-generate employee ID based on role
            role = self.cleaned_data['role']
            role_prefix = {
                'admin': 'ADM',
                'director': 'DIR',
                'teacher': 'TCH',
                'security': 'SEC',
                'accountant': 'ACC',
                'hr_manager': 'HRM',
                'receptionist': 'REC',
                'librarian': 'LIB',
                'nurse': 'NUR',
                'staff': 'STF',
            }
            
            prefix = role_prefix.get(role, 'EMP')
            
            # Add head_of_class prefix
            if role == 'head_of_class':
                prefix = 'HOC'
            
            # Get the last employee ID with this prefix
            last_profile = UserProfile.objects.filter(
                employee_id__startswith=prefix
            ).order_by('-employee_id').first()
            
            if last_profile:
                try:
                    last_num = int(last_profile.employee_id[3:])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            employee_id = f"{prefix}{new_num:03d}"
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                employee_id=employee_id,
                department=self.cleaned_data.get('department'),
                role=role,
                phone=self.cleaned_data.get('phone', ''),
                class_name=self.cleaned_data.get('class_name', ''),
                is_active_employee=True
            )
        
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['employee_id', 'department', 'role', 'phone', 'address', 
                 'profile_picture', 'hire_date', 'is_active_employee']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['profile_picture', 'hire_date', 'address']:
                field.widget.attrs['class'] = 'form-control'