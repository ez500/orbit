from django.urls import path

from . import views
from .views import MyTeamsView, TeamDetailView, TeamCreateView, join_team, team_dashboard, delete_team_task, \
    delete_team_event, leave_team, my_teams_api
from .views import remove_member, promote_member, demote_member

app_name = "teams"

urlpatterns = [
    path("", MyTeamsView.as_view(), name="my_teams"),
    path("<int:pk>/", TeamDetailView.as_view(), name="detail"),
    path("create/", TeamCreateView.as_view(), name="create_team"),
    path("join/", join_team, name="join_team"),
    path("<int:pk>/dashboard/", team_dashboard, name="team_dashboard"),
    path("<int:team_pk>/delete_task/<int:task_pk>/", delete_team_task, name="delete_team_task"),
    path("<int:team_pk>/events/<int:event_pk>/delete/", delete_team_event, name="delete_team_event"),
    path("<int:pk>/leave/", leave_team, name="leave_team"),
    path("<int:team_pk>/remove/<int:user_pk>/", remove_member, name="remove_member"),
    path("<int:team_pk>/promote/<int:user_pk>/", promote_member, name="promote_member"),
    path("<int:team_pk>/demote/<int:user_pk>/", demote_member, name="demote_member"),
    path("<int:team_pk>/documents/add/", views.team_add_document, name="team_add_document"),
    path("<int:team_pk>/documents/create/", views.team_create_internal_document, name="team_create_internal_document"),
    path("<int:team_pk>/documents/<int:doc_pk>/", views.team_view_document, name="team_view_document"),
    path("<int:team_pk>/documents/<int:doc_pk>/delete/", views.team_delete_document, name="team_delete_document"),
    path("<int:team_pk>/documents/<int:doc_pk>/edit/", views.team_edit_internal_document, name="team_edit_internal_document"),


    # API endpoints
    path("api/my-teams/", my_teams_api, name="my_teams_api"),
]
