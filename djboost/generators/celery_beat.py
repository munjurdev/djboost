import re
from pathlib import Path
from rich import print


def generate_celery_beat_config(name: str):
    """Add Celery Beat schedule settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False
    
    content = settings_path.read_text(encoding="utf-8")
    
    # Check if Celery Beat is already configured
    if "CELERY_BEAT_SCHEDULE" in content and "schedule" in content:
        print("[yellow]Warning: Celery Beat is already configured in settings.py. Skipping.[/yellow]")
        return True
    
    # Check if Celery is configured at all
    if "CELERY_BROKER_URL" not in content:
        print("[red]Error: Celery is not configured. Please run 'djboost add celery' first.[/red]")
        return False
    
    # Remove existing CELERY_BEAT_SCHEDULE if present but empty
    beat_pattern = r"\nCELERY_BEAT_SCHEDULE\s*=\s*\{[^}]*\}"
    content = re.sub(beat_pattern, "", content, flags=re.DOTALL)
    
    # Add Celery Beat schedule
    beat_settings = """

# ── Celery Beat Schedule ─────────────────────────────────────────────────────
CELERY_BEAT_SCHEDULE = {
    # "sample-periodic-task": {
    #     "task": "{name}.tasks.sample_task",
    #     "schedule": crontab(minute="*/15"),  # Every 15 minutes
    # },
    # "daily-cleanup": {
    #     "task": "{name}.tasks.cleanup_task",
    #     "schedule": crontab(hour=0, minute=0),  # Every day at midnight
    # },
    # "weekly-report": {
    #     "task": "{name}.tasks.weekly_report",
    #     "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Every Monday at 8 AM
    # },
}
"""
    
    content += beat_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Celery Beat schedule to {name}/settings.py[/green]")
    return True


def add_crontab_import(name: str):
    """Ensure crontab is imported in settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        return False
    
    content = settings_path.read_text(encoding="utf-8")
    
    # Check if crontab is already imported
    if "crontab" in content and "import" in content:
        print("[yellow]Warning: crontab already imported in settings.py. Skipping.[/yellow]")
        return True
    
    # Add crontab import
    try_import = """
try:
    from celery.schedules import crontab
except ImportError:
    pass
"""
    
    # Add after existing imports
    content = content.replace(
        "from decouple import config",
        "from decouple import config\n" + try_import
    )
    
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added crontab import to {name}/settings.py[/green]")
    return True
