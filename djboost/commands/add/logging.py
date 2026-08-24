import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.logging_config import (
    get_project_name,
    generate_logging_config,
    add_logging_settings,
    add_logging_to_requirements,
)
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_logging_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add structured JSON logging with structlog."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]📋 Adding Structured Logging to project: {name}[/bold green]\n")

    plan = generate_add_plan("logging", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Structured Logging is already configured.[/yellow]")
        raise typer.Exit(0)

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying Structured Logging ━━━[/cyan]")
    generate_logging_config(name)
    add_logging_settings(name)
    add_logging_to_requirements()

    print()
    print("[bold green]✅ Structured Logging added successfully![/bold green]")
    print()
    print("[cyan]Usage:[/cyan]")
    print('  import structlog')
    print('  logger = structlog.get_logger()')
    print('  logger.info("user_logged_in", user_id=user.id)')
    print()
    print("[cyan]Config via .env:[/cyan]")
    print("  LOG_LEVEL=INFO")
    print("  LOG_FORMAT=json  # or 'console'")
