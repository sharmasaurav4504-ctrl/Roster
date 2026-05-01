from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('wfm', 'WFM'),
        ('supervisor', 'Supervisor'),
        ('agent', 'Agent'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    employee_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    team = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id}) - {self.role}"

    class Meta:
        ordering = ['full_name']


class Schedule(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('off', 'Day Off'),
        ('wfh', 'Work From Home'),
        ('leave', 'On Leave'),
        ('training', 'Training'),
    ]

    agent = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    shift_start_ist = models.TimeField(null=True, blank=True)
    shift_end_ist = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    break_duration_minutes = models.IntegerField(default=60)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_schedules')
    last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['agent', 'date']
        ordering = ['date', 'shift_start_ist']

    def __str__(self):
        return f"{self.agent.full_name} - {self.date} - {self.status}"
