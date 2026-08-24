import typer
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_monitoring_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove OpenTelemetry from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing OpenTelemetry...[/bold green]\n")

    plan = generate_remove_plan("monitoring", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ OpenTelemetry is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    settings_files = list(Path(".").glob("*/settings.py"))
    project_name = settings_files[0].parent.name if settings_files else None

    # Remove telemetry.py
    if project_name:
        telemetry_path = Path(f"{project_name}/telemetry.py")
        if telemetry_path.exists():
            telemetry_path.unlink()
            print(f"[green]✔ Removed {project_name}/telemetry.py[/green]")

    # Remove from wsgi.py
    if project_name:
        wsgi_path = Path(f"{project_name}/wsgi.py")
        if wsgi_path.exists():
            content = wsgi_path.read_text(encoding="utf-8")
            content = re.sub(r"from \w+\.telemetry import.*?\n", "", content)
            content = re.sub(r"init_telemetry\(\)\n", "", content)
            wsgi_path.write_text(content, encoding="utf-8")
            print(f"[green]✔ Removed telemetry init from {project_name}/wsgi.py[/green]")

    # Remove from settings.py
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        content = re.sub(r"\n# ── OpenTelemetry.*?(?=\n# ──|\Z)", "", content, flags=re.DOTALL)
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Removed OpenTelemetry settings from settings.py[/green]")

    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if "opentelemetry" not in l.lower()]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed OpenTelemetry packages from requirements.txt[/green]")

    print()
    print("[bold green]✅ OpenTelemetry removed successfully![/bold green]")
