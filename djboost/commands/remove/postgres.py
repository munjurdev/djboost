import re
from pathlib import Path

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_postgres_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove PostgreSQL — revert to SQLite default."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing PostgreSQL...[/bold green]\n")

    plan = generate_remove_plan("postgres", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ PostgreSQL is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    # Revert DATABASES to SQLite
    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        # Replace postgresql engine with sqlite3
        content = content.replace(
            "django.db.backends.postgresql",
            "django.db.backends.sqlite3",
        )
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Reverted DATABASES to SQLite[/green]")

    # Remove from requirements.txt
    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "psycopg2" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed psycopg2-binary from requirements.txt[/green]")

    print()
    print("[bold green]✅ PostgreSQL removed — reverted to SQLite[/bold green]")
