"""djboost features — list available features and their status."""
from pathlib import Path
from rich import print
from rich.table import Table
from rich.console import Console

from djboost.generators.features import list_features, scan_enabled_features


def features_command():
    """List all available DJBoost features and their current status."""
    console = Console()

    print("\n[bold green]📦 djboost features — Available Features[/bold green]\n")

    # Detect project name
    project_name = None
    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        project_name = settings_files[0].parent.name

    # Scan enabled features
    enabled = scan_enabled_features(project_name) if Path("manage.py").exists() else set()

    # Build table
    table = Table(title="Features")
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Feature", style="cyan")
    table.add_column("Description")
    table.add_column("Dependencies")

    for feat in list_features():
        if feat.name in enabled:
            status = "[green]✅ Enabled[/green]"
        else:
            status = "[dim]○ Available[/dim]"

        deps = ", ".join(feat.requires) if feat.requires else "—"
        table.add_row(status, feat.display_name, feat.description, deps)

    console.print(table)

    print()
    print("[cyan]Usage:[/cyan]")
    print("  djboost add <feature>       — Enable a feature")
    print("  djboost remove <feature>    — Disable a feature")
    print("  djboost add <feature> --dry-run — Preview changes")
    print()
