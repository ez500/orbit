from django import forms
from django.contrib.auth.models import User

from dashboard.models import Task, Event
from projects.models import Project
from teams.models import Team


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "content", "status", "deadline", "team", "project", "users"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Task title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "users": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        team = kwargs.pop("team", None)
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["users"].queryset = User.objects.filter(id=user.id)
        else:
            self.fields["users"].queryset = User.objects.none()
        if team is not None:
            self.fields["team"].queryset = Team.objects.filter(id=team.id)
            self.fields["team"].initial = team.pk
            self.fields["team"].disabled = True
            self.fields["users"].queryset = User.objects.filter(teams=team)
            self.fields["project"].queryset = Project.objects.none()
            self.fields["project"].disabled = True
        elif project is not None:
            self.fields["project"].queryset = Project.objects.filter(id=project.id)
            self.fields["project"].initial = project.pk
            self.fields["project"].disabled = True
            self.fields["users"].queryset = (User.objects.filter(led_projects=project)
                                             | User.objects.filter(collaborative_projects=project))
            self.fields["team"].queryset = Team.objects.none()
            self.fields["team"].disabled = True


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "content", "start_datetime", "end_datetime", "team", "project", "users"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Event name"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "start_datetime": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "users": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        team = kwargs.pop("team", None)
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["users"].queryset = User.objects.filter(id=user.id)
        else:
            self.fields["users"].queryset = User.objects.none()
        if team is not None:
            self.fields["team"].queryset = Team.objects.filter(id=team.id)
            self.fields["team"].initial = team.pk
            self.fields["team"].disabled = True
            self.fields["users"].queryset = User.objects.filter(teams=team)
            self.fields["project"].queryset = Project.objects.none()
            self.fields["project"].disabled = True
        elif project is not None:
            self.fields["project"].queryset = Project.objects.filter(id=project.id)
            self.fields["project"].initial = project.pk
            self.fields["project"].disabled = True
            self.fields["users"].queryset = (User.objects.filter(led_projects=project)
                                             | User.objects.filter(collaborative_projects=project))
            self.fields["team"].queryset = Team.objects.none()
            self.fields["team"].disabled = True
