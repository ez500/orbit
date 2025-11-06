# projects/forms.py
from django import forms
from django.db import models  # for Q() queries
from django.contrib.auth.models import User
from company.models import Company
from .models import Project, Task, Event


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "collaborators", "companies"]

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
                models.Q(owner=user) | models.Q(members=user)
            ).distinct()
        else:
            self.fields["companies"].queryset = Company.objects.none()

        # --- Field Styling ---
        self.fields["name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter project name"
        })

        self.fields["description"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter project description",
            "rows": 3,
        })

        self.fields["collaborators"].widget.attrs.update({
            "class": "form-select",
            "multiple": True,
        })

        self.fields["companies"].widget.attrs.update({
            "class": "form-select",
            "multiple": True,
        })


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
