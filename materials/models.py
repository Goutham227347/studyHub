import os
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Emoji or icon class')
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#8b5cf6')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='subjects')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StudyMaterial(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('ppt', 'PPT/PPTX'),
        ('image', 'Image'),
        ('zip', 'ZIP'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    semester = models.PositiveSmallIntegerField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    file = models.FileField(upload_to='materials/%Y/%m/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default='other')
    file_size = models.PositiveIntegerField(default=0, help_text='Size in bytes')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    is_featured = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['-download_count']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            slug = base
            counter = 1
            while StudyMaterial.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.file_type:
            self.file_type = self.detect_file_type()
        super().save(*args, **kwargs)

    def detect_file_type(self):
        ext = os.path.splitext(self.file.name)[1].lower()
        mapping = {
            '.pdf': 'pdf', '.docx': 'docx', '.doc': 'docx',
            '.ppt': 'ppt', '.pptx': 'ppt',
            '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.gif': 'image', '.webp': 'image',
            '.zip': 'zip',
        }
        return mapping.get(ext, 'other')

    def get_absolute_url(self):
        return reverse('materials:detail', kwargs={'slug': self.slug})

    @property
    def file_size_display(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != 'B' else f"{size} B"
            size /= 1024
        return f"{size:.1f} GB"

    @property
    def average_rating(self):
        from django.db.models import Avg
        result = self.ratings.aggregate(avg=Avg('score'))
        return round(result['avg'] or 0, 1)

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def is_approved(self):
        return self.status == 'approved'


class MaterialView(models.Model):
    """Track recently viewed materials per user/session."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='recent_views')
    session_key = models.CharField(max_length=40, blank=True)
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
