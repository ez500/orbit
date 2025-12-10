from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("create/", views.project_create, name="project_create"),
    path("<int:pk>/delete/", views.delete_project, name="delete_project"),


    # ROLE MANAGEMENT
    path("<int:pk>/add-manager/", views.add_manager, name="add_manager"),
    path("<int:pk>/add-member/", views.add_member, name="add_member"),
    path("<int:pk>/promote/<int:user_id>/", views.promote_member, name="promote_member"),
    path("<int:pk>/demote/<int:user_id>/", views.demote_manager, name="demote_manager"),
    path("<int:pk>/remove/<int:user_id>/", views.remove_user, name="remove_user"),

    # Dashboard and documents (unchanged)
    path("<int:pk>/dashboard/", views.project_dashboard, name="project_dashboard"),
    path("<int:pk>/events-json/", views.project_events_json, name="project_events_json"),

    path("<int:pk>/documents/add/", views.add_document, name="add_document"),
    path("<int:pk>/documents/create/", views.create_internal_document, name="create_internal_document"),
    path("documents/<int:doc_id>/edit/", views.edit_internal_document, name="edit_internal_document"),
    path("documents/<int:doc_id>/view/", views.view_internal_document, name="view_internal_document"),
    path("<int:pk>/documents/<int:doc_id>/", views.view_document, name="view_document"),

    # Delete task
    path("<int:project_pk>/tasks/<int:task_pk>/delete/",
       views.delete_project_task,
       name="delete_project_task"),

    # Delete event
    path("<int:project_pk>/events/<int:event_pk>/delete/",
        views.delete_project_event,
        name="delete_project_event"),
]
