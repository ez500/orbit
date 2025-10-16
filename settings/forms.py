from django import forms
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "full_name", "bio", "location", "company",
            "website", "avatar", "visibility",
        ]

    def clean_website(self):
        url = self.cleaned_data.get("website", "").strip()
        return url or ""
