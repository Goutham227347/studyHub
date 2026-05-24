from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, UniqueConstraint

from materials.models import StudyMaterial


class Comment(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.material.title}"

    @property
    def is_reply(self):
        return self.parent is not None


class Rating(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['material', 'user'], name='unique_rating_per_user'),
        ]

    def __str__(self):
        return f"{self.score}★ by {self.user.username}"


class Like(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['material', 'user'], name='unique_like_per_user'),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.material.title}"


class DownloadHistory(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='download_history')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Download histories'
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"{self.user.username} downloaded {self.material.title}"


class Bookmark(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['material', 'user'], name='unique_bookmark_per_user'),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.material.title}"


class Report(models.Model):
    REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    ]
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REASONS)
    description = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.material.title}"
