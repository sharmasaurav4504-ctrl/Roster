from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_roster_view, name='roster'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload-schedule/', views.upload_schedule, name='upload_schedule'),
    path('edit-schedule/', views.edit_schedule, name='edit_schedule'),
    path('delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('manage-agents/', views.manage_agents, name='manage_agents'),
    path('add-agent/', views.add_agent, name='add_agent'),
    path('edit-agent/<int:agent_id>/', views.edit_agent, name='edit_agent'),
    path('download-template/', views.download_template, name='download_template'),
]
