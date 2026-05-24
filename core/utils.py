from .models import Notification


def notify_user(recipient, title, message, notification_type='system', link=''):
    """Create a notification for a user."""
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
