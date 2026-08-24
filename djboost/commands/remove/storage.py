import typer
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_storage_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Cloud Storage from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing Cloud Storage...[/bold green]\n")

    plan = generate_remove_plan("storage", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ Cloud Storage is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        content = re.sub(r"\n# ── S3 / Cloud Storage.*?(?=\n# ──|\Z)", "", content, flags=re.DOTALL)
        content = re.sub(r"AWS_\w+\s*=.*?\n", "", content)
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Removed S3 storage config from settings.py[/green]")

    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "storages" not in l.lower() and "boto3" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed django-storages and boto3 from requirements.txt[/green]")

    print()
    print("[bold green]✅ Cloud Storage removed successfully![/bold green]")
