from home.models import Company, Project
from teams.models import Team
from django import forms
from django.contrib.auth.models import User


FILTER_CHOICES = [
      ('user', 'Users'),
      ('company', 'Companies'),
      ('team', 'Teams'),
      ('project', 'Projects'),
]


class SearchForm(forms.Form):
	q = forms.CharField(
	label="Search",
	required=False,
	widget=forms.TextInput(attrs={
	"placeholder": "Search users, teams, companies, projects…",
	"class": "form-control",
	}),
	)

 	filter_by = forms.MultipleChoiceField(
        choices=FILTER_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
   	)

	team = forms.ModelChoiceField(
	label="Team",
	required=False,
	queryset=Team.objects.order_by("name"),
	widget=forms.Select(attrs={"class": "form-select"}),
	)


	company = forms.ModelChoiceField(
	label="Company",
	required=False,
	queryset=Company.objects.order_by("name"),
	widget=forms.Select(attrs={"class": "form-select"}),
	)


	project = forms.ModelChoiceField(
	label="Project",
	required=False,
	queryset=Project.objects.order_by("name"),
	widget=forms.Select(attrs={"class": "form-select"}),
	)
