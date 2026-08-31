import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.kubernetes import generate_k8s_manifests, get_project_name
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_kubernetes_command(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add Kubernetes deployment manifests."""
    check_virtual_environment()
    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    print(f"\n[bold green]☸️  Adding Kubernetes manifests to project: {name}[/bold green]\n")

    plan = generate_add_plan("kubernetes", dry_run=dry_run, project_name=name, force=force)
    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)
    if plan.idempotent:
        print("[yellow]⚠ Kubernetes manifests already exist.[/yellow]")
        raise typer.Exit(0)

    def apply_kubernetes():
        generate_k8s_manifests(name)

    record = execute_plan(plan, project_name=name, apply_fn=apply_kubernetes)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print("[bold green]✅ Kubernetes manifests added successfully![/bold green]")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Edit k8s/secrets.yaml with real credentials")
    print("  2. Update k8s/ingress.yaml with your domain")
    print("  3. Apply: [bold]kubectl apply -f k8s/[/bold]")
