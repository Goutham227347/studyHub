"""
Remove stale files and optional duplicate DB.

Usage:
  python manage.py cleanup_files              # orphan media only
  python manage.py cleanup_files --remove-sqlite  # also delete unused db.sqlite3
  python manage.py cleanup_files --purge-empty-materials  # DB rows with no file on disk
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from materials.models import StudyMaterial


class Command(BaseCommand):
    help = 'Clean orphan media files and optional duplicate SQLite database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-sqlite',
            action='store_true',
            help='Delete db.sqlite3 when using PostgreSQL (USE_SQLITE=False)',
        )
        parser.add_argument(
            '--purge-empty-materials',
            action='store_true',
            help='Delete StudyMaterial rows whose file is missing on disk',
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            media_root.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f'Created {media_root}')

        # Orphan files on disk (not referenced in DB)
        referenced = set()
        for mat in StudyMaterial.objects.exclude(file=''):
            if mat.file:
                try:
                    referenced.add(Path(mat.file.path).resolve())
                except (ValueError, FileNotFoundError):
                    pass
            if mat.thumbnail:
                try:
                    referenced.add(Path(mat.thumbnail.path).resolve())
                except (ValueError, FileNotFoundError):
                    pass

        removed = 0
        for path in media_root.rglob('*'):
            if path.is_file() and path.resolve() not in referenced:
                path.unlink()
                removed += 1
                self.stdout.write(f'Removed orphan: {path.relative_to(media_root)}')

        if options['purge_empty_materials']:
            with transaction.atomic():
                for mat in StudyMaterial.objects.all():
                    missing = not mat.file or not mat.file.name
                    if not missing:
                        try:
                            missing = not Path(mat.file.path).exists()
                        except ValueError:
                            missing = True
                    if missing:
                        self.stdout.write(f'Removing DB row (no file): {mat.title}')
                        mat.delete()

        if options['remove_sqlite']:
            sqlite_path = settings.BASE_DIR / 'db.sqlite3'
            from decouple import config
            if not config('USE_SQLITE', default=True, cast=bool) and sqlite_path.exists():
                sqlite_path.unlink()
                self.stdout.write(self.style.SUCCESS(f'Deleted duplicate database: {sqlite_path}'))
            elif sqlite_path.exists():
                self.stdout.write(
                    'Skipped db.sqlite3 (set USE_SQLITE=False in .env to remove when using PostgreSQL)'
                )

        self.stdout.write(self.style.SUCCESS(f'Done. Removed {removed} orphan file(s).'))
