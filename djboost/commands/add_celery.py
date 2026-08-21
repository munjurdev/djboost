import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.celery import (
    get_project_name,
    generate_celery_files,
    update_settings_celery,
)
from djboost.generators.dependencies import install_optional_packages, freeze_requirements


def add_celery_command():
    """Add Celery configuration to an existing Django project."""
    check_virtual_environment()
    
    name = get_project_name()
    if not name:
        raise typer.Exit(1)
    
    print(f"\n[bold green]🚀 Adding Celery to project: {name}[/bold green]\n")
    
    # Step 1: Install Celery packages
    install_optional_packages("celery")
    
    # Step 2: Generate Celery files
    print("[cyan]📝 Generating Celery files...[/cyan]")
    generate_celery_files(name)
    
    # Step 3: Update settings.py
    print("[cyan]⚙️  Updating settings.py...[/cyan]")
    update_settings_celery(name)
    
    # Step 4: Freeze requirements
    freeze_requirements()
    
    print()
    print("[bold green]✅ Celery added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your Redis credentials")
    print("  2. Start Celery worker: [bold]celery -A {} worker -l info[/bold]".format(name))
    print("  3. Start Celery Beat: [bold]celery -A {} beat -l info[/bold]".format(name))
