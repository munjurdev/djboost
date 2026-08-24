import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.monitoring import (
    add_monitoring_settings,
    add_monitoring_to_requirements,
    add_monitoring_to_wsgi,
    generate_telemetry,
    get_project_name,
)
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_monitoring_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add OpenTelemetry distributed tracing and metrics."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]📊 Adding OpenTelemetry to project: {name}[/bold green]\n")

    plan = generate_add_plan("monitoring", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ OpenTelemetry is already configured.[/yellow]")
        raise typer.Exit(0)

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying OpenTelemetry ━━━[/cyan]")
    generate_telemetry(name)
    add_monitoring_settings(name)
    add_monitoring_to_wsgi(name)
    add_monitoring_to_requirements()

    print()
    print("[bold green]✅ OpenTelemetry added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Set [bold]OTEL_EXPORTER_OTLP_ENDPOINT[/bold] in .env")
    print("  2. Ensure your OTEL collector is running")
    print("  3. Deploy and check your traces in Jaeger/Grafana")
