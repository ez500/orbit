from django.urls import path
from .views import MyTeamsView, TeamDetailView, TeamCreateView, join_team, team_dashboard, delete_team_task, delete_team_event, leave_team

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
]
