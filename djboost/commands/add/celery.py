import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.celery import (
    get_project_name,
    generate_celery_files,
    update_settings_celery,
)
from djboost.generators.dependencies import freeze_requirements
from djboost.generators.safe_engine import (
    execute_plan,
    generate_add_plan,
    scan_enabled_features,
)


def add_celery_command(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="Preview changes without applying them."
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip conflict checks."
    ),
):
    """Add Celery configuration to an existing Django project."""
    check_virtual_environment()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🚀 Adding Celery to project: {name}[/bold green]\n")

    # Generate plan through safe engine
    plan = generate_add_plan("celery", dry_run=dry_run, project_name=name, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print("[yellow]⚠ Celery is already configured.[/yellow]")
        raise typer.Exit(0)

    # Execute plan (dry-run or real)
    record = execute_plan(plan, project_name=name)

    if dry_run:
        raise typer.Exit(0)

    # Apply the actual file changes (the safe engine handled packages + validation)
    print("\n[cyan]━━━ Applying Celery configuration ━━━[/cyan]")

    generate_celery_files(name)
    update_settings_celery(name)
    freeze_requirements()

    print()
    print("[bold green]✅ Celery added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your Redis credentials")
    print(f"  2. Start Celery worker: [bold]celery -A {name} worker -l info[/bold]")
    print(f"  3. Start Celery Beat: [bold]celery -A {name} beat -l info[/bold]")
