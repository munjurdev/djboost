import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.api_docs import (
    add_spectacular_settings,
    add_spectacular_to_installed_apps,
    add_spectacular_to_requirements,
    generate_api_docs_urls,
    get_project_name,
)
from djboost.generators.safe_engine import (
    execute_plan,
    generate_add_plan,
    scan_enabled_features,
)


def add_api_docs_command(
    provider: str = typer.Argument("swagger", help="API documentation provider (swagger, redoc, or both)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add API documentation (Swagger/ReDoc) to an existing Django project."""
    check_virtual_environment()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    provider = provider.lower()
    if provider not in ["swagger", "redoc", "both"]:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported: swagger, redoc, both.[/red]")
        raise typer.Exit(1)

    print(f"\n[bold green]📚 Adding API Documentation to project: {name}[/bold green]\n")

    # Generate plan through safe engine
    plan = generate_add_plan("api-docs", dry_run=dry_run, project_name=name, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print("[yellow]⚠ API Documentation is already configured.[/yellow]")
        raise typer.Exit(0)

    # Execute plan (dry-run or real)
    record = execute_plan(plan, project_name=name)

    if dry_run:
        raise typer.Exit(0)

    # Apply the actual file changes
    print("\n[cyan]━━━ Applying API Documentation configuration ━━━[/cyan]")

    add_spectacular_to_installed_apps(name)
    add_spectacular_settings(name)
    generate_api_docs_urls(name)
    add_spectacular_to_requirements()

    print()
    print("[bold green]✅ API Documentation added successfully![/bold green]")
    print()

    if provider in ["swagger", "both"]:
        print("[cyan]Swagger UI:[/cyan]")
        print("  [bold]http://localhost:8000/api/schema/swagger-ui/[/bold]")

    if provider in ["redoc", "both"]:
        print("[cyan]ReDoc:[/cyan]")
        print("  [bold]http://localhost:8000/api/schema/redoc/[/bold]")

    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Run [bold]pip install -r requirements.txt[/bold]")
    print("  2. Run [bold]python manage.py runserver[/bold]")
    print("  3. Access API docs at the URLs above")
