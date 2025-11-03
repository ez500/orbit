from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm as DefaultChangePasswordForm

from .models import Profile
from .validators import validate_email


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    last_name = forms.CharField(label='Last Name', max_length=30, required=False)
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(
        label='E-mail',
        max_length=254,
        help_text='Must be a valid E-mail address.',
        validators=[validate_email]
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
        help_text='Must be a valid E-mail address.',
        validators=[validate_email]
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class UpdateProfileForm(forms.ModelForm):
    bio = forms.CharField(label='Bio', max_length=127, required=False)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    location = forms.CharField(label='Location', max_length=100, required=False)
    website = forms.URLField(label='Website', required=False)
    theme_color = forms.ChoiceField(
        label='Theme Color',
        choices=Profile.THEME_CHOICES,
        initial='dark',
        required=False
    )
    accent_color = forms.ChoiceField(
        label='Accent Color',
        choices=Profile.ACCENT_CHOICES,
        initial='#1E90FF',
        required=False
    )
    visibility = forms.ChoiceField(
        label='Profile Visibility',
        choices=[(tag.name, tag.value) for tag in Profile.Visibility],
        initial=Profile.Visibility.PUBLIC.name
    )
    # Accessibility / appearance preferences
    high_contrast = forms.BooleanField(label='High Contrast', required=False)
    font_size = forms.ChoiceField(
        label='Font size',
        choices=Profile.FONT_SIZE_CHOICES,
        initial='medium',
        required=False
    )
    spacing = forms.ChoiceField(
        label='Spacing',
        choices=Profile.SPACING_CHOICES,
        initial='normal',
        required=False
    )
    notification_email = forms.BooleanField(label='Email Notifications', required=False, initial=True)
    notification_web = forms.BooleanField(label='Web Notifications', required=False, initial=True)

    class Meta:
        model = Profile
        fields = [
            'bio', 'profile_picture', 'location', 'website', 'visibility',
            'theme_color', 'accent_color', 'high_contrast', 'font_size', 'spacing',
            'notification_email', 'notification_web'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.TextInput(attrs={'class': 'form-control'}),
            # 'theme_color': forms.Select(attrs={'class': 'form-select'}),
            # 'accent_color': forms.RadioSelect(attrs={'class': 'accent-color-select'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'theme_color': forms.Select(attrs={'class': 'form-select'}),
            'accent_color': forms.RadioSelect(attrs={'class': 'accent-color-select'}),
            'high_contrast': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'font_size': forms.Select(attrs={'class': 'form-select'}),
            'spacing': forms.Select(attrs={'class': 'form-select'}),
            'notification_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notification_web': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # 'notification_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # 'notification_web': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ChangePasswordForm(DefaultChangePasswordForm):
    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )

    new_password1, new_password2 = SetPasswordMixin.create_password_fields("New Password", "Confirm New Password")

    class Meta:
        model = User
        fields = ['password1', 'password2']
