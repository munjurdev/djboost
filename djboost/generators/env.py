def generate_env_file(secret_key: str, name: str):
    """Generate a pre-filled .env file."""
    content = f"""# ── Django ────────────────────────────────────────────────────────────────────
DEBUG=True
SECRET_KEY={secret_key}
ALLOWED_HOSTS=localhost,127.0.0.1

# ── CORS & CSRF ───────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:8000
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:8000

# ── Database (uncomment to use PostgreSQL) ────────────────────────────────────
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME={name}_db
# DB_USER={name}_user
# DB_PASSWORD=your-db-password
# DB_HOST=localhost
# DB_PORT=5432
# CONN_MAX_AGE=600

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ── Email (SMTP) ──────────────────────────────────────────────────────────────
EMAIL_USE_SSL=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=465
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
"""
    with open(".env", "w", encoding="utf-8") as f:
        f.write(content)
