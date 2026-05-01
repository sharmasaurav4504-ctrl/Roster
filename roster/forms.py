from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, Schedule
import csv, io


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Employee ID', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class AgentForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['employee_id', 'full_name', 'team', 'email', 'role', 'is_active']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'team': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class ScheduleForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Schedule
        fields = ['agent', 'date', 'shift_start_ist', 'shift_end_ist', 'status', 'break_duration_minutes', 'notes']
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'shift_start_ist': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'shift_end_ist': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'break_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agent'].queryset = UserProfile.objects.filter(is_active=True, role='agent')


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload Schedule CSV',
        widget=forms.FileInput(attrs={'accept': '.csv', 'class': 'form-control'})
    )

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.endswith('.csv'):
            raise forms.ValidationError('Please upload a valid CSV file.')
        return f
