"""djboost remove docker — remove Docker configuration."""

from pathlib import Path

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_docker_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Docker configuration from the project."""
    check_virtual_environment()

    print("\n[bold green]🔄 Removing Docker...[/bold green]\n")

    # Generate plan through safe engine
    plan = generate_remove_plan("docker", dry_run=dry_run, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return

    if plan.idempotent:
        print("[yellow]⚠ Docker is not currently configured.[/yellow]")
        return

    # Execute plan (dry-run or real)
    record = execute_plan(plan)

    if dry_run:
        return

    # Apply the actual file changes
    removed = []

    # 1. Remove Dockerfile
    if Path("Dockerfile").exists():
        Path("Dockerfile").unlink()
        removed.append("Dockerfile")
        print("[green]✔ Removed Dockerfile[/green]")
    else:
        print("[yellow]⚠ Dockerfile not found, skipping[/yellow]")

    # 2. Remove docker-compose.yml
    if Path("docker-compose.yml").exists():
        Path("docker-compose.yml").unlink()
        removed.append("docker-compose.yml")
        print("[green]✔ Removed docker-compose.yml[/green]")
    else:
        print("[yellow]⚠ docker-compose.yml not found, skipping[/yellow]")

    # 3. Remove .dockerignore
    if Path(".dockerignore").exists():
        Path(".dockerignore").unlink()
        removed.append(".dockerignore")
        print("[green]✔ Removed .dockerignore[/green]")
    else:
        print("[yellow]⚠ .dockerignore not found, skipping[/yellow]")

    # 4. Remove flower from requirements.txt
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        content = requirements_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = [line for line in lines if "flower" not in line.lower() and "gunicorn" not in line.lower()]
        if len(new_lines) < len(lines):
            requirements_path.write_text("\n".join(new_lines), encoding="utf-8")
            print("[green]✔ Removed flower/gunicorn from requirements.txt[/green]")

    print()
    if removed:
        print(f"[bold green]✅ Docker removed successfully![/bold green]")
        print(f"  Removed: {', '.join(removed)}")
    else:
        print("[yellow]⚠ No Docker files found to remove.[/yellow]")
    print()
