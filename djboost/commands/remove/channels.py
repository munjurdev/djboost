import typer
import re
from pathlib import Path
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_channels_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Django Channels from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing Django Channels...[/bold green]\n")

    plan = generate_remove_plan("channels", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ Django Channels is not currently configured.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    settings_files = list(Path(".").glob("*/settings.py"))
    project_name = settings_files[0].parent.name if settings_files else None

    # Remove asgi.py (only if it's the Channels version)
    if project_name:
        asgi_path = Path(f"{project_name}/asgi.py")
        if asgi_path.exists():
            content = asgi_path.read_text(encoding="utf-8")
            if "ProtocolTypeRouter" in content:
                asgi_path.unlink()
                print(f"[green]✔ Removed {project_name}/asgi.py[/green]")

    # Remove from settings.py
    if settings_files:
        settings_path = settings_files[0]
        content = settings_path.read_text(encoding="utf-8")
        # Remove daphne from INSTALLED_APPS
        content = content.replace("    'daphne',\n", "")
        # Remove Channels settings block
        content = re.sub(r"\n# ── Django Channels.*?(?=\n# ──|\Z)", "", content, flags=re.DOTALL)
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Removed Channels config from settings.py[/green]")

    req_path = Path("requirements.txt")
    if req_path.exists():
        content = req_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if not any(p in l.lower() for p in ["daphne", "channels"])]
        req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("[green]✔ Removed channels packages from requirements.txt[/green]")

    print()
    print("[bold green]✅ Django Channels removed successfully![/bold green]")
