"""
Template filters for timezone conversions
"""
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def user_timezone(value, user):
    """
    Convert a datetime to user's preferred timezone
    Usage: {{ task.deadline|user_timezone:request.user }}
    """
    if not value:
        return value

    if not user or not hasattr(user, 'profile'):
        return value

    # Get user's timezone preference
    user_tz_name = getattr(user.profile, 'timezone', 'UTC')

    try:
        user_tz = pytz.timezone(user_tz_name)
    except pytz.exceptions.UnknownTimeZoneError:
        user_tz = pytz.UTC

    # Convert to user's timezone
    if timezone.is_aware(value):
        return value.astimezone(user_tz)
    else:
        # Make aware in UTC first, then convert
        value = timezone.make_aware(value, pytz.UTC)
        return value.astimezone(user_tz)


@register.filter
def user_timezone_date(value, user):
    """
    Convert a datetime to user's preferred timezone and format as date
    Usage: {{ task.deadline|user_timezone_date:request.user }}
    """
    converted = user_timezone(value, user)
    if converted:
        return converted.strftime('%Y-%m-%d')
    return ''


@register.filter
def user_timezone_datetime(value, user):
    """
    Convert a datetime to user's preferred timezone and format as datetime
    Usage: {{ task.deadline|user_timezone_datetime:request.user }}
    """
    converted = user_timezone(value, user)
    if converted:
        return converted.strftime('%Y-%m-%d %H:%M')
    return ''
