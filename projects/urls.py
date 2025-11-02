from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("create/", views.project_create, name="project_create"),
    path("<int:pk>/add-collaborator/", views.add_collaborator, name="add_collaborator"),
    path("<int:pk>/dashboard/", views.project_dashboard, name="project_dashboard"),
    path("<int:pk>/add-collaborator/", views.add_collaborator, name="add_collaborator"),

]

