"""
Management command to seed StudyHub with demo data.
Usage: python manage.py seed_data
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from materials.models import Category, Subject


class Command(BaseCommand):
    help = 'Seed database with categories, subjects, demo users and materials'

    def handle(self, *args, **options):
        self.stdout.write('Seeding StudyHub...')

        categories_data = [
            ('Engineering', '🛠️', '#8b5cf6'),
            ('Science', '🔬', '#3b82f6'),
            ('Business', '💼', '#06b6d4'),
            ('Arts', '🎨', '#ec4899'),
            ('Medicine', '⚕️', '#10b981'),
            ('Law', '⚖️', '#f59e0b'),
        ]
        categories = {}
        for name, icon, color in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={'icon': icon, 'color': color}
            )
            categories[name] = cat

        subjects_data = [
            ('Computer Science', 'Engineering'),
            ('Mathematics', 'Science'),
            ('Physics', 'Science'),
            ('Economics', 'Business'),
            ('Organic Chemistry', 'Science'),
            ('Data Structures', 'Engineering'),
        ]
        subjects = {}
        for name, cat_name in subjects_data:
            sub, _ = Subject.objects.get_or_create(
                name=name, defaults={'category': categories[cat_name]}
            )
            subjects[name] = sub

        demo_users = [
            ('alice', 'alice@studyhub.edu', 'Computer Science', 'MIT'),
            ('bob', 'bob@studyhub.edu', 'Mathematics', 'Stanford'),
            ('carol', 'carol@studyhub.edu', 'Physics', 'Caltech'),
        ]
        users = {}
        for username, email, dept, college in demo_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': username.title()},
            )
            if created:
                user.set_password('demo1234')
                user.save()
            profile = user.profile
            profile.department = dept
            profile.college_name = college
            profile.bio = f'Student passionate about {dept}.'
            profile.save()
            users[username] = user

        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@studyhub.edu', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin.set_password('admin1234')
            admin.save()
        self.stdout.write(self.style.SUCCESS('Admin: admin / admin1234'))

        self.stdout.write(self.style.SUCCESS('Admin: admin / admin1234'))

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {Category.objects.count()} categories, '
            f'{Subject.objects.count()} subjects, '
            f'{len(users)} demo users.'
        ))
        self.stdout.write('Demo users: alice/bob/carol — password: demo1234')
        self.stdout.write('Upload real files at /materials/upload/ (seed does not create fake file records).')
