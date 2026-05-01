#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py migrate

# Create superuser safely
python manage.py shell << END
from django.contrib.auth.models import User

username = "wfm_admin"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
    print("Superuser created")
else:
    print("Superuser already exists")
END