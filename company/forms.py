from django import forms
from django.db.models import Q

from dashboard.models import Task
from teams.models import Team
from .models import Company, Announcement
from .validators import validate_email


class CompanyRegistrationForm(forms.ModelForm):
    name = forms.CharField(
        label='Company Name',
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    description = forms.CharField(label='Description', max_length=200, required=False)
    logo = forms.ImageField(label='Logo', required=False)
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
        fields = ['name', 'description', 'logo', 'email', 'website', 'phone', 'location']


class CompanyEditForm(forms.ModelForm):
    name = forms.CharField(
        label='Company Name',
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    description = forms.CharField(label='Description', max_length=200, required=False)
    logo = forms.ImageField(label='Logo', required=False)
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
        fields = ["name", "email", "phone", "location", "description", "website", "logo"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email
        if Company.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f'{email} is already taken.')
        return email


class CompanyAnnouncementCreationForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=200, required=True)
    content = forms.CharField(label="Content", required=True, widget=forms.Textarea(attrs={"rows": 4}))
    tasks = forms.ModelMultipleChoiceField(
        label='Related Tasks',
        queryset=Task.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'tasks']

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["tasks"].queryset = Task.objects.filter(
                Q(team__company=company) | Q(project__companies=company)
            ).distinct().order_by("title")


class CompanyAnnouncementEditForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=200, required=True)
    content = forms.CharField(label='Content', required=True)
    tasks = forms.ModelMultipleChoiceField(
        label='Related Tasks',
        queryset=Task.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'tasks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.company_id:
            company = self.instance.company
            self.fields["tasks"].queryset = Task.objects.filter(
                Q(team__company=company) | Q(project__companies=company)
            ).distinct().order_by("title")
