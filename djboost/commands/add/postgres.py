import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.postgres import add_postgres_to_requirements, get_project_name, update_env_postgres, update_settings_postgres
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_postgres_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add PostgreSQL database backend to an existing Django project."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🐘 Adding PostgreSQL to project: {name}[/bold green]\n")

    plan = generate_add_plan("postgres", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ PostgreSQL is already configured.[/yellow]")
        raise typer.Exit(0)

    def apply_postgres():
        update_settings_postgres(name)
        update_env_postgres(name)
        add_postgres_to_requirements()

    record = execute_plan(plan, project_name=name, apply_fn=apply_postgres)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ PostgreSQL added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your PostgreSQL credentials")
    print("  2. Run [bold]python manage.py migrate[/bold]")
