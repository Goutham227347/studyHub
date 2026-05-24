# PostgreSQL Setup for StudyHub (Windows)

## Your current setup (verified)

| Setting | Value |
|---------|--------|
| PostgreSQL | **18.4** (`C:\Program Files\PostgreSQL\18\`) |
| Database | `studyhub` |
| User | `postgres` |
| Host / Port | `localhost` / `5432` |
| Django | `USE_SQLITE=False` in `.env` |

Migrations are applied and Django connects successfully.

---

## 1. Install PostgreSQL (if not installed)

1. Download: https://www.postgresql.org/download/windows/
2. Run the installer (EDB installer is fine).
3. Remember the **postgres user password** you set during install.
4. Keep default port **5432**.
5. Optionally install **pgAdmin 4** (GUI).

Or via winget:

```powershell
winget install PostgreSQL.PostgreSQL.18
```

---

## 2. Start PostgreSQL service

```powershell
# Check service name (often postgresql-x64-18)
Get-Service *postgres*

# Start if stopped
Start-Service postgresql-x64-18
```

Or: **Services** app → find `postgresql-x64-18` → Start.

---

## 3. Create the database

Open **SQL Shell (psql)** from Start Menu, or PowerShell:

```powershell
$env:PGPASSWORD = "YOUR_POSTGRES_PASSWORD"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE studyhub;"
```

If the database already exists, skip this step.

---

## 4. Configure StudyHub `.env`

In the project root, edit `.env`:

```env
USE_SQLITE=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=studyhub
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=localhost
DB_PORT=5432
```

**Important:** `DB_PASSWORD` must match the password you chose when installing PostgreSQL.

---

## 5. Run migrations

```powershell
cd c:\Users\LENOVO\Desktop\studyhub
.\venv\Scripts\activate
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Or use the helper script:

```powershell
.\scripts\setup_postgres.ps1 -DbPassword "YOUR_POSTGRES_PASSWORD"
```

---

## 6. Verify connection

```powershell
python manage.py dbshell
```

In psql:

```sql
\dt
SELECT COUNT(*) FROM auth_user;
\q
```

---

## Troubleshooting

### `connection refused` / could not connect

- PostgreSQL service is not running → start `postgresql-x64-18`.
- Wrong port → check `DB_PORT=5432`.

### `password authentication failed`

- Update `DB_PASSWORD` in `.env` to match your postgres user password.
- Reset password in pgAdmin or psql:

```sql
ALTER USER postgres PASSWORD 'newpassword';
```

### `database "studyhub" does not exist`

```powershell
$env:PGPASSWORD = "yourpassword"
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres studyhub
python manage.py migrate
```

### Switch back to SQLite (temporary)

In `.env`:

```env
USE_SQLITE=True
```

### pgAdmin

1. Open pgAdmin → Servers → PostgreSQL 18.
2. Connect with your postgres password.
3. Databases → `studyhub` → browse tables.

---

## Production notes

- Use a dedicated DB user (not `postgres`) with limited privileges.
- Set strong `SECRET_KEY`, `DEBUG=False`.
- Enable SSL for remote DB hosts if applicable.
