from django.db.models import Max

from dashboard.models import Notification, InsightSuggestion


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {'count': 0, 'unread': []}

    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    count = notifications.count()

    return {'count': count, 'unread': notifications}


# TODO FIX BUG OF RELOADING INSIGHTS FOR CERTAIN ACTIONS
# TODO APPLY ORBIT INSIGHT RELEVANT FEATURES TO ALL PAGES
def recall_orbit_insights(request):
    if not request.user.is_authenticated:
        return {}

    latest_batch_time = InsightSuggestion.objects.aggregate(max_field_value=Max('created_at'))['max_field_value']
    if not InsightSuggestion.objects.filter(user=request.user).exists():
        return {}
    latest_batch_id = InsightSuggestion.objects.filter(user=request.user, created_at=latest_batch_time).first().batch_id
    recall_insights = InsightSuggestion.objects.filter(user=request.user, batch_id=latest_batch_id, executed=False)

    context = dict()
    context['orbit_insights'] = recall_insights
    context['create_task_event_insights'] = (recall_insights.filter(suggestion_type='create_task')
                                             | recall_insights.filter(suggestion_type='create_event'))
    context['create_announcement_insights'] = recall_insights.filter(suggestion_type='create_announcement')

    return context
