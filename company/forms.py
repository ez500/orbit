from django import forms
from .models import Company


class CompanyRegistrationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "email", "phone", "location", "description", "website", "logo"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
