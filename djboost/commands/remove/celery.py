import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.celery import (
    get_project_name,
    remove_celery_files,
    remove_celery_from_init,
    remove_celery_from_settings,
    remove_celery_from_requirements,
)
from djboost.generators.dependencies import uninstall_optional_packages
from djboost.generators.safe_engine import (
    execute_plan,
    generate_remove_plan,
    scan_enabled_features,
)


def remove_celery_command(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="Preview changes without applying them."
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip reverse dependency checks."
    ),
):
    """Remove Celery configuration from an existing Django project."""
    check_virtual_environment()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold red]🗑️  Removing Celery from project: {name}[/bold red]\n")

    # Generate plan through safe engine
    plan = generate_remove_plan("celery", dry_run=dry_run, project_name=name, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print("[yellow]⚠ Celery is not currently enabled.[/yellow]")
        raise typer.Exit(0)

    # Execute plan (dry-run or real)
    record = execute_plan(plan, project_name=name)

    if dry_run:
        raise typer.Exit(0)

    # Apply the actual file changes
    print("\n[cyan]━━━ Removing Celery configuration ━━━[/cyan]")

    uninstall_optional_packages("celery")
    remove_celery_files(name)
    remove_celery_from_init(name)
    remove_celery_from_settings(name)
    remove_celery_from_requirements()

    print()
    print("[bold green]✅ Celery removed successfully![/bold green]")
    print()
    print("[cyan]Removed:[/cyan]")
    print("  • celery + redis packages uninstalled")
    print("  • celery.py, tasks.py deleted")
    print("  • Celery config removed from settings.py")
    print("  • Celery removed from requirements.txt")
