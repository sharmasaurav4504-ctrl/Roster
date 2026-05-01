from django.contrib import admin
from .models import UserProfile, Schedule

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employee_id', 'role', 'team', 'is_active']
    list_filter = ['role', 'team', 'is_active']
    search_fields = ['full_name', 'employee_id']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['agent', 'date', 'shift_start_ist', 'shift_end_ist', 'status']
    list_filter = ['status', 'date']
    search_fields = ['agent__full_name', 'agent__employee_id']
