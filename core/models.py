from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    TYPES = [
        ('like', 'New Like'),
        ('comment', 'New Comment'),
        ('download', 'New Download'),
        ('approval', 'Material Approved'),
        ('rejection', 'Material Rejected'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.recipient.username}"
