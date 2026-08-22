import os
import shutil
import typer
from rich import print
from djboost.generator import check_virtual_environment


def remove_cicd_command(provider: str = typer.Argument(..., help="The CI/CD provider to remove (github or gitlab)")):
    check_virtual_environment()
    provider = provider.lower()

    if provider not in ["github", "gitlab"]:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported providers are: github, gitlab.[/red]")
        raise typer.Exit(code=1)

    icon = "⚡" if provider == "github" else "🦊"
    name = "GitHub Actions" if provider == "github" else "GitLab CI"

    print(f"\n[bold red]🗑️  Removing {name} from your project...[/bold red]\n")

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
