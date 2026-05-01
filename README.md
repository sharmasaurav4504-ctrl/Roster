# Roster Manager

A workforce management system built with Django.

## Default Login Credentials

| Role       | Username    | Password  |
|------------|-------------|-----------|
| WFM        | wfm_admin   | wfm@2025  |
| Supervisor | supervisor1 | sup@2025  |
| Agent      | (no login)  | (no login)|

## Local Development

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://localhost:8000
