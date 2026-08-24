import os
import shutil

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.safe_engine import execute_plan, generate_remove_plan


def remove_cicd_command(
    provider: str = typer.Argument(..., help="The CI/CD provider to remove (github or gitlab)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without applying them."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip reverse dependency checks."),
):
    """Remove CI/CD pipeline from the project."""
    check_virtual_environment()
    provider = provider.lower()

    if provider not in ["github", "gitlab"]:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported: github, gitlab.[/red]")
        raise typer.Exit(code=1)

    feature_name = f"cicd-{provider}"
    icon = "⚡" if provider == "github" else "🦊"
    name = "GitHub Actions" if provider == "github" else "GitLab CI"

    print(f"\n[bold red]🗑️  Removing {name} from your project...[/bold red]\n")

    # Generate plan through safe engine
    plan = generate_remove_plan(feature_name, dry_run=dry_run, force=force)

    if plan.errors and not dry_run:
        for err in plan.errors:
            print(f"[red]✘ {err}[/red]")
        raise typer.Exit(1)

    if plan.idempotent:
        print(f"[yellow]⚠ {name} is not currently configured.[/yellow]")
        raise typer.Exit(0)

    # Execute plan (dry-run or real)
    record = execute_plan(plan)

    if dry_run:
        raise typer.Exit(0)

    # Apply the actual file changes
    if provider == "github":
        github_dir = ".github"
        if os.path.exists(github_dir):
            print("[cyan]📝 Removing GitHub Actions files...[/cyan]")
            shutil.rmtree(github_dir)
            print("[green]  ✔ .github/workflows/ deleted[/green]")
        else:
            print("[yellow]⚠️  GitHub Actions workflow is not present in this project.[/yellow]")
            raise typer.Exit(0)

    elif provider == "gitlab":
        gitlab_file = ".gitlab-ci.yml"
        if os.path.exists(gitlab_file):
            print("[cyan]📝 Removing GitLab CI file...[/cyan]")
            os.remove(gitlab_file)
            print("[green]  ✔ .gitlab-ci.yml deleted[/green]")
        else:
            print("[yellow]⚠️  GitLab CI pipeline is not present in this project.[/yellow]")
            raise typer.Exit(0)

    print()
    print(f"[bold green]✅ {name} removed successfully![/bold green]")
