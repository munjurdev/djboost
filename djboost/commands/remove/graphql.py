import re
from pathlib import Path

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_graphql_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove GraphQL from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing GraphQL...[/bold green]\n")

    plan = generate_remove_plan("graphql", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ GraphQL is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    # Remove schema.py
    settings_files = list(Path(".").glob("*/settings.py"))
    project_name = settings_files[0].parent.name if settings_files else None
    if project_name:
        schema_path = Path(f"{project_name}/schema.py")
        if schema_path.exists():
            schema_path.unlink()
            print(f"[green]✔ Removed {project_name}/schema.py[/green]")

    # Remove GraphQL URLs
    if settings_files:
        urls_path = Path(f"{project_name}/urls.py")
        if urls_path.exists():
            content = urls_path.read_text(encoding="utf-8")
            content = re.sub(r"from strawberry\.django.*?\n", "", content)
            content = re.sub(r"\s*path\(['\"]graphql/['\"].*?\n", "", content)
            urls_path.write_text(content, encoding="utf-8")
            print(f"[green]✔ Removed GraphQL URL from {project_name}/urls.py[/green]")

    # Remove from requirements.txt
    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "strawberry" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed strawberry-graphql from requirements.txt[/green]")

    print()
    print("[bold green]✅ GraphQL removed successfully![/bold green]")
