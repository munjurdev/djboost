import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_add_plan
from djboost.generators.storage import (
    add_storage_to_requirements,
    get_project_name,
    update_env_storage,
    update_settings_storage,
)


def add_storage_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add S3-compatible cloud storage with django-storages."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]☁️  Adding Cloud Storage to project: {name}[/bold green]\n")

    plan = generate_add_plan("storage", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Cloud Storage is already configured.[/yellow]")
        raise typer.Exit(0)

    def apply_storage():
        update_settings_storage(name)
        update_env_storage(name)
        add_storage_to_requirements()

    record = execute_plan(plan, project_name=name, apply_fn=apply_storage)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ Cloud Storage added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Set AWS credentials in [bold].env[/bold]")
    print("  2. Run [bold]pip install -r requirements.txt[/bold]")
