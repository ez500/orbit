from django.urls import path

from . import views


app_name = 'dashboard'

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path("tasks/", views.tasks, name='tasks'),
    path("tasks/<int:pk>/view/", views.TaskDetailModalView.as_view(), name='task_detail'),
    path("orbit/", views.orbit_insights, name='orbit_insights'),
    path(
        "orbit/execute/<int:suggestion_id>",
        views.execute_suggestion,
        name='execute_suggestion'
    ),
    path("api/project-team-members/", views.get_project_or_team_members, name='get_team_members'),
    path("api/tasks/", views.TaskCreateAPIView.as_view(), name='create_task'),
    path("api/tasks/<int:task_id>/", views.task_delete, name='task_delete'),
    path("api/orbit-insights", views.OrbitInsightsAPIView.as_view(), name='orbit_insights_api'),
]
