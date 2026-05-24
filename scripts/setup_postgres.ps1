# StudyHub — PostgreSQL setup helper (Windows)
# Run from project root:  .\scripts\setup_postgres.ps1

param(
    [string]$DbName = "studyhub",
    [string]$DbUser = "postgres",
    [string]$DbPassword = "1234",
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$PgVersion = "18"
)

$ErrorActionPreference = "Stop"
$psql = "C:\Program Files\PostgreSQL\$PgVersion\bin\psql.exe"
$createdb = "C:\Program Files\PostgreSQL\$PgVersion\bin\createdb.exe"

if (-not (Test-Path $psql)) {
    Write-Host "PostgreSQL not found at: $psql" -ForegroundColor Red
    Write-Host "Install from: https://www.postgresql.org/download/windows/"
    Write-Host "Or set -PgVersion to your installed version (e.g. 16, 17, 18)."
    exit 1
}

$env:PGPASSWORD = $DbPassword

Write-Host "Checking PostgreSQL connection..." -ForegroundColor Cyan
& $psql -U $DbUser -h $DbHost -p $DbPort -c "SELECT version();" | Out-Null
Write-Host "Connected OK." -ForegroundColor Green

$exists = & $psql -U $DbUser -h $DbHost -p $DbPort -t -c "SELECT 1 FROM pg_database WHERE datname='$DbName';"
if ($exists -match "1") {
    Write-Host "Database '$DbName' already exists." -ForegroundColor Yellow
} else {
    Write-Host "Creating database '$DbName'..." -ForegroundColor Cyan
    & $createdb -U $DbUser -h $DbHost -p $DbPort $DbName
    Write-Host "Database created." -ForegroundColor Green
}

# Ensure .env uses PostgreSQL
$envPath = Join-Path $PSScriptRoot "..\.env"
$envExample = @"
USE_SQLITE=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DbName
DB_USER=$DbUser
DB_PASSWORD=$DbPassword
DB_HOST=$DbHost
DB_PORT=$DbPort
"@

Write-Host ""
Write-Host "Add these to your .env file (if not already set):" -ForegroundColor Cyan
Write-Host $envExample

Write-Host ""
Write-Host "Running Django migrations..." -ForegroundColor Cyan
Push-Location (Join-Path $PSScriptRoot "..")
& .\venv\Scripts\python.exe manage.py migrate
& .\venv\Scripts\python.exe manage.py seed_data
Pop-Location

Write-Host ""
Write-Host "Done! Start the server with:" -ForegroundColor Green
Write-Host "  .\venv\Scripts\python manage.py runserver"
