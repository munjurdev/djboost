import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.redis_cache import add_redis_cache_to_requirements, get_project_name, update_env_redis_cache, update_settings_redis_cache
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_redis_cache_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add Redis-backed caching and session storage."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]🔴 Adding Redis Cache to project: {name}[/bold green]\n")

    plan = generate_add_plan("redis-cache", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Redis Cache is already configured.[/yellow]")
        raise typer.Exit(0)

    def apply_redis_cache():
        update_settings_redis_cache(name)
        update_env_redis_cache(name)
        add_redis_cache_to_requirements()

    record = execute_plan(plan, project_name=name, apply_fn=apply_redis_cache)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ Redis Cache added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Ensure Redis is running (docker run -d -p 6379:6379 redis:7-alpine)")
    print("  2. Run [bold]pip install -r requirements.txt[/bold]")
