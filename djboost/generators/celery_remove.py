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


def remove_celery_files(name: str):
    """Remove Celery-related files from the project."""
    files_to_remove = [
        Path(f"{name}/celery.py"),
        Path(f"{name}/tasks.py"),
    ]
    
    removed_files = []
    for file_path in files_to_remove:
        if file_path.exists():
            file_path.unlink()
            removed_files.append(str(file_path))
            print(f"[green]✔ Removed {file_path}[/green]")
        else:
            print(f"[yellow]Warning: {file_path} not found. Skipping.[/yellow]")
    
    return removed_files


def remove_celery_from_init(name: str):
    """Remove Celery app from __init__.py."""
    init_path = Path(f"{name}/__init__.py")
    if not init_path.exists():
        print(f"[yellow]Warning: {name}/__init__.py not found. Skipping.[/yellow]")
        return False
    
    content = init_path.read_text(encoding="utf-8")
    
    # Check if Celery is configured
    if "celery_app" not in content:
        print(f"[yellow]Warning: Celery not configured in {name}/__init__.py. Skipping.[/yellow]")
        return True
    
    # Remove Celery imports
    content = content.replace(
        "from .celery import app as celery_app\n\n__all__ = ('celery_app',)",
        ""
    )
    
    # If file is empty, add a comment
    if not content.strip():
        content = "# This file is intentionally left blank.\n"
    
    init_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Removed Celery app from {name}/__init__.py[/green]")
    return True


def remove_celery_from_settings(name: str):
    """Remove Celery settings from settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False
    
    content = settings_path.read_text(encoding="utf-8")
    
    # Check if Celery is configured
    if "CELERY_BROKER_URL" not in content:
        print("[yellow]Warning: Celery not configured in settings.py. Skipping.[/yellow]")
        return True
    
    # Remove Celery settings block
    celery_pattern = r"\n# ── Celery \(Background Tasks\) ─.*?(?=\n# ──|\Z)"
    content = re.sub(celery_pattern, "", content, flags=re.DOTALL)
    
    # Remove Celery Beat schedule if present
    beat_pattern = r"\nCELERY_BEAT_SCHEDULE\s*=\s*\{[^}]*\}"
    content = re.sub(beat_pattern, "", content, flags=re.DOTALL)
    
    # Remove crontab import if present
    content = content.replace(
        "\ntry:\n    from celery.schedules import crontab\nexcept ImportError:\n    pass",
        ""
    )
    
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
    
    # Packages to remove
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
