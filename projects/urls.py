from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("create/", views.project_create, name="project_create"),
    path("<int:pk>/add-collaborator/", views.add_collaborator, name="add_collaborator"),
    path("<int:pk>/dashboard/", views.project_dashboard, name="project_dashboard"),
    path("<int:pk>/events-json/", views.project_events_json, name="project_events_json"),
    path("<int:pk>/remove-collaborator/<int:user_id>/", views.remove_collaborator, name="remove_collaborator"),
    path("<int:pk>/remove-task/<int:task_id>/", views.remove_task, name="remove_task"),
    path("<int:pk>/remove-event/<int:event_id>/", views.remove_event, name="remove_event"),
    path("<int:pk>/delete/", views.delete_project, name="delete_project"),
]

