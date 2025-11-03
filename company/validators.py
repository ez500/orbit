from django.core.exceptions import ValidationError

from company.models import Company


def validate_email(value):
    if Company.objects.filter(email=value).exists():
        raise ValidationError(f'{value} is already taken.')
