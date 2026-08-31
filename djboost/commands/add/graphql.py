import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.graphql import (
    add_graphql_settings, add_graphql_to_requirements,
    add_graphql_urls, generate_graphql_schema, get_project_name,
)
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_graphql_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add GraphQL API with Strawberry to an existing Django project."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🔮 Adding GraphQL to project: {name}[/bold green]\n")

    plan = generate_add_plan("graphql", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ GraphQL is already configured.[/yellow]")
        raise typer.Exit(0)

    def apply_graphql():
        generate_graphql_schema(name)
        add_graphql_urls(name)
        add_graphql_settings(name)
        add_graphql_to_requirements()

    record = execute_plan(plan, project_name=name, apply_fn=apply_graphql)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ GraphQL added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Run [bold]pip install -r requirements.txt[/bold]")
    print("  2. Access GraphiQL at [bold]http://localhost:8000/graphql/[/bold]")
    print(f"  3. Define your types in [bold]{name}/schema.py[/bold]")
