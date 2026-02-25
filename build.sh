#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell << EOF
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='cranictech@elincorporatedlimited.com',
        password='Admin@2024',
        first_name='System',
        last_name='Administrator'
    )
    UserProfile.objects.create(
        user=user,
        employee_id='ADMIN001',
        role='admin',
        is_active_employee=True
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists')
EOF
