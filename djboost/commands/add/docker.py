import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.docker import (
    get_project_name,
    generate_dockerfile,
    generate_docker_compose_add,
    generate_dockerignore_add,
    add_docker_to_requirements,
)
from djboost.generators.safe_engine import (
    execute_plan,
    generate_add_plan,
    scan_enabled_features,
)


def add_docker_command(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="Preview changes without applying them."
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip conflict checks."
    ),
):
    """Add Docker configuration to an existing Django project."""
    check_virtual_environment()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🐳 Adding Docker to project: {name}[/bold green]\n")

    # Generate plan through safe engine
    plan = generate_add_plan("docker", dry_run=dry_run, project_name=name, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print("[yellow]⚠ Docker is already configured.[/yellow]")
        raise typer.Exit(0)

    # Execute plan (dry-run or real)
    record = execute_plan(plan, project_name=name)

    if dry_run:
        raise typer.Exit(0)

    # Apply the actual file changes
    print("\n[cyan]━━━ Applying Docker configuration ━━━[/cyan]")

    generate_dockerfile()
    generate_docker_compose_add(name)
    generate_dockerignore_add()
    add_docker_to_requirements()

    print()
    print("[bold green]✅ Docker added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your database credentials")
    print("  2. Run [bold]docker-compose up --build[/bold]")
    print("  3. Access Django at [bold]http://localhost:8000[/bold]")
    print()
    print("[cyan]Note:[/cyan] Services depend on which features you have installed.")
    print("  Run [bold]djboost add celery[/bold] before Docker to include Celery services.")
