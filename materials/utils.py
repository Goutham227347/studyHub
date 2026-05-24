import os
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError

from PIL import Image


def validate_upload_file(file):
    """Validate file extension and size."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(
            f'File type "{ext}" is not allowed. Allowed: {", ".join(settings.ALLOWED_UPLOAD_EXTENSIONS)}'
        )
    if file.size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            f'File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB.'
        )


def generate_thumbnail(material):
    """Generate thumbnail from image files or PDF placeholder."""
    if not material.file:
        return None
    ext = os.path.splitext(material.file.name)[1].lower()
    if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
        try:
            material.file.open('rb')
            img = Image.open(material.file)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            from django.core.files.base import ContentFile
            name = f"thumb_{material.pk or 'new'}.jpg"
            material.thumbnail.save(name, ContentFile(buffer.read()), save=False)
            material.file.close()
            return material.thumbnail
        except Exception:
            return None
    return None
