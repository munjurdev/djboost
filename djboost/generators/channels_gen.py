"""Django Channels generator — add WebSocket and async support."""
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


def generate_asgi_file(name: str):
    """Create ASGI application file with Channels routing."""
    asgi_content = '''"""
ASGI config for {name} project.

Docs: https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')

django_asgi_app = get_asgi_application()

try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from django.urls import path

    application = ProtocolTypeRouter({{
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter([])
        ),
    }})
except ImportError:
    application = django_asgi_app
'''.format(name=name)

    path = Path(f"{name}/asgi.py")
    if path.exists():
        print(f"[yellow]Warning: {name}/asgi.py already exists. Skipping.[/yellow]")
        return False
    path.write_text(asgi_content, encoding="utf-8")
    print(f"[green]✔ Created {name}/asgi.py[/green]")
    return True


def update_settings_channels(name: str):
    """Add Channels settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "ASGI_APPLICATION" in content and "channels" in content.lower():
        print("[yellow]Warning: Channels already configured. Skipping.[/yellow]")
        return True

    # Add daphne to INSTALLED_APPS (must be first)
    if "'daphne'" not in content:
        content = content.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'daphne',",
        )

    channels_settings = """

# ── Django Channels ────────────────────────────────────────────────────────────
ASGI_APPLICATION = '{name}.asgi.application'

CHANNEL_LAYERS = {{
    'default': {{
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {{
            'hosts': [(
                config('REDIS_HOST', default='127.0.0.1'),
                config('REDIS_PORT', default=6379, cast=int),
            )],
        }},
    }},
}}
""".format(name=name)

    content += channels_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Channels config to {name}/settings.py[/green]")
    return True


def add_channels_to_requirements():
    """Add channels packages to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    packages = []
    if "daphne" not in existing:
        packages.append("daphne>=4.1,<5")
    if "channels" not in existing:
        packages.append("channels>=4.1,<5")
    if "channels-redis" not in existing:
        packages.append("channels-redis>=4.2,<5")

    if packages:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for pkg in packages:
                f.write(pkg + "\n")
        print(f"[green]✔ Added {', '.join(packages)} to requirements.txt[/green]")
    else:
        print("[yellow]Warning: Channels packages already in requirements.txt. Skipping.[/yellow]")
