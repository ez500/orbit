from django import forms
from .models import Team, TeamTask, TeamEvent

class JoinTeamForm(forms.Form):
    team_name = forms.CharField(
        label="Team Name",
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Enter team name"})
    )

    def clean_team_name(self):
        name = self.cleaned_data["team_name"].strip()
        try:
            team = Team.objects.get(name__iexact=name)
        except Team.DoesNotExist:
            raise forms.ValidationError("No team found with that name.")
        return team

class TeamTaskForm(forms.ModelForm):
    class Meta:
        model = TeamTask
        fields = ["title", "description", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Task title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Task details..."}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

class TeamEventForm(forms.ModelForm):
    class Meta:
        model = TeamEvent
        fields = ["title", "description", "start_date", "end_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
