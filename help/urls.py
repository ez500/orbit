from django.urls import path
from . import views

app_name = "help"

urlpatterns = [
    path("accounts/", views.account_help, name="account_help"),
    path("company/", views.company_help, name="company_help"),
    path("task/", views.task_help, name="task_help"),
]