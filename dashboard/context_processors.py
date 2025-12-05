from dashboard.models import Notification


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {'count': 0, 'unread': []}

    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    count = notifications.count()

    return {'count': count, 'unread': notifications}
