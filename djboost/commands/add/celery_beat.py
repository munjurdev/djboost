import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.celery import add_crontab_import, generate_celery_beat_config, get_project_name
from djboost.generators.safe_engine import execute_plan, generate_add_plan, scan_enabled_features


def add_celery_beat_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add Celery Beat configuration to an existing Django project."""
    check_virtual_environment()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🚀 Adding Celery Beat to project: {name}[/bold green]\n")

    enabled = scan_enabled_features(name)
    if "celery" not in enabled:
        print("[red]Error: Celery is not installed. Run 'djboost add celery' first.[/red]")
        raise typer.Exit(1)

    plan = generate_add_plan("celery-beat", dry_run=dry_run, project_name=name, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print("[yellow]⚠ Celery Beat is already configured.[/yellow]")
        raise typer.Exit(0)

    def apply_celery_beat():
        add_crontab_import(name)
        generate_celery_beat_config(name)

    record = execute_plan(plan, project_name=name, apply_fn=apply_celery_beat)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ Celery Beat added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print(f"  1. Edit [bold]{name}/settings.py[/bold] to add your periodic tasks")
    print(f"  2. Start Celery Beat: [bold]celery -A {name} beat -l info[/bold]")
