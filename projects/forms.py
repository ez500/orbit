# projects/forms.py
from django import forms
from django.db import models  # for Q() queries
from django.contrib.auth.models import User
from company.models import Company
from .models import Project, Task, Event, ProjectDocument
from teams.models import Team


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "collaborators", "companies", "team"]  # ✅ added team
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter project name"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter project description",
                "rows": 3
            }),
            "collaborators": forms.SelectMultiple(attrs={
                "class": "form-select"
            }),
            "companies": forms.SelectMultiple(attrs={
                "class": "form-select"
            }),
            "team": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # --- Collaborators field ---
        # Show all users except the current user
        self.fields["collaborators"].queryset = User.objects.exclude(
            id=user.id if user else None
        )

        # --- Companies field ---
        # Only show companies that this user owns or belongs to
        if user:
            self.fields["companies"].queryset = Company.objects.filter(
                models.Q(owner=user) | models.Q(memberships__user=user)
            ).distinct()
        else:
            self.fields["companies"].queryset = Company.objects.none()

        # --- Team field ---
        # Only show teams that the user belongs to or owns
        if user:
            self.fields["team"].queryset = Team.objects.filter(
            memberships__user=user
            ).distinct()
        else:
            self.fields["team"].queryset = Team.objects.none()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "completed"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Task title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_date", "end_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Event name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["name", "file"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document name"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
