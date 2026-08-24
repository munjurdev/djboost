import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_add_plan
from djboost.generators.security import (
    add_security_to_requirements,
    get_project_name,
    update_settings_security,
)


def add_security_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add security headers (CSP, HSTS) to an existing Django project."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🔒 Adding Security Headers to project: {name}[/bold green]\n")

    plan = generate_add_plan("security", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Security Headers are already configured.[/yellow]")
        raise typer.Exit(0)

    record = execute_plan(plan, project_name=name)
    if dry_run:
        raise typer.Exit(0)

    print("\n[cyan]━━━ Applying Security Headers ━━━[/cyan]")
    update_settings_security(name)
    add_security_to_requirements()

    print()
    print("[bold green]✅ Security Headers added successfully![/bold green]")
    print()
    print("[cyan]What was added:[/cyan]")
    print("  • Content Security Policy (CSP)")
    print("  • HSTS (enable via SECURE_HSTS_SECONDS in .env)")
    print("  • SSL redirect, secure cookies (enable in production)")
