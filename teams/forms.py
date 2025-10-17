from django import forms
from .models import Team

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
