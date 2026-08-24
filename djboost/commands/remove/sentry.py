import typer
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_sentry_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Sentry from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing Sentry...[/bold green]\n")

    plan = generate_remove_plan("sentry", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ Sentry is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    # Remove Sentry config from settings.py
    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        content = re.sub(r"\n# ── Sentry.*?(?=\n# ──|\Z)", "", content, flags=re.DOTALL)
        content = re.sub(r"import sentry_sdk.*?\n", "", content)
        content = re.sub(r"from sentry_sdk.*?\n", "", content)
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Removed Sentry config from settings.py[/green]")

    # Remove from requirements.txt
    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "sentry" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed sentry-sdk from requirements.txt[/green]")

    print()
    print("[bold green]✅ Sentry removed successfully![/bold green]")
