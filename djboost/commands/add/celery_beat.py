import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.celery import (
    get_project_name,
    generate_celery_beat_config,
    add_crontab_import,
)


def add_celery_beat_command():
    """Add Celery Beat configuration to an existing Django project."""
    check_virtual_environment()
    
    name = get_project_name()
    if not name:
        raise typer.Exit(1)
    
    print(f"\n[bold green]🚀 Adding Celery Beat to project: {name}[/bold green]\n")
    
    # Step 1: Add crontab import
    print("[cyan]📝 Adding crontab import...[/cyan]")
    add_crontab_import(name)
    
    # Step 2: Generate Celery Beat config
    print("[cyan]⚙️  Generating Celery Beat schedule...[/cyan]")
    generate_celery_beat_config(name)
    
    print()
    print("[bold green]✅ Celery Beat added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Edit [bold]{}[/bold] to add your periodic tasks".format(f"{name}/settings.py"))
    print("  2. Start Celery Beat: [bold]celery -A {} beat -l info[/bold]".format(name))
    print()
    print("[cyan]Example schedule:[/cyan]")
    print('  "daily-cleanup": {')
    print(f'      "task": "{name}.tasks.cleanup_task",')
    print('      "schedule": crontab(hour=0, minute=0),')
    print('  },')
