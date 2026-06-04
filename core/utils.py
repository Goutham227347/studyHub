from typing import Optional
from django.contrib.auth.models import User

from .models import Notification


def notify_user(
    recipient: User,
    title: str,
    message: str,
    notification_type: str = 'system',
    link: str = ''
) -> Notification:
    """Create a notification for a user.
    
    Args:
        recipient: The User object to receive the notification
        title: Notification title (max 200 chars)
        message: Notification message/body
        notification_type: Type of notification (like, comment, download, approval, rejection, system)
        link: Optional URL link for the notification
        
    Returns:
        The created Notification object
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
