"""Redis Cache generator — add Redis-backed caching and session storage."""

import re
from pathlib import Path

from rich import print


def get_project_name():
    """Extract project name from manage.py."""
    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in the project root?[/red]")
        return None
    content = Path("manage.py").read_text(encoding="utf-8")
    match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^.]+)\.settings['\"]", content)
    if match:
        return match.group(1)
    print("[red]Error: Could not determine project name from manage.py[/red]")
    return None


def update_settings_redis_cache(name: str):
    """Add Redis cache and session config to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "CACHES" in content and "django_redis" in content:
        print("[yellow]Warning: Redis cache already configured. Skipping.[/yellow]")
        return True

    cache_settings = """

# ── Redis Cache ─
CACHES = {{
    'default': {{
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {{
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }},
        'KEY_PREFIX': '{name}',
    }}
}}

# Session backend (optional — uses Redis for sessions)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'
""".format(name=name)

    content += cache_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Redis cache config to {name}/settings.py[/green]")
    return True


def update_env_redis_cache(name: str):
    """Update .env with Redis cache variables."""
    env_path = Path(".env")
    if not env_path.exists():
        return False

    content = env_path.read_text(encoding="utf-8")

    if "REDIS_URL" in content:
        print("[yellow]Warning: REDIS_URL already in .env. Skipping.[/yellow]")
        return True

    redis_env = """
# ── Redis Cache ─
REDIS_URL=redis://127.0.0.1:6379/1
"""
    content += redis_env
    env_path.write_text(content, encoding="utf-8")
    print("[green]✔ Added Redis cache vars to .env[/green]")
    return True


def add_redis_cache_to_requirements():
    """Add django-redis to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    packages = []
    if "django-redis" not in existing:
        packages.append("django-redis>=5.4,<6")
    if "redis" not in existing:
        packages.append("redis>=5.0,<6")

    if packages:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for pkg in packages:
                f.write(pkg + "\n")
        print(f"[green]✔ Added {', '.join(packages)} to requirements.txt[/green]")
    else:
        print("[yellow]Warning: Redis packages already in requirements.txt. Skipping.[/yellow]")
