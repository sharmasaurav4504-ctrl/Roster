from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, date
import csv, io, json

from .models import UserProfile, Schedule
from .forms import LoginForm, AgentForm, ScheduleForm, CSVUploadForm
from .decorators import wfm_required, supervisor_or_wfm_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('roster')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('roster')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'roster/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def agent_roster_view(request):
    """Public view for agents — no login needed."""
    today = date.today()
    week_start_str = request.GET.get('week_start')
    
    if week_start_str:
        try:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        except ValueError:
            week_start = today - timedelta(days=today.weekday())
    else:
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    
    agents = UserProfile.objects.filter(is_active=True, role='agent').order_by('team', 'full_name')
    schedules = Schedule.objects.filter(date__range=[week_start, week_end]).select_related('agent')
    
    schedule_map = {}
    for s in schedules:
        schedule_map[(s.agent_id, str(s.date))] = s

    return render(request, 'roster/roster.html', {
        'agents': agents,
        'week_dates': week_dates,
        'week_start': week_start,
        'week_end': week_end,
        'schedule_map': schedule_map,
        'prev_week': week_start - timedelta(days=7),
        'next_week': week_start + timedelta(days=7),
        'today': today,
        'user_role': get_role(request.user),
    })


@login_required
def dashboard_view(request):
    try:
        profile = request.user.userprofile
        role = profile.role
    except UserProfile.DoesNotExist:
        role = 'agent'

    if role == 'agent':
        return redirect('roster')

    total_agents = UserProfile.objects.filter(role='agent', is_active=True).count()
    today = date.today()
    today_schedules = Schedule.objects.filter(date=today).count()
    this_week_start = today - timedelta(days=today.weekday())
    week_schedules = Schedule.objects.filter(date__range=[this_week_start, this_week_start + timedelta(days=6)]).count()

    return render(request, 'roster/dashboard.html', {
        'total_agents': total_agents,
        'today_schedules': today_schedules,
        'week_schedules': week_schedules,
        'today': today,
        'user_role': role,
    })


@login_required
@wfm_required
def upload_schedule(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            created, updated, errors = 0, 0, []

            agents_created = 0
            for row_num, row in enumerate(reader, start=2):
                try:
                    emp_id = row.get('employee_id', '').strip()
                    date_str = row.get('date', '').strip()
                    start_str = row.get('shift_start_ist', '').strip()
                    end_str = row.get('shift_end_ist', '').strip()
                    status = row.get('status', 'scheduled').strip() or 'scheduled'
                    break_min = int(row.get('break_duration_minutes', 60) or 60)
                    notes = row.get('notes', '').strip()

                    if not emp_id:
                        errors.append(f"Row {row_num}: Missing employee_id, skipped.")
                        continue

                    # Auto-create agent if not found
                    full_name = row.get('agent_name', '').strip() or row.get('name', '').strip() or emp_id
                    team = row.get('team', '').strip()
                    email = row.get('email', '').strip()

                    agent, agent_created = UserProfile.objects.get_or_create(
                        employee_id=emp_id,
                        defaults={
                            'full_name': full_name,
                            'role': 'agent',
                            'team': team,
                            'email': email,
                            'is_active': True,
                        }
                    )
                    if agent_created:
                        agents_created += 1

                    sched_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    start_time = datetime.strptime(start_str, '%H:%M').time() if start_str else None
                    end_time = datetime.strptime(end_str, '%H:%M').time() if end_str else None

                    obj, c = Schedule.objects.update_or_create(
                        agent=agent, date=sched_date,
                        defaults={
                            'shift_start_ist': start_time,
                            'shift_end_ist': end_time,
                            'status': status,
                            'break_duration_minutes': break_min,
                            'notes': notes,
                            'uploaded_by': request.user,
                            'last_edited_by': request.user,
                        }
                    )
                    if c:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")

            msg = f"Upload complete: {created} schedules created, {updated} updated."
            if agents_created:
                msg += f" {agents_created} new agent(s) auto-created."
            messages.success(request, msg)
            if errors:
                for err in errors[:5]:
                    messages.warning(request, err)
            return redirect('upload_schedule')
    else:
        form = CSVUploadForm()

    return render(request, 'roster/upload_schedule.html', {
        'form': form,
        'user_role': get_role(request.user),
    })


@login_required
@supervisor_or_wfm_required
def edit_schedule(request):
    today = date.today()
    week_start_str = request.GET.get('week_start')
    if week_start_str:
        try:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        except ValueError:
            week_start = today - timedelta(days=today.weekday())
    else:
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    agents = UserProfile.objects.filter(is_active=True, role='agent').order_by('team', 'full_name')
    schedules = Schedule.objects.filter(date__range=[week_start, week_end]).select_related('agent')
    schedule_map = {(s.agent_id, str(s.date)): s for s in schedules}

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            sched = form.save(commit=False)
            sched.last_edited_by = request.user
            # Check for existing
            existing = Schedule.objects.filter(agent=sched.agent, date=sched.date).first()
            if existing:
                for field in ['shift_start_ist', 'shift_end_ist', 'status', 'break_duration_minutes', 'notes']:
                    setattr(existing, field, getattr(sched, field))
                existing.last_edited_by = request.user
                existing.save()
                messages.success(request, 'Schedule updated.')
            else:
                sched.save()
                messages.success(request, 'Schedule created.')
            return redirect(f'/edit-schedule/?week_start={week_start}')
    else:
        form = ScheduleForm()

    return render(request, 'roster/edit_schedule.html', {
        'form': form,
        'agents': agents,
        'week_dates': week_dates,
        'week_start': week_start,
        'schedule_map': schedule_map,
        'prev_week': week_start - timedelta(days=7),
        'next_week': week_start + timedelta(days=7),
        'today': today,
        'user_role': get_role(request.user),
    })


@login_required
@supervisor_or_wfm_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule entry deleted.')
    return redirect('edit_schedule')


@login_required
@wfm_required
def manage_agents(request):
    agents = UserProfile.objects.all().order_by('role', 'full_name')
    return render(request, 'roster/manage_agents.html', {
        'agents': agents,
        'user_role': get_role(request.user),
    })


@login_required
@wfm_required
def add_agent(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agent added successfully.')
            return redirect('manage_agents')
    else:
        form = AgentForm()
    return render(request, 'roster/agent_form.html', {
        'form': form, 'title': 'Add Agent',
        'user_role': get_role(request.user),
    })


@login_required
@wfm_required
def edit_agent(request, agent_id):
    agent = get_object_or_404(UserProfile, id=agent_id)
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agent updated.')
            return redirect('manage_agents')
    else:
        form = AgentForm(instance=agent)
    return render(request, 'roster/agent_form.html', {
        'form': form, 'title': 'Edit Agent',
        'user_role': get_role(request.user),
    })


@login_required
@wfm_required
def download_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="schedule_template.csv"'
    writer = csv.writer(response)
    writer.writerow(['employee_id', 'date', 'shift_start_ist', 'shift_end_ist', 'status', 'break_duration_minutes', 'notes'])
    writer.writerow(['EMP001', '2025-01-20', '09:00', '18:00', 'scheduled', '60', ''])
    writer.writerow(['EMP002', '2025-01-20', '14:00', '23:00', 'scheduled', '60', 'Night shift'])
    writer.writerow(['EMP003', '2025-01-20', '', '', 'off', '0', 'Weekly off'])
    return response


def get_role(user):
    if not user.is_authenticated:
        return 'agent'
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return 'agent'