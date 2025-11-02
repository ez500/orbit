from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name", "description", "collaborators",
            "clients", "related_projects", "due_date"
        ]
