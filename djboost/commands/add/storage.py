import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.storage import (
    get_project_name,
    update_settings_storage,
    update_env_storage,
    add_storage_to_requirements,
)
from djboost.generators.safe_engine import execute_plan, generate_add_plan


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

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying Cloud Storage configuration ━━━[/cyan]")
    update_settings_storage(name)
    update_env_storage(name)
    add_storage_to_requirements()

    print()
    print("[bold green]✅ Cloud Storage added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Set AWS credentials in [bold].env[/bold]")
    print("  2. Run [bold]pip install -r requirements.txt[/bold]")
