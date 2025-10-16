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
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        )

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
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )

class UpdateProfileForm(forms.ModelForm):
    bio = forms.CharField(label='Bio', max_length=127, required=False)
    profile_picture = forms.ImageField()
    is_visible = forms.BooleanField(label='Profile visible to others')
    is_private = forms.BooleanField(label='Personal info shown in profile')

    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'is_visible', 'is_private')

