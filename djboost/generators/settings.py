import re


def update_settings_file(settings_path: str, name: str) -> str:
    """Patch Django's generated settings.py with production-ready config."""
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract original SECRET_KEY
    match = re.search(r"SECRET_KEY\s*=\s*(['\"].*?['\"])", content)
    secret_key = match.group(1) if match else "'your-secret-key-here'"

    # ── Imports ───────────────────────────────────────────────────────────────
    content = content.replace(
        "from pathlib import Path",
        (
            "from pathlib import Path\n"
            "from datetime import timedelta\n"
            "from decouple import config\n\n"
            "try:\n"
            "    from celery.schedules import crontab\n"
            "except ImportError:\n"
            "    pass"
        )
    )

    # ── Core Settings ─────────────────────────────────────────────────────────
    content = re.sub(r"SECRET_KEY = .*", "SECRET_KEY = config('SECRET_KEY')", content)
    content = re.sub(r"DEBUG = .*", "DEBUG = config('DEBUG', default=False, cast=bool)", content)
    content = re.sub(
        r"ALLOWED_HOSTS = .*",
        "ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=lambda v: [s.strip() for s in v.split(',')])",
        content
    )

    # ── INSTALLED_APPS ────────────────────────────────────────────────────────
    apps_addition = (
        "    'corsheaders',\n"
        "    'rest_framework',\n"
        "    'rest_framework_simplejwt',\n"
        "    'rest_framework_simplejwt.token_blacklist',\n"
        "    'channels',\n"
        "    'drf_spectacular',"
    )
    content = re.sub(
        r"['\"]django\.contrib\.staticfiles['\"],",
        f"'daphne',\n    'django.contrib.staticfiles',\n{apps_addition}",
        content
    )

    # ── MIDDLEWARE ────────────────────────────────────────────────────────────
    content = content.replace(
        "MIDDLEWARE = [",
        "MIDDLEWARE = [\n    'corsheaders.middleware.CorsMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
    )

    # ── DATABASE ──────────────────────────────────────────────────────────────
    db_config = """DATABASES = {
    'default': {
        'ENGINE': config("DB_ENGINE", default="django.db.backends.sqlite3"),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', default=600, cast=int),
    }
}"""
    content = re.sub(r"DATABASES\s*=\s*\{.*?\}\s*\}", db_config, content, flags=re.DOTALL)

    # ── WSGI / ASGI ───────────────────────────────────────────────────────────
    content = re.sub(
        r"WSGI_APPLICATION\s*=\s*['\"]" + re.escape(name) + r"\.wsgi\.application['\"]",
        f"WSGI_APPLICATION = '{name}.wsgi.application'\nASGI_APPLICATION = '{name}.asgi.application'",
        content
    )

    # ── Static / Media ────────────────────────────────────────────────────────
    static_media_config = (
        "STATIC_URL = '/static/'\n"
        "MEDIA_URL = '/media/'\n\n"
        "STATICFILES_DIRS = [BASE_DIR / 'static']\n"
        "STATIC_ROOT = BASE_DIR / 'assets'\n"
        "MEDIA_ROOT = BASE_DIR / 'media'"
    )
    content = re.sub(r"STATIC_URL\s*=\s*['\"]static/['\"]", static_media_config, content)

    # ── Append Extended Config ────────────────────────────────────────────────
    content += _build_extra_config(name)

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(content)

    return secret_key


def _build_extra_config(name: str) -> str:
    """Return the extra settings block appended at the end of settings.py."""
    return f"""

# ── Caching (Redis) ───────────────────────────────────────────────────────────
CACHES = {{
    "default": {{
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }}
}}

# ── Security & Performance ────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
STORAGES = {{
    "staticfiles": {{
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }},
}}

# ── Django Channels ───────────────────────────────────────────────────────────
CHANNEL_LAYERS = {{
    "default": {{
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {{
            "hosts": [(config("REDIS_HOST", default="127.0.0.1"), config("REDIS_PORT", default=6379, cast=int))],
        }},
    }},
}}

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': '{name}.utils.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {{'anon': '100/day', 'user': '1000/day'}},
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}}

# ── Swagger / ReDoc ───────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {{
    'TITLE': 'API Documentation',
    'DESCRIPTION': 'Project API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}}

# ── Simple JWT ────────────────────────────────────────────────────────────────
SIMPLE_JWT = {{
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}}

# ── CORS & CSRF ───────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [i.strip() for i in config("CSRF_TRUSTED_ORIGINS", "").split(",") if i]
CORS_ALLOWED_ORIGINS = [i.strip() for i in config("CORS_ALLOWED_ORIGINS", "").split(",") if i]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {{
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {{
        "verbose": {{"format": "[{{levelname}}] {{asctime}} {{name}}: {{message}}", "style": "{{"}},
    }},
    "handlers": {{
        "console": {{"class": "logging.StreamHandler", "formatter": "verbose"}},
    }},
    "loggers": {{
        "django": {{"handlers": ["console"], "level": "INFO"}},
        "celery": {{"handlers": ["console"], "level": "INFO"}},
    }},
}}

# ── Celery ────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

CELERY_BEAT_SCHEDULE = {{
    "sample_task": {{
        "task": "{name}.tasks.sample_task",
        "schedule": crontab(minute="*/15"),
    }},
}}
"""
