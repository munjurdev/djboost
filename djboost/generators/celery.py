"""Celery generators — add, beat, remove — all in one file."""

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


# ── ADD CELERY ────────────────────────────────────────────────────────────────


def generate_celery_files(name):
    """Generate Celery app configuration and tasks file."""

    celery_content = f"""import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')

app = Celery('{name}')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {{self.request!r}}')
"""
    celery_path = Path(f"{name}/celery.py")
    if celery_path.exists():
        print(f"[yellow]Warning: {name}/celery.py already exists. Skipping.[/yellow]")
    else:
        celery_path.write_text(celery_content, encoding="utf-8")
        print(f"[green]✔ Created {name}/celery.py[/green]")

    tasks_content = f"""from celery import shared_task


@shared_task
def sample_task():
    \"\"\"Sample Celery task - replace with your own logic.\"\"\"
    print("sample_task is running!")
    return "done"


# ── Example: send email async ─────────────────────────────────────────────────
# @shared_task
# def send_welcome_email(user_id):
#     from django.contrib.auth import get_user_model
#     User = get_user_model()
#     user = User.objects.get(id=user_id)
#     # send_mail(subject, message, from_email, [user.email])
#     return f"Email sent to {{user.email}}"
"""
    tasks_path = Path(f"{name}/tasks.py")
    if tasks_path.exists():
        print(f"[yellow]Warning: {name}/tasks.py already exists. Skipping.[/yellow]")
    else:
        tasks_path.write_text(tasks_content, encoding="utf-8")
        print(f"[green]✔ Created {name}/tasks.py[/green]")

    init_path = Path(f"{name}/__init__.py")
    init_content = """from .celery import app as celery_app

__all__ = ('celery_app',)
"""
    if init_path.exists():
        existing = init_path.read_text(encoding="utf-8")
        if "celery_app" not in existing:
            init_path.write_text(init_content, encoding="utf-8")
            print(f"[green]✔ Updated {name}/__init__.py with Celery app[/green]")
        else:
            print(f"[yellow]Warning: {name}/__init__.py already has Celery app. Skipping.[/yellow]")
    else:
        init_path.write_text(init_content, encoding="utf-8")
        print(f"[green]✔ Created {name}/__init__.py[/green]")


def update_settings_celery(name):
    """Add Celery settings to settings.py if not present."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "CELERY_BROKER_URL" in content:
        print("[yellow]Warning: Celery is already configured in settings.py. Skipping.[/yellow]")
        return True

    if "from celery.schedules import crontab" not in content:
        content = content.replace(
            "from decouple import config", "from decouple import config\nfrom celery.schedules import crontab"
        )

    celery_settings = """

# ── Celery (Background Tasks) ────────────────────────────────────────────────
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

CELERY_BEAT_SCHEDULE = {
    # "sample_task": {
    #     "task": "{name}.tasks.sample_task",
    #     "schedule": crontab(minute="*/15"),
    # },
}
"""

    content += celery_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Celery settings to {name}/settings.py[/green]")
    return True


# ── ADD CELERY BEAT ───────────────────────────────────────────────────────────


def generate_celery_beat_config(name):
    """Add Celery Beat schedule settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "CELERY_BEAT_SCHEDULE" in content and "schedule" in content:
        print("[yellow]Warning: Celery Beat is already configured in settings.py. Skipping.[/yellow]")
        return True

    if "CELERY_BROKER_URL" not in content:
        print("[red]Error: Celery is not configured. Please run 'djboost add celery' first.[/red]")
        return False

    beat_pattern = r"\nCELERY_BEAT_SCHEDULE\s*=\s*\{[^}]*\}"
    content = re.sub(beat_pattern, "", content, flags=re.DOTALL)

    beat_settings = """

# ── Celery Beat Schedule ─────────────────────────────────────────────────────
CELERY_BEAT_SCHEDULE = {
    # "sample-periodic-task": {
    #     "task": "{name}.tasks.sample_task",
    #     "schedule": crontab(minute="*/15"),
    # },
    # "daily-cleanup": {
    #     "task": "{name}.tasks.cleanup_task",
    #     "schedule": crontab(hour=0, minute=0),
    # },
}
"""

    content += beat_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Celery Beat schedule to {name}/settings.py[/green]")
    return True


def add_crontab_import(name):
    """Ensure crontab is imported in settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "crontab" in content and "import" in content:
        print("[yellow]Warning: crontab already imported in settings.py. Skipping.[/yellow]")
        return True

    try_import = """
try:
    from celery.schedules import crontab
except ImportError:
    pass
"""
    content = content.replace("from decouple import config", "from decouple import config\n" + try_import)

    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added crontab import to {name}/settings.py[/green]")
    return True


# ── REMOVE CELERY ─────────────────────────────────────────────────────────────


def remove_celery_files(name):
    """Remove Celery-related files from the project."""
    files_to_remove = [Path(f"{name}/celery.py"), Path(f"{name}/tasks.py")]

    removed_files = []
    for file_path in files_to_remove:
        if file_path.exists():
            file_path.unlink()
            removed_files.append(str(file_path))
            print(f"[green]✔ Removed {file_path}[/green]")
        else:
            print(f"[yellow]Warning: {file_path} not found. Skipping.[/yellow]")

    return removed_files


def remove_celery_from_init(name):
    """Remove Celery app from __init__.py."""
    init_path = Path(f"{name}/__init__.py")
    if not init_path.exists():
        print(f"[yellow]Warning: {name}/__init__.py not found. Skipping.[/yellow]")
        return False

    content = init_path.read_text(encoding="utf-8")

    if "celery_app" not in content:
        print(f"[yellow]Warning: Celery not configured in {name}/__init__.py. Skipping.[/yellow]")
        return True

    content = content.replace("from .celery import app as celery_app\n\n__all__ = ('celery_app',)", "")

    if not content.strip():
        content = "# This file is intentionally left blank.\n"

    init_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Removed Celery app from {name}/__init__.py[/green]")
    return True


def remove_celery_from_settings(name):
    """Remove Celery settings from settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "CELERY_BROKER_URL" not in content:
        print("[yellow]Warning: Celery not configured in settings.py. Skipping.[/yellow]")
        return True

    celery_pattern = r"\n# ── Celery \(Background Tasks\) ─.*?(?=\n# ──|\Z)"
    content = re.sub(celery_pattern, "", content, flags=re.DOTALL)

    beat_pattern = r"\nCELERY_BEAT_SCHEDULE\s*=\s*\{[^}]*\}"
    content = re.sub(beat_pattern, "", content, flags=re.DOTALL)

    content = content.replace("\ntry:\n    from celery.schedules import crontab\nexcept ImportError:\n    pass", "")

    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Removed Celery settings from {name}/settings.py[/green]")
    return True


def remove_celery_from_requirements():
    """Remove Celery and Redis from requirements.txt."""
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("[yellow]Warning: requirements.txt not found. Skipping.[/yellow]")
        return False

    content = requirements_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    packages_to_remove = ["celery", "redis"]
    removed_packages = []
    new_lines = []

    for line in lines:
        line_stripped = line.strip()
        should_remove = False

        for package in packages_to_remove:
            if line_stripped.lower().startswith(package + ">=") or line_stripped.lower() == package:
                should_remove = True
                removed_packages.append(line_stripped)
                break

        if not should_remove:
            new_lines.append(line)

    if removed_packages:
        requirements_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"[green]✔ Removed {len(removed_packages)} package(s) from requirements.txt[/green]")
        for pkg in removed_packages:
            print(f"  [dim]  - {pkg}[/dim]")
    else:
        print("[yellow]Warning: Celery packages not found in requirements.txt. Skipping.[/yellow]")

    return True
