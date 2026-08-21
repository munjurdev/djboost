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


def generate_celery_files(name: str):
    """Generate Celery app configuration and tasks file."""
    
    # Create celery.py
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

    # Create tasks.py
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

    # Update __init__.py
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


def update_settings_celery(name: str):
    """Add Celery settings to settings.py if not present."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False
    
    content = settings_path.read_text(encoding="utf-8")
    
    # Check if Celery is already configured
    if "CELERY_BROKER_URL" in content:
        print("[yellow]Warning: Celery is already configured in settings.py. Skipping.[/yellow]")
        return True
    
    # Add Celery settings at the end
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


# Note: Celery packages (celery, redis) are installed via
# djboost.generators.dependencies.install_optional_packages('celery')
