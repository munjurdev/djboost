import re
from pathlib import Path

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_redis_cache_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Redis Cache from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing Redis Cache...[/bold green]\n")

    plan = generate_remove_plan("redis-cache", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ Redis Cache is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        content = re.sub(r"\n# ── Redis Cache.*?(?=\n# ──|\Z)", "", content, flags=re.DOTALL)
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Removed Redis cache config from settings.py[/green]")

    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "django-redis" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed django-redis from requirements.txt[/green]")

    print()
    print("[bold green]✅ Redis Cache removed successfully![/bold green]")
