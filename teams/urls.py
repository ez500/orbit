from django.urls import path
from .views import MyTeamsView, TeamDetailView

app_name = "teams"

urlpatterns = [
    path("my/", MyTeamsView.as_view(), name="my_teams"),
    path("<int:pk>/", TeamDetailView.as_view(), name="detail"),
]
