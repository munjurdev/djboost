"""
generator.py — main orchestrator for djboost.

All logic is split into generators/ sub-modules.
This file only imports and wires them together.
"""

import subprocess
import sys
from pathlib import Path

from rich import print

from djboost.generators.dependencies import freeze_requirements, install_dependencies
from djboost.generators.env import generate_env_file
from djboost.generators.project_files import (
    create_common_files,
    create_directories,
    create_utils_file,
    update_urls_file,
)
from djboost.generators.quality import (
    generate_gitignore,
    generate_pre_commit_config,
    generate_pytest_ini,
)
from djboost.generators.settings import update_settings_file

# ── Re-export for backward compatibility (commands import from here) ───────────
from djboost.generators.validators import check_virtual_environment, validate_name


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

    # Beautiful header
    print()
    print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    print("[bold green]║           🚀 djboost — Creating Project                 ║[/bold green]")
    print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    print()

    # Step 1: Install Django
    print("[cyan]━━━ Step 1/6: Installing Django ━━━[/cyan]")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "Django", "-q"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[red]Failed to install Django:\n{result.stderr}[/red]")
        import typer

        raise typer.Exit(1)
    print("[green]   ✔ Django installed[/green]")
    print()

    # Step 2: Create project
    print("[cyan]━━━ Step 2/6: Creating project structure ━━━[/cyan]")
    result = subprocess.run(
        [sys.executable, "-m", "django", "startproject", name, "."],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[red]Failed to scaffold project:\n{result.stderr}[/red]")
        import typer

        raise typer.Exit(1)
    print(f"[green]   ✔ Created {name}/ directory[/green]")
    print("[green]   ✔ Created manage.py[/green]")
    print("[green]   ✔ Created settings.py[/green]")
    print("[green]   ✔ Created urls.py[/green]")
    print("[green]   ✔ Created wsgi.py + asgi.py[/green]")
    print()

    # Step 3: Configure settings
    print("[cyan]━━━ Step 3/6: Configuring settings ━━━[/cyan]")
    secret_key = update_settings_file(f"{name}/settings.py", name)
    print("[green]   ✔ Added DRF + JWT + CORS + Security[/green]")
    create_utils_file(name)
    print("[green]   ✔ Created exception handler[/green]")
    update_urls_file(name)
    print("[green]   ✔ Created root URLs[/green]")
    create_directories()
    print("[green]   ✔ Created apps/ directory[/green]")
    print("[green]   ✔ Created media/ directory[/green]")
    print("[green]   ✔ Created static/ directory[/green]")
    create_common_files()
    print("[green]   ✔ Created common/ package[/green]")
    print("[green]     ├── responses.py[/green]")
    print("[green]     ├── pagination.py[/green]")
    print("[green]     └── exceptions.py[/green]")
    print()

    # Step 4: Install dependencies
    print("[cyan]━━━ Step 4/6: Installing dependencies ━━━[/cyan]")
    install_dependencies()
    print()

    # Step 5: Generate config files
    print("[cyan]━━━ Step 5/6: Generating config files ━━━[/cyan]")
    generate_env_file(secret_key, name)
    print("[green]   ✔ Created .env[/green]")
    freeze_requirements()
    print("[green]   ✔ Created requirements.txt[/green]")
    generate_gitignore()
    print("[green]   ✔ Created .gitignore[/green]")
    generate_pytest_ini(name)
    print("[green]   ✔ Created pytest.ini[/green]")
    generate_pre_commit_config()
    print("[green]   ✔ Created .pre-commit-config.yaml[/green]")
    print()

    # Step 6: Summary
    print("[cyan]━━━ Step 6/6: Summary ━━━[/cyan]")
    print()
    print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    print("[bold green]║           ✅ Project Created Successfully!              ║[/bold green]")
    print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    print()
    print("[cyan]📁 Project Structure:[/cyan]")
    print(f"   {name}/")
    print("   ├── settings.py      ✔ Configured")
    print("   ├── urls.py          ✔ Ready")
    print("   ├── utils.py         ✔ Exception handler")
    print("   ├── apps/            ✔ Ready for apps")
    print("   ├── common/          ✔ Response helpers")
    print("   ├── media/           ✔ File uploads")
    print("   ├── static/          ✔ Static files")
    print("   ├── .env             ✔ Environment vars")
    print("   ├── .gitignore       ✔ Git ignore")
    print("   └── requirements.txt ✔ 13 packages")
    print()
    print("[cyan]🚀 Next steps:[/cyan]")
    print(f"   1. cd {name}")
    print("   2. python manage.py migrate")
    print("   3. python manage.py runserver")
    print()
    print("[cyan]📌 Optional commands:[/cyan]")
    print("   djboost startapp products      # Create an app")
    print("   djboost startauth              # Create auth system")
    print("   djboost add celery             # Add background tasks")
    print("   djboost add docker             # Add Docker")
    print("   djboost add api-docs both      # Add Swagger + ReDoc")
    print("   djboost doctor                 # Check project health")
    print()
