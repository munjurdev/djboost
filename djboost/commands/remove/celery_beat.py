"""djboost remove celery-beat — remove Celery Beat scheduler."""
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment


def remove_celery_beat_command():
    """Remove Celery Beat from the project."""
    check_virtual_environment()
    
    print("\n[bold green]🔄 Removing Celery Beat...[/bold green]\n")
    
    settings_files = list(Path(".").glob("*/settings.py"))
    if not settings_files:
        print("[red]Error: settings.py not found.[/red]")
        return
    
    settings_path = settings_files[0]
    settings_content = settings_path.read_text(encoding="utf-8")
    
    # 1. Remove crontab import
    if "from celery.schedules import crontab" in settings_content:
        settings_content = settings_content.replace("from celery.schedules import crontab\n", "")
        print("[green]✔ Removed crontab import from settings.py[/green]")
    else:
        print("[yellow]⚠ crontab import not found, skipping[/yellow]")
    
    # 2. Remove CELERY_BEAT_SCHEDULE
    if "CELERY_BEAT_SCHEDULE" in settings_content:
        # Remove the entire block
        settings_content = re.sub(
            r"\n# ── Celery Beat.*?}\n",
            "\n",
            settings_content,
            flags=re.DOTALL
        )
        # Also try simpler pattern
        settings_content = re.sub(
            r"CELERY_BEAT_SCHEDULE\s*=\s*\{.*?\}\s*\n",
            "",
            settings_content,
            flags=re.DOTALL
        )
        print("[green]✔ Removed CELERY_BEAT_SCHEDULE from settings.py[/green]")
    else:
        print("[yellow]⚠ CELERY_BEAT_SCHEDULE not found, skipping[/yellow]")
    
    # Save settings
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(settings_content)
    
    # 3. Remove from requirements.txt
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        content = requirements_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = [line for line in lines if "celery-beat" not in line.lower()]
        requirements_path.write_text("\n".join(new_lines), encoding="utf-8")
        print("[green]✔ Removed celery-beat from requirements.txt[/green]")
    
    print()
    print("[bold green]✅ Celery Beat removed successfully![/bold green]")
    print()
    print("[cyan]Note:[/cyan] Celery worker is still installed.")
    print("  Run [bold]djboost remove celery[/bold] to remove Celery completely.")
    print()
