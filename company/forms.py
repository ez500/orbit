from django import forms

from .models import Company
from .validators import validate_email


class CompanyRegistrationForm(forms.ModelForm):
    name = forms.CharField(
        label='Company Name',
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    description = forms.CharField(label='Description', max_length=200, required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    email = forms.EmailField(
        label='E-mail',
        max_length=254,
        help_text='Must be a valid E-mail address.',
        validators=[validate_email]
    )
    website = forms.URLField(label='Website', required=False)
    phone = forms.CharField(label='Phone #', required=False)
    location = forms.CharField(label='Location', max_length=200, required=False)

    class Meta:
        model = Company
        fields = ['name', 'description', 'profile_picture', 'email', 'website', 'phone', 'location']


class CompanyEditForm(forms.ModelForm):
    name = forms.CharField(
        label='Company Name',
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    description = forms.CharField(label='Description', max_length=200, required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    email = forms.EmailField(
        label='E-mail',
        max_length=254,
        help_text='Must be a valid E-mail address.'
    )
    website = forms.URLField(label='Website', required=False)
    phone = forms.CharField(label='Phone #', required=False)
    location = forms.CharField(label='Location', max_length=200, required=False)

    class Meta:
        model = Company
        fields = ['name', 'description', 'profile_picture', 'email', 'website', 'phone', 'location']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        if Company.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f'{email} is already taken.')
        return email
