import shutil
from pathlib import Path

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_kubernetes_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove Kubernetes manifests from the project."""
    check_virtual_environment()
    print("\n[bold green]🔄 Removing Kubernetes manifests...[/bold green]\n")

    plan = generate_remove_plan("kubernetes", dry_run=dry_run, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        return
    if plan.idempotent:
        print("[yellow]⚠ Kubernetes manifests are not present.[/yellow]")
        return

    record = execute_plan(plan)
    if dry_run:
        return

    k8s_dir = Path("k8s")
    if k8s_dir.exists():
        shutil.rmtree(k8s_dir)
        print("[green]✔ Removed k8s/ directory[/green]")
    else:
        print("[yellow]⚠ k8s/ directory not found, skipping[/yellow]")

    print()
    print("[bold green]✅ Kubernetes manifests removed successfully![/bold green]")
