"""
generator.py — main orchestrator for djboost.

All logic is split into generators/ sub-modules.
This file only imports and wires them together.
"""

import subprocess
import sys
from pathlib import Path

from rich import print

from djboost.generators.dependencies import (
    ESSENTIAL_PACKAGES,
    add_to_requirements,
    install_dependencies,
)
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

    print()
    print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    print("[bold green]║           🚀 djboost — Creating Project                 ║[/bold green]")
    print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    print()

    print("[cyan]━━━ Step 1/6: Installing Django ━━━[/cyan]")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "Django", "-q"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[red]Failed to install Django:\n{result.stderr}[/red]")
        import typer

        raise typer.Exit(1)
    print("[green]   ✔ Django installed[/green]")
    print()

    print("[cyan]━━━ Step 2/6: Creating project structure ━━━[/cyan]")
    result = subprocess.run([sys.executable, "-m", "django", "startproject", name, "."], capture_output=True, text=True)
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

    print("[cyan]━━━ Step 4/6: Installing dependencies ━━━[/cyan]")
    install_dependencies()
    print()

    print("[cyan]━━━ Step 5/6: Generating config files ━━━[/cyan]")
    generate_env_file(secret_key, name)
    print("[green]   ✔ Created .env[/green]")
    add_to_requirements(ESSENTIAL_PACKAGES)
    print("[green]   ✔ Created requirements.txt[/green]")
    generate_gitignore()
    print("[green]   ✔ Created .gitignore[/green]")
    generate_pytest_ini(name)
    print("[green]   ✔ Created pytest.ini[/green]")
    generate_pre_commit_config()
    print("[green]   ✔ Created .pre-commit-config.yaml[/green]")
    print()

    print("[cyan]━━━ Step 6/6: Summary ━━━[/cyan]")
    print()
    print("[bold green]╔══════════════════════════════════════════════════════════╗[/bold green]")
    print("[bold green]║           ✅ Project Created Successfully!              ║[/bold green]")
    print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]")
    print()
    print("[cyan]📁 Project Structure:[/cyan]")
    print("   ./")
    print("   ├── manage.py        ✔ Django management")
    print(f"   ├── {name}/           ✔ Settings + URLs")
    print("   ├── apps/            ✔ Ready for apps")
    print("   ├── common/          ✔ Response helpers")
    print("   ├── media/           ✔ File uploads")
    print("   ├── static/          ✔ Static files")
    print("   ├── .env             ✔ Environment vars")
    print("   ├── .gitignore       ✔ Git ignore")
    print("   └── requirements.txt ✔ 13 packages")
    print()
    print("[cyan]🚀 Next steps:[/cyan]")
    print("   1. python manage.py migrate")
    print("   2. python manage.py runserver")
    print()
    print("[cyan]📌 Quick commands:[/cyan]")
    print("   djboost --help                 # Show all commands")
    print()
    print("[cyan]📱 Create:[/cyan]")
    print("   djboost startapp products      # Create an app")
    print("   djboost startauth              # Create auth system")
    print()
    print("[cyan]🔧 Add features:[/cyan]")
    print("   djboost add celery             # Background tasks")
    print("   djboost add docker             # Docker support")
    print("   djboost add api-docs swagger   # Swagger UI only")
    print("   djboost add api-docs redoc     # ReDoc only")
    print("   djboost add api-docs both      # Swagger + ReDoc")
    print("   djboost add postgres           # PostgreSQL database")
    print("   djboost add redis-cache        # Redis caching")
    print("   djboost add channels           # WebSocket support")
    print("   djboost add security           # Security headers")
    print("   djboost add sentry             # Error tracking")
    print("   djboost add graphql            # GraphQL API")
    print("   djboost add storage            # Cloud storage (S3)")
    print("   djboost add cicd github        # GitHub Actions CI/CD")
    print("   djboost add logging            # Structured logging")
    print("   djboost add monitoring         # OpenTelemetry")
    print()
    print("[cyan]📋 Management:[/cyan]")
    print("   djboost doctor                 # Check project health")
    print("   djboost features               # List available features")
    print("   djboost validate               # Validate project structure")
    print("   djboost info                   # Show project info")
    print()
