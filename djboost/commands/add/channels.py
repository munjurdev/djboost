import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.channels_gen import (
    get_project_name,
    generate_asgi_file,
    update_settings_channels,
    add_channels_to_requirements,
)
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_channels_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add Django Channels for WebSocket and async protocol support."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]⚡ Adding Django Channels to project: {name}[/bold green]\n")

    plan = generate_add_plan("channels", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Django Channels is already configured.[/yellow]")
        raise typer.Exit(0)

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying Django Channels ━━━[/cyan]")
    generate_asgi_file(name)
    update_settings_channels(name)
    add_channels_to_requirements()

    print()
    print("[bold green]✅ Django Channels added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Ensure Redis is running (channels-redis requires it)")
    print("  2. Run [bold]pip install -r requirements.txt[/bold]")
    print("  3. Add WebSocket consumers and routes in {}/asgi.py".format(name))
