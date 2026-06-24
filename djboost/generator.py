"""
generator.py — main orchestrator for djboost.

All logic is split into generators/ sub-modules.
This file only imports and wires them together.
"""
import sys
import subprocess
from pathlib import Path
from rich import print

# ── Re-export for backward compatibility (commands import from here) ───────────
from djboost.generators.validators import check_virtual_environment, validate_name
from djboost.generators.settings import update_settings_file
from djboost.generators.dependencies import install_dependencies, freeze_requirements
from djboost.generators.env import generate_env_file
from djboost.generators.docker import generate_docker_files
from djboost.generators.project_files import (
    create_directories,
    create_utils_file,
    create_celery_file,
    create_tasks_file,
    update_init_file,
    update_urls_file,
)
from djboost.generators.quality import (
    generate_gitignore,
    generate_pytest_ini,
    generate_pre_commit_config,
)
from djboost.generators.cicd import generate_github_actions, generate_gitlab_ci


def create_project(name: str):
    """Create a full production-ready Django project."""
    check_virtual_environment()
    validate_name(name, "project name")

    if Path(name).exists():
        print(f"[red]Error: Directory '{name}' already exists. Choose a different name.[/red]")
        import typer
        raise typer.Exit(1)

    if Path("manage.py").exists():
        print("[red]Error: manage.py already exists. Run this in an empty folder.[/red]")
        import typer
        raise typer.Exit(1)

    print(f"\n[bold green]🚀 Creating Django project: {name}[/bold green]\n")

    # ── Step 1: Install Django & scaffold ────────────────────────────────────
    print("[cyan]📦 Installing Django...[/cyan]")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "Django", "-q"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[red]Failed to install Django:\n{result.stderr}[/red]")
        import typer
        raise typer.Exit(1)

    result = subprocess.run(
        [sys.executable, "-m", "django", "startproject", name, "."],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[red]Failed to scaffold project:\n{result.stderr}[/red]")
        import typer
        raise typer.Exit(1)

    # ── Step 2: Patch settings & project files ───────────────────────────────
    print("[cyan]⚙️  Configuring settings...[/cyan]")
    secret_key = update_settings_file(f"{name}/settings.py", name)
    create_utils_file(name)
    create_celery_file(name)
    create_tasks_file(name)
    update_init_file(name)
    update_urls_file(name)
    create_directories()

    # ── Step 3: Install all dependencies ─────────────────────────────────────
    install_dependencies()

    # ── Step 4: Generate config files ────────────────────────────────────────
    print("[cyan]📝 Generating config files...[/cyan]")
    generate_env_file(secret_key, name)
    freeze_requirements()
    generate_docker_files(name)
    generate_gitignore()
    generate_pytest_ini(name)
    generate_pre_commit_config()

    # ── Done ─────────────────────────────────────────────────────────────────
    print()
    print(f"[bold green]✅ Project '{name}' created successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your DB credentials")
    print("  2. Run [bold]git init[/bold]")
    print("  3. Run [bold]python manage.py migrate[/bold]")
    print("  4. Run [bold]python manage.py runserver[/bold]")
