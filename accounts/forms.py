from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    last_name = forms.CharField(label='Last Name', max_length=30, required=False)  # noqa E501
    username = forms.CharField(label='Username', max_length=150)
    email = forms.CharField(
        label='E-mail',
        max_length=254,
        help_text='Required. Must be a valid E-mail address.',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class UpdateUserForm(forms.ModelForm):
   first_name = forms.CharField(
        label='First Name',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
   last_name = forms.CharField(label='Last Name', max_length=30, required=False)
   username = forms.CharField(label='Username', max_length=150)
   email = forms.CharField(
        label='E-mail',
        max_length=254,
        help_text='Required. Must be a valid E-mail address.',
    )

   class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class UpdateProfileForm(forms.ModelForm):
    bio = forms.CharField(label='Bio', max_length=127, required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    location = forms.CharField(label='Location', max_length=100, required=False)
    website = forms.URLField(label='Website', required=False)
    visibility = forms.ChoiceField(label='Profile Visibility',
                                   choices=[(tag.name, tag.value) for tag in Profile.Visibility],
                                   initial=Profile.Visibility.PUBLIC.name)

    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'location', 'website', 'visibility']
