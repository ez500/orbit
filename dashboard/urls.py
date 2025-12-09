from django.urls import path

from . import views


app_name = 'dashboard'

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path("tasks/", views.tasks, name='tasks'),
    path("tasks/<int:pk>/view/", views.TaskDetailModalView.as_view(), name='task_detail'),
    path("api/project-team-members/", views.get_project_or_team_members, name='get_team_members'),
    path("api/tasks/", views.TaskCreateAPIView.as_view(), name='create_task'),
    path("api/tasks/<int:task_id>/update/", views.TaskUpdateAPIView.as_view(), name='update_task'),
    path("api/tasks/<int:task_id>/", views.task_delete, name='task_delete'),
    path("api/widgets/", views.get_dashboard_widgets, name='dashboard_widgets'),
    path("api/widget-data/<str:widget_type>/", views.get_widget_data, name='widget_data'),
]
