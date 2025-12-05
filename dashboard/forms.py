from django import forms

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
        team = kwargs.pop("team", None)
        super().__init__(*args, **kwargs)
        if team is not None:
            self.fields["team"].queryset = Team.objects.filter(id=team.id)
            self.fields["team"].initial = team.pk
            self.fields["team"].disabled = True
            self.fields["project"].queryset = Project.objects.none()
            self.fields["project"].disabled = True


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
        team = kwargs.pop("team", None)
        super().__init__(*args, **kwargs)
        if team is not None:
            self.fields["team"].queryset = Team.objects.filter(id=team.id)
            self.fields["team"].initial = team.pk
            self.fields["team"].disabled = True
            self.fields["project"].queryset = Project.objects.none()
            self.fields["project"].disabled = True
