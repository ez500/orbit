from django import forms

from .models import Team,TeamDocument


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

class TeamDocumentForm(forms.ModelForm):
    class Meta:
        model = TeamDocument
        fields = ["name", "doc_type", "file", "content", "external_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "doc_type": forms.Select(attrs={"class": "form-select"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": "8"}),
            "external_url": forms.URLInput(attrs={"class": "form-control"}),
        }
