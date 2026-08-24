import typer
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_security_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Security Headers from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing Security Headers...[/bold green]\n")

    plan = generate_remove_plan("security", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ Security Headers are not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        # Remove CSP middleware
        content = content.replace("    'csp.middleware.CSPMiddleware',\n", "")
        # Remove security settings
        content = re.sub(r"\n# ── Security Headers.*?(?=\n# ──|\Z)", "", content, flags=re.DOTALL)
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Removed security headers from settings.py[/green]")

    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "django-csp" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed django-csp from requirements.txt[/green]")

    print()
    print("[bold green]✅ Security Headers removed successfully![/bold green]")
