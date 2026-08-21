import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.celery_remove import (
    get_project_name,
    remove_celery_files,
    remove_celery_from_init,
    remove_celery_from_settings,
    remove_celery_from_requirements,
)
from djboost.generators.dependencies import uninstall_optional_packages


def remove_celery_command():
    """Remove Celery configuration from an existing Django project."""
    check_virtual_environment()
    
    name = get_project_name()
    if not name:
        raise typer.Exit(1)
    
    print(f"\n[bold red]🗑️  Removing Celery from project: {name}[/bold red]\n")
    
    # Step 1: Uninstall Celery packages
    uninstall_optional_packages("celery")
    
    # Step 2: Remove Celery files
    print("[cyan]📝 Removing Celery files...[/cyan]")
    remove_celery_files(name)
    
    # Step 3: Remove from __init__.py
    print("[cyan]📝 Updating __init__.py...[/cyan]")
    remove_celery_from_init(name)
    
    # Step 4: Remove from settings.py
    print("[cyan]⚙️  Updating settings.py...[/cyan]")
    remove_celery_from_settings(name)
    
    # Step 5: Remove from requirements.txt
    print("[cyan]📦 Updating requirements.txt...[/cyan]")
    remove_celery_from_requirements()
    
    print()
    print("[bold green]✅ Celery removed successfully![/bold green]")
    print()
    print("[cyan]Removed:[/cyan]")
    print("  • celery + redis packages uninstalled")
    print("  • celery.py, tasks.py deleted")
    print("  • Celery config removed from settings.py")
    print("  • Celery removed from requirements.txt")
