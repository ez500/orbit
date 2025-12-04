from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="files"),
    path("handle/", views.HandleFileUpload.as_view()),
    path("download/<uid>/", views.download, name="download"),
    path("pdf_list/", views.list, name="pdf_list"),
]
