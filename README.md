# StudyHub

A modern **Study Material Sharing Platform** for students — built with Django, PostgreSQL, Tailwind CSS, and Alpine.js.

![StudyHub](https://img.shields.io/badge/Django-6.0-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ready-blue) ![Tailwind](https://img.shields.io/badge/Tailwind-CSS-38bdf8)

## Features

- **Authentication** — Register, login, logout, password reset
- **Study Materials** — Upload PDF, DOCX, PPT, images, ZIP with metadata & tags
- **Search & Filter** — Full-text search, AJAX suggestions, filters, sorting, pagination
- **Interactions** — Likes, star ratings, comments & replies, bookmarks
- **Dashboards** — User stats; admin analytics with Chart.js
- **Moderation** — Approve/reject/delete materials; user management
- **Notifications** — Likes, comments, downloads, approvals
- **UI** — Neo-glassmorphism, bento grid, dark/light theme toggle

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python Django 6 |
| Database | PostgreSQL (SQLite for quick local dev) |
| Frontend | Django Templates + Tailwind CSS + Alpine.js |
| Auth | Django built-in authentication |
| Files | Local `media/` storage |

## Project Structure

```
studyhub/
├── accounts/       # User profiles, registration, login
├── materials/      # Study materials, categories, subjects
├── interactions/   # Likes, ratings, comments, bookmarks
├── dashboard/      # User & admin dashboards
├── core/           # Home, about, notifications
├── config/         # Django settings & URLs
├── templates/      # HTML templates
├── static/         # CSS & JavaScript
└── media/          # Uploaded files
```

## Quick Start

### 1. Clone & virtual environment

```bash
cd studyhub
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment variables

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
USE_SQLITE=True          # Set False for PostgreSQL
```

**PostgreSQL** (when `USE_SQLITE=False`):

```env
DB_NAME=studyhub
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

Create the database:

```sql
CREATE DATABASE studyhub;
```

### 3. Migrate & seed

```bash
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser   # optional
```

### 4. Run server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

### Demo accounts (after seed)

| User | Password | Role |
|------|----------|------|
| admin | admin1234 | Superuser |
| alice | demo1234 | Student |
| bob | demo1234 | Student |
| carol | demo1234 | Student |

## Pages

| URL | Description |
|-----|-------------|
| `/` | Home — hero, bento grid, trending |
| `/materials/browse/` | Browse & filter materials |
| `/materials/<slug>/` | Material detail |
| `/materials/upload/` | Upload (auth required) |
| `/accounts/register/` | Registration |
| `/accounts/login/` | Login |
| `/dashboard/` | User dashboard |
| `/dashboard/admin/` | Admin analytics (staff) |
| `/dashboard/admin/moderate/` | Content moderation |
| `/about/` | About page |

## Security

- CSRF protection on all forms
- XSS escaping via Django templates
- ORM prevents SQL injection
- File type & size validation on upload
- `@login_required` and `@staff_member_required` decorators
- Session cookies HTTP-only

## File Upload Limits

- Max size: **25 MB** (configurable via `MAX_UPLOAD_SIZE_MB`)
- Allowed: `.pdf`, `.docx`, `.ppt`, `.pptx`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.zip`

## Production Checklist

1. Set `DEBUG=False` and strong `SECRET_KEY`
2. Configure PostgreSQL (`USE_SQLITE=False`)
3. Run `python manage.py collectstatic`
4. Use a production WSGI server (gunicorn, uwsgi)
5. Serve media via nginx or object storage
6. Enable HTTPS and secure cookie settings

## License

MIT — Built for educational purposes.
