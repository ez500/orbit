# projects/forms.py
from django import forms
from django.contrib.auth.models import User
from django.db import models

from company.models import Company
from .models import Project
from .models import ProjectDocument
from teams.models import Team


class ProjectForm(forms.ModelForm):
    """
    Main project form. Adds optional role assignment fields:
    - managers
    - members

    lead (request.user) is handled automatically inside views.
    collaborators remain under-the-hood compatibility only.
    """

    managers = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"})
    )

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"})
    )

    auto_add_team_members = forms.BooleanField(
        required=False,
        label="Automatically add all team members as project collaborators",
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "team",
            "companies",
            "managers",   # NEW
            "members",    # NEW
            "auto_add_team_members",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Project name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "companies": forms.SelectMultiple(attrs={"class": "form-select"}),
            "team": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Filter managers/members to users except current lead
        if user:
            self.fields["managers"].queryset = User.objects.exclude(id=user.id)
            self.fields["members"].queryset = User.objects.exclude(id=user.id)

        # Only show companies belonging to the acting user
        if user:
            self.fields["companies"].queryset = Company.objects.filter(
                models.Q(owner=user) | models.Q(memberships__user=user)
            ).distinct()

        # Team queryset = teams the acting user belongs to
        if user:
            self.fields["team"].queryset = Team.objects.filter(memberships__user=user).distinct()

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["name", "file"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document name"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class InternalDocumentForm(forms.ModelForm):
    """
    Used for creating/editing internal CRM documents written in the editor.
    Stores HTML content in ProjectDocument.content.
    """
    class Meta:
        model = ProjectDocument
        fields = ["name", "content"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document title"}),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 20,
                "placeholder": "Write your document here..."
            }),
        }

class AddManagerForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
        label="Select User to Promote to Manager"
    )


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
        label="Select User to Add as Member"
    )
