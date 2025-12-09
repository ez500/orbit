from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm as DefaultChangePasswordForm

from .models import Profile
from .validators import validate_email

# Common timezone choices
TIMEZONE_CHOICES = [
    ('UTC', 'UTC'),
    ('US/Eastern', 'Eastern Time (US & Canada)'),
    ('US/Central', 'Central Time (US & Canada)'),
    ('US/Mountain', 'Mountain Time (US & Canada)'),
    ('US/Pacific', 'Pacific Time (US & Canada)'),
    ('US/Alaska', 'Alaska'),
    ('US/Hawaii', 'Hawaii'),
    ('Europe/London', 'London'),
    ('Europe/Paris', 'Paris'),
    ('Europe/Berlin', 'Berlin'),
    ('Europe/Rome', 'Rome'),
    ('Europe/Madrid', 'Madrid'),
    ('Asia/Tokyo', 'Tokyo'),
    ('Asia/Shanghai', 'Shanghai'),
    ('Asia/Hong_Kong', 'Hong Kong'),
    ('Asia/Singapore', 'Singapore'),
    ('Asia/Dubai', 'Dubai'),
    ('Asia/Kolkata', 'India Standard Time'),
    ('Australia/Sydney', 'Sydney'),
    ('Australia/Melbourne', 'Melbourne'),
    ('Pacific/Auckland', 'Auckland'),
]


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
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'})
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Username',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        max_length=254,
        required=False,
        help_text='Must be a valid E-mail address.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # If username is empty, it means the user didn't change it, so skip validation
        if not username:
            # Get the original username from the instance
            return self.instance.username
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f'{username} is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # If email is empty, it means the user didn't change it, so skip validation
        if not email:
            # Get the original email from the instance
            return self.instance.email
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f'{email} is already taken.')
        return email


class UpdateProfileForm(forms.ModelForm):
    bio = forms.CharField(label='Bio', max_length=127, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    profile_picture = forms.ImageField(label='Profile Picture', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    location = forms.CharField(label='Location', max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    website = forms.URLField(label='Website', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    theme_color = forms.ChoiceField(
        label='Theme Color',
        choices=Profile.THEME_CHOICES,
        initial='dark',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    accent_color = forms.ChoiceField(
        label='Accent Color',
        choices=Profile.ACCENT_CHOICES,
        initial='#1E90FF',
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'accent-color-select'})
    )
    visibility = forms.ChoiceField(
        label='Profile Visibility',
        choices=[(tag.name, tag.value) for tag in Profile.Visibility],
        initial=Profile.Visibility.PUBLIC.name,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Accessibility / appearance preferences
    high_contrast = forms.BooleanField(label='High Contrast', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    font_size = forms.ChoiceField(
        label='Font size',
        choices=Profile.FONT_SIZE_CHOICES,
        initial='medium',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    spacing = forms.ChoiceField(
        label='Spacing',
        choices=Profile.SPACING_CHOICES,
        initial='normal',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    timezone = forms.ChoiceField(
        label='Timezone',
        choices=TIMEZONE_CHOICES,
        initial='UTC',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notification_email = forms.BooleanField(label='Email Notifications', required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    notification_web = forms.BooleanField(label='Web Notifications', required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = Profile
        fields = [
            'bio', 'location', 'website', 'visibility',
            'theme_color', 'accent_color', 'high_contrast', 'font_size', 'spacing',
            'timezone', 'notification_email', 'notification_web'
        ]
    
    def clean_profile_picture(self):
        """Handle profile picture upload"""
        profile_picture = self.cleaned_data.get('profile_picture')
        # If no new picture was uploaded, keep the existing one
        if not profile_picture:
            return self.instance.profile_picture
        return profile_picture
    
    def save(self, commit=True):
        """Override save to handle profile_picture separately"""
        instance = super().save(commit=False)
        
        # Handle profile picture if it was uploaded
        if 'profile_picture' in self.cleaned_data and self.cleaned_data['profile_picture']:
            instance.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            instance.save()
        return instance


class ChangePasswordForm(DefaultChangePasswordForm):
    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "class": "form-control"}
        ),
    )

    new_password1, new_password2 = SetPasswordMixin.create_password_fields("New Password", "Confirm New Password")

    class Meta:
        model = User
        fields = ['password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name in self.fields:
            if hasattr(self.fields[field_name].widget, 'attrs'):
                self.fields[field_name].widget.attrs['class'] = 'form-control'
