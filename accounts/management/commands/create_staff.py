from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create staff users with different roles'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username')
        parser.add_argument('--password', type=str, required=True, help='Password')
        parser.add_argument('--email', type=str, required=True, help='Email')
        parser.add_argument('--first_name', type=str, required=True, help='First name')
        parser.add_argument('--last_name', type=str, required=True, help='Last name')
        parser.add_argument('--role', type=str, required=True, 
                          choices=['admin', 'director', 'teacher', 'security', 'accountant', 
                                 'hr_manager', 'receptionist', 'librarian', 'nurse', 'staff'],
                          help='User role')
        parser.add_argument('--employee_id', type=str, required=True, help='Employee ID')
        parser.add_argument('--phone', type=str, default='', help='Phone number')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        role = options['role']
        employee_id = options['employee_id']
        phone = options['phone']

        # Check if user exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User {username} already exists'))
            return

        # Check if employee_id exists
        if UserProfile.objects.filter(employee_id=employee_id).exists():
            self.stdout.write(self.style.ERROR(f'Employee ID {employee_id} already exists'))
            return

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Set staff status for certain roles
        if role in ['admin', 'director', 'hr_manager', 'accountant']:
            user.is_staff = True
            user.save()

        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            employee_id=employee_id,
            role=role,
            phone=phone,
            is_active_employee=True
        )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {role} user: {username} (ID: {employee_id})'
        ))
