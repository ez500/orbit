from django.urls import path

from . import views


app_name = 'home'

urlpatterns = [
    path("", views.home, name='home'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("tasks/", views.tasks, name='tasks'),
    path("api/tasks/", views.TaskCreateAPIView.as_view(), name='create-task'),
    path("api/tasks/<int:task_id>/", views.TaskDeleteAPIView.as_view(), name='task-delete'),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
