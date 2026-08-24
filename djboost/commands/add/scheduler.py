import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_add_plan
from djboost.generators.scheduler import (
    add_scheduler_settings,
    add_scheduler_to_requirements,
    generate_scheduler_config,
    get_project_name,
)


def add_scheduler_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add APScheduler for lightweight in-process job scheduling."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]⏰ Adding APScheduler to project: {name}[/bold green]\n")

    plan = generate_add_plan("scheduler", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ APScheduler is already configured.[/yellow]")
        raise typer.Exit(0)

    # Check for conflict with celery-beat
    from djboost.generators.features import scan_enabled_features

    enabled = scan_enabled_features(name)
    if "celery-beat" in enabled and not force:
        print("[red]Error: Celery Beat is already installed. APScheduler conflicts with it.[/red]")
        print("[cyan]Use --force to override, or remove celery-beat first.[/cyan]")
        raise typer.Exit(1)

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying APScheduler ━━━[/cyan]")
    generate_scheduler_config(name)
    add_scheduler_settings(name)
    add_scheduler_to_requirements()

    print()
    print("[bold green]✅ APScheduler added successfully![/bold green]")
    print()
    print("[cyan]Usage:[/cyan]")
    print("  1. Register jobs in {}/scheduler.py".format(name))
    print("  2. Call start_scheduler() in your AppConfig.ready()")
    print("  3. Run [bold]python manage.py migrate[/bold] (for job store)")
