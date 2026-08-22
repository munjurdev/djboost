import re
import sys
import subprocess
from pathlib import Path
import typer
from rich import print
from djboost.generator import check_virtual_environment, validate_name
from djboost.generators.app_structure import generate_standard_app


def get_project_name():
    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in the project root?[/red]")
        raise typer.Exit(1)

    content = Path("manage.py").read_text(encoding="utf-8")
    match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^.]+)\.settings['\"]", content)
    if match:
        return match.group(1)

    print("[red]Error: Could not determine project name from manage.py[/red]")
    raise typer.Exit(1)


def update_settings(project_name: str, app_name: str):
    settings_path = Path(project_name) / "settings.py"
    if not settings_path.exists():
        print(f"[yellow]Warning: Could not find settings.py at {settings_path}. Skipping.[/yellow]")
        return

    content = settings_path.read_text(encoding="utf-8")
    app_string = f"'apps.{app_name}',"

    if app_string in content or f'"apps.{app_name}",' in content:
        print(f"[yellow]App '{app_name}' is already in INSTALLED_APPS[/yellow]")
        return

    if "INSTALLED_APPS = [" in content:
        content = re.sub(
            r"(INSTALLED_APPS\s*=\s*\[.*?)(\n?\])",
            rf"\1\n    {app_string}\2",
            content,
            flags=re.DOTALL
        )
        settings_path.write_text(content, encoding="utf-8")
        print(f"[green]✔ Added '{app_string}' to INSTALLED_APPS[/green]")
    else:
        print("[yellow]Warning: Could not find INSTALLED_APPS in settings.py[/yellow]")


def update_urls(project_name: str, app_name: str):
    urls_path = Path(project_name) / "urls.py"
    if not urls_path.exists():
        print(f"[yellow]Warning: Could not find urls.py at {urls_path}. Skipping.[/yellow]")
        return

    content = urls_path.read_text(encoding="utf-8")

    if f"apps.{app_name}.urls" in content:
        print(f"[yellow]App '{app_name}' is already mapped in urls.py[/yellow]")
        return

    # Ensure 'include' is imported
    if "include" not in content:
        content = content.replace(
            "from django.urls import path",
            "from django.urls import path, include"
        )

    if "urlpatterns = [" in content:
        content = content.replace(
            "urlpatterns = [",
            f"urlpatterns = [\n    path('api/{app_name}/', include('apps.{app_name}.urls')),"
        )
        urls_path.write_text(content, encoding="utf-8")
        print(f"[green]✔ Mapped /api/{app_name}/ in {project_name}/urls.py[/green]")
    else:
        print("[yellow]Warning: Could not find urlpatterns in urls.py[/yellow]")


def create_app_command(name: str = typer.Argument(..., help="The name of the Django app to create")):
    check_virtual_environment()
    validate_name(name, "app name")

    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Run this command from your Django project root.[/red]")
        raise typer.Exit(1)

    # Check if project was created by djboost
    if not Path("apps").exists() or not Path("common").exists():
        print("[yellow]Warning: This project was not created by djboost.[/yellow]")
        print("[yellow]Some features may not work correctly.[/yellow]")
        print("[cyan]Recommended: Run 'djboost create project' first for best results.[/cyan]")
        print()

    app_path = Path("apps") / name
    if app_path.exists():
        print(f"[red]Error: App '{name}' already exists at apps/{name}.[/red]")
        raise typer.Exit(1)

    Path("apps").mkdir(exist_ok=True)

    # Generate standard app structure
    generate_standard_app(name)

    # Update project settings and URLs
    try:
        project_name = get_project_name()
        update_settings(project_name, name)
        update_urls(project_name, name)
        
        print()
        print("[bold green]✅ Standard app created successfully![/bold green]")
        print()
        print("[cyan]Structure:[/cyan]")
        print(f"  apps/{name}/")
        print(f"    ├── views/           ← Multiple view files")
        print(f"    ├── serializers/     ← Multiple serializer files")
        print(f"    ├── service/         ← Business logic")
        print(f"    ├── permissions.py   ← Custom permissions")
        print(f"    ├── tasks.py         ← Celery tasks")
        print(f"    ├── models.py        ← Database models")
        print(f"    ├── admin.py         ← Admin config")
        print(f"    ├── urls.py          ← URL patterns")
        print(f"    ├── apps.py          ← App config")
        print(f"    └── tests.py         ← Tests")
        print()
        print("[cyan]Next steps:[/cyan]")
        print(f"  1. Run [bold]python manage.py makemigrations {name}[/bold]")
        print("  2. Run [bold]python manage.py migrate[/bold]")
        print("  3. Run [bold]python manage.py runserver[/bold]")
    except Exception as e:
        print(f"[red]Error during auto-configuration: {str(e)}[/red]")
