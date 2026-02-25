#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; from accounts.models import UserProfile; User = get_user_model(); user = User.objects.create_superuser(username='admin', email='cranictech@elincorporatedlimited.com', password='Admin@2024', first_name='System', last_name='Administrator') if not User.objects.filter(username='admin').exists() else None; UserProfile.objects.create(user=User.objects.get(username='admin'), employee_id='ADMIN001', role='admin', is_active_employee=True) if user and not UserProfile.objects.filter(user__username='admin').exists() else None; print('Setup complete!')" | python manage.py shell
