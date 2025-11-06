from django import template

register = template.Library()

_STATUS_TO_COLOR = {
    'completed': 'success',
    'in_progress': 'warning',
    'review': 'info',
    'todo': 'danger',
}

@register.filter
def status_badge(status):
    color = _STATUS_TO_COLOR.get(status, 'danger')
    return f"bg-{color}-subtle text-{color}"
