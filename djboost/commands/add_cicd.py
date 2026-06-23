import typer
from rich import print
from djboost.generator import generate_github_actions, generate_gitlab_ci, check_virtual_environment

def add_cicd_command(provider: str = typer.Argument(..., help="The CI/CD provider to add (github or gitlab)")):
    check_virtual_environment()
    provider = provider.lower()
    if provider == "github":
        generate_github_actions()
        print("[green]GitHub Actions workflow created successfully![/green]")
    elif provider == "gitlab":
        generate_gitlab_ci()
        print("[green]GitLab CI pipeline created successfully![/green]")
    else:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported providers are: github, gitlab.[/red]")
        raise typer.Exit(code=1)
