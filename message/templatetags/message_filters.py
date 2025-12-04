from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe
from zoneinfo import ZoneInfo
import re

register = template.Library()

@register.filter
def user_timezone(value, user):
    """Convert a datetime to the user's timezone"""
    if not value:
        return ""

    # Get user's timezone from their profile
    try:
        user_tz = user.profile.timezone or 'UTC'
    except:
        user_tz = 'UTC'

    try:
        tz = ZoneInfo(user_tz)
        # Convert to user's timezone
        local_time = value.astimezone(tz)
        return local_time
    except:
        # If timezone is invalid, return original value
        return value

@register.filter
def highlight_mentions(text):
    """Highlight @mentions in message content"""
    if not text:
        return ""

    # Replace @username with highlighted span
    # \w+ matches one or more word characters (letters, digits, underscore)
    highlighted = re.sub(r'@(\w+)', r'<span class="mention">@\1</span>', text)

    return mark_safe(highlighted)
