import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.celery import (
    generate_celery_files,
    get_project_name,
    update_settings_celery,
)
from djboost.generators.dependencies import add_to_requirements
from djboost.generators.safe_engine import (
    execute_plan,
    generate_add_plan,
    scan_enabled_features,
)


def add_celery_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add Celery configuration to an existing Django project."""
    check_virtual_environment()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🚀 Adding Celery to project: {name}[/bold green]\n")

    plan = generate_add_plan("celery", dry_run=dry_run, project_name=name, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print("[yellow]⚠ Celery is already configured.[/yellow]")
        raise typer.Exit(0)

    def apply_celery():
        generate_celery_files(name)
        update_settings_celery(name)
        add_to_requirements(["celery>=5.4,<6", "redis>=5.0,<6"])

    record = execute_plan(plan, project_name=name, apply_fn=apply_celery)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ Celery added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your Redis credentials")
    print(f"  2. Start Celery worker: [bold]celery -A {name} worker -l info[/bold]")
    print(f"  3. Start Celery Beat: [bold]celery -A {name} beat -l info[/bold]")
