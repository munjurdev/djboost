import os
import shutil
import typer
from rich import print
from djboost.generator import check_virtual_environment

def remove_cicd_command(provider: str = typer.Argument(..., help="The CI/CD provider to remove (github or gitlab)")):
    check_virtual_environment()
    provider = provider.lower()
    if provider == "github":
        github_dir = ".github"
        if os.path.exists(github_dir):
            try:
                shutil.rmtree(github_dir)
                print("[green]GitHub Actions workflow removed successfully![/green]")
            except Exception as e:
                print(f"[red]Failed to remove GitHub Actions workflow: {e}[/red]")
        else:
            print("[yellow]GitHub Actions workflow is not present in this project.[/yellow]")
            
    elif provider == "gitlab":
        gitlab_file = ".gitlab-ci.yml"
        if os.path.exists(gitlab_file):
            try:
                os.remove(gitlab_file)
                print("[green]GitLab CI pipeline removed successfully![/green]")
            except Exception as e:
                print(f"[red]Failed to remove GitLab CI pipeline: {e}[/red]")
        else:
            print("[yellow]GitLab CI pipeline is not present in this project.[/yellow]")
            
    else:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported providers are: github, gitlab.[/red]")
        raise typer.Exit(code=1)
