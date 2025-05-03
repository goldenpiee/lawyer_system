import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawyer_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpass')
full_name = os.environ.get('DJANGO_SUPERUSER_FULLNAME', 'Admin User')
phone = os.environ.get('DJANGO_SUPERUSER_PHONE', '+79990000000')

if not User.objects.filter(email=email).exists():
    print(f"Создаю суперпользователя {email}")
    User.objects.create_superuser(
        email=email,
        password=password,
        full_name=full_name,
        phone=phone
    )
else:
    print(f"Суперпользователь {email} уже существует")
