from django.db.models import Q

from core.models import Notification


def site_context(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
    return {
        'unread_notifications': unread_notifications,
        'site_name': 'StudyHub',
    }
