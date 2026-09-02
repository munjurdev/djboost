"""APScheduler generator — lightweight in-process job scheduler."""

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


def generate_scheduler_config(name: str):
    """Create scheduler configuration."""
    scheduler_content = '''"""
APScheduler configuration — register your jobs here.

Docs: https://django-apscheduler.readthedocs.io
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the scheduler — call this in AppConfig.ready()."""
    from django_apscheduler.jobstores import DjangoJobStore

    scheduler.add_jobstore(DjangoJobStore(), "default")

    # ── Register your jobs here ────────────────────────────────────────────
    # scheduler.add_job(
    #     my_periodic_task,
    #     CronTrigger(minute="*/15"),
    #     id="my_periodic_task",
    #     name="Run every 15 minutes",
    #     replace_existing=True,
    # )

    scheduler.start()
'''
    path = Path(f"{name}/scheduler.py")
    if path.exists():
        print(f"[yellow]Warning: {name}/scheduler.py already exists. Skipping.[/yellow]")
        return False
    path.write_text(scheduler_content, encoding="utf-8")
    print(f"[green]✔ Created {name}/scheduler.py[/green]")
    return True


def add_scheduler_settings(name: str):
    """Add APScheduler settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "APSCHEDULER_DATETIME_FORMAT" in content:
        print("[yellow]Warning: APScheduler already in settings. Skipping.[/yellow]")
        return True

    scheduler_settings = """

# ── APScheduler ─
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
SCHEDULER_DEFAULT = {{
    "max_instances": 3,
    "misfire_grace_time": 300,
}}
"""
    content += scheduler_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added APScheduler settings to {name}/settings.py[/green]")
    return True


def add_scheduler_to_requirements():
    """Add django-apscheduler to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    if "django-apscheduler" not in existing:
        with open(requirements_path, "a", encoding="utf-8") as f:
            f.write("django-apscheduler>=0.7,<1\n")
        print("[green]✔ Added django-apscheduler to requirements.txt[/green]")
    else:
        print("[yellow]Warning: django-apscheduler already in requirements.txt. Skipping.[/yellow]")
