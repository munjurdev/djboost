import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_add_plan
from djboost.generators.sentry import (
    add_sentry_to_requirements,
    add_sentry_to_settings,
    get_project_name,
)


def add_sentry_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add Sentry error tracking to an existing Django project."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🐛 Adding Sentry to project: {name}[/bold green]\n")

    plan = generate_add_plan("sentry", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Sentry is already configured.[/yellow]")
        raise typer.Exit(0)

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying Sentry configuration ━━━[/cyan]")
    add_sentry_to_settings(name)
    add_sentry_to_requirements()

    print()
    print("[bold green]✅ Sentry added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Set [bold]SENTRY_DSN[/bold] in your .env file")
    print("  2. Run [bold]pip install -r requirements.txt[/bold]")
    print("  3. Deploy and check your Sentry dashboard")
