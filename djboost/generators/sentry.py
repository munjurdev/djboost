"""Sentry generator — add Sentry error tracking to a Django project."""

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


def add_sentry_to_settings(name: str):
    """Add Sentry DSN and config to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "SENTRY_DSN" in content:
        print("[yellow]Warning: Sentry already configured in settings.py. Skipping.[/yellow]")
        return True

    sentry_settings = """

# ── Sentry Error Tracking ──────────────────────────────────────────────────────
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_TRACES_SAMPLE_RATE = config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=True,
        environment=config('SENTRY_ENVIRONMENT', default='production'),
    )
"""
    content += sentry_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Sentry config to {name}/settings.py[/green]")
    return True


def add_sentry_to_wsgi(name: str):
    """Add Sentry import to wsgi.py (import happens in settings, but this ensures coverage)."""
    wsgi_path = Path(f"{name}/wsgi.py")
    if not wsgi_path.exists():
        return False
    # Sentry is configured via settings.py import, no wsgi change needed
    return True


def add_sentry_to_requirements():
    """Add sentry-sdk to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    if "sentry-sdk" not in existing:
        with open(requirements_path, "a", encoding="utf-8") as f:
            f.write("sentry-sdk[django]>=2.0,<3\n")
        print("[green]✔ Added sentry-sdk to requirements.txt[/green]")
    else:
        print("[yellow]Warning: sentry-sdk already in requirements.txt. Skipping.[/yellow]")
