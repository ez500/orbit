from django import template

from dashboard.serializer import TaskViewSerializer, EventViewSerializer

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


@register.filter
def tasks_to_serialized_data(tasks_list):
    return TaskViewSerializer(tasks_list, many=True).data


@register.filter
def events_to_serialized_data(events_list):
    return EventViewSerializer(events_list, many=True).data
