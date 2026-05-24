from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


class MaterialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'materials'

    def ready(self):
        media_root = Path(settings.MEDIA_ROOT)
        for subdir in ('materials', 'thumbnails', 'profiles'):
            (media_root / subdir).mkdir(parents=True, exist_ok=True)
