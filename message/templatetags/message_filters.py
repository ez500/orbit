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

def linkify_urls(text):
    """Convert URLs in text to clickable links"""
    # URL pattern - matches http://, https://, and www. URLs
    url_pattern = r'(https?://[^\s]+)|(www\.[^\s]+)'

    def replace_url(match):
        url = match.group(0)
        href = url

        # Add https:// to www. URLs
        if url.startswith('www.'):
            href = 'https://' + url

        # Truncate display URL if too long
        display_url = url
        if len(url) > 50:
            display_url = url[:47] + '...'

        return f'<a href="{href}" class="message-link" target="_blank" rel="noopener noreferrer">{display_url}</a>'

    return re.sub(url_pattern, replace_url, text)

@register.filter
def highlight_mentions(text):
    """Highlight @mentions and linkify URLs in message content"""
    if not text:
        return ""

    # Replace @username with highlighted span
    # \w+ matches one or more word characters (letters, digits, underscore)
    highlighted = re.sub(r'@(\w+)', r'<span class="mention">@\1</span>', text)

    # Linkify URLs
    linked = linkify_urls(highlighted)

    return mark_safe(linked)
