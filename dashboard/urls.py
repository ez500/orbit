from django.urls import path

from . import views


app_name = 'dashboard'

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path("tasks/", views.tasks, name='tasks'),
    path("api/project-team-members/", views.get_project_or_team_members, name='get_team_members'),
    path("api/tasks/", views.TaskCreateAPIView.as_view(), name='create_task'),
    path("api/tasks/<int:task_id>/", views.TaskDeleteAPIView.as_view(), name='task_delete'),
]
