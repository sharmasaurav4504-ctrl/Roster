#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roster_manager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
from django.contrib.auth.models import User
from roster.models import UserProfile

# Create WFM user
wfm = User.objects.create_user(username='wfm_admin', password='wfm@2025', first_name='WFM', last_name='Admin')
UserProfile.objects.create(user=wfm, employee_id='WFM001', full_name='WFM Admin', role='wfm')

# Create Supervisor user
sup = User.objects.create_user(username='supervisor1', password='sup@2025', first_name='Rahul', last_name='Sharma')
UserProfile.objects.create(user=sup, employee_id='SUP001', full_name='Rahul Sharma', role='supervisor', team='Team Alpha')

print("Users created successfully!")
exit()