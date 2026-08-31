import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.cicd import generate_github_actions, generate_gitlab_ci
from djboost.generators.safe_engine import execute_plan, generate_add_plan


def add_cicd_command(
    provider: str = typer.Argument(..., help="The CI/CD provider to add (github or gitlab)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip conflict checks."),
):
    """Add CI/CD pipeline to an existing Django project."""
    check_virtual_environment()
    provider = provider.lower()

    if provider not in ["github", "gitlab"]:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported: github, gitlab.[/red]")
        raise typer.Exit(code=1)

    feature_name = f"cicd-{provider}"
    icon = "⚡" if provider == "github" else "🦊"
    name = "GitHub Actions" if provider == "github" else "GitLab CI"

    print(f"\n[bold green]{icon} Adding {name} to your project...[/bold green]\n")

    # Generate plan through safe engine
    plan = generate_add_plan(feature_name, dry_run=dry_run, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print(f"[yellow]⚠ {name} is already configured.[/yellow]")
        raise typer.Exit(0)

    # Define the actual file generation callback
    def apply_cicd():
        if provider == "github":
            generate_github_actions()
            print("[green]  ✔ .github/workflows/main.yml created[/green]")
        else:
            generate_gitlab_ci()
            print("[green]  ✔ .gitlab-ci.yml created[/green]")

    # Execute plan with the apply callback (safe engine handles rollback)
    record = execute_plan(plan, apply_fn=apply_cicd)

    if dry_run or record is None and plan.errors:
        raise typer.Exit(1 if plan.errors else 0)

    print()
    print(f"[bold green]✅ {name} added successfully![/bold green]")
    print()
    print("[cyan]Pipeline includes:[/cyan]")
    print("  • [bold]Lint[/bold] — black, flake8, isort")
    print("  • [bold]Test[/bold] — pytest with coverage")
    print("  • [bold]Build[/bold] — Docker image build")
    print("  • [bold]Deploy[/bold] — Production deployment")
    print()
    print("[cyan]Next steps:[/cyan]")
    if provider == "github":
        print("  1. Push to [bold]main[/bold] branch to trigger workflow")
        print("  2. Add secrets in [bold]Settings → Secrets[/bold]")
    else:
        print("  1. Push to [bold]main[/bold] branch to trigger pipeline")
        print("  2. Configure CI/CD variables in [bold]Settings → CI/CD[/bold]")
