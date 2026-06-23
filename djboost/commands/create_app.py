import re
import sys
import subprocess
from pathlib import Path
import typer
from rich import print
from djboost.generator import check_virtual_environment, validate_name


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

    if "include" not in content:
        content = re.sub(r"(from django\.urls import.*?path)", r"\1, include", content)

    if "urlpatterns = [" in content:
        content = content.replace(
            "urlpatterns = [",
            f"urlpatterns = [\n    path('api/{app_name}/', include('apps.{app_name}.urls')),"
        )
        urls_path.write_text(content, encoding="utf-8")
        print(f"[green]✔ Mapped /api/{app_name}/ in {project_name}/urls.py[/green]")
    else:
        print("[yellow]Warning: Could not find urlpatterns in urls.py[/yellow]")


def create_app_urls(app_name: str):
    urls_path = Path("apps") / app_name / "urls.py"
    content = f"""from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    # path('', views.MyView.as_view(), name='my-view'),
]
"""
    urls_path.write_text(content, encoding="utf-8")


def create_app_command(name: str = typer.Argument(..., help="The name of the Django app to create")):
    check_virtual_environment()
    validate_name(name, "app name")

    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Run this command from your Django project root.[/red]")
        raise typer.Exit(1)

    app_path = Path("apps") / name
    if app_path.exists():
        print(f"[red]Error: App '{name}' already exists at apps/{name}.[/red]")
        raise typer.Exit(1)

    Path("apps").mkdir(exist_ok=True)

    print(f"[cyan]Creating app '{name}'...[/cyan]")
    result = subprocess.run(
        [sys.executable, "manage.py", "startapp", name, f"apps/{name}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[red]Error creating app:\n{result.stderr}[/red]")
        raise typer.Exit(1)

    (Path(f"apps/{name}") / "__init__.py").touch()

    # Fix apps.py name
    apps_py_path = Path(f"apps/{name}/apps.py")
    if apps_py_path.exists():
        apps_content = apps_py_path.read_text(encoding="utf-8")
        apps_content = re.sub(rf"name\s*=\s*['\"]{name}['\"]", f"name = 'apps.{name}'", apps_content)
        apps_py_path.write_text(apps_content, encoding="utf-8")

    try:
        project_name = get_project_name()
        update_settings(project_name, name)
        update_urls(project_name, name)
        create_app_urls(name)
        print(f"[bold green]✅ App '{name}' created and configured successfully![/bold green]")
    except Exception as e:
        print(f"[red]Error during auto-configuration: {str(e)}[/red]")
