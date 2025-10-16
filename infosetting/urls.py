from django.urls import path
from .views import ProfileView, ProfileEditView

app_name = "infosetting"

urlpatterns = [
    path("me/", ProfileView.as_view(), name="me"),          # View profile
    path("me/edit/", ProfileEditView.as_view(), name="edit")# Edit profile
]
