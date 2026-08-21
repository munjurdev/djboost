import typer
from rich import print
from djboost.generator import generate_github_actions, generate_gitlab_ci, check_virtual_environment

def add_cicd_command(provider: str = typer.Argument(..., help="The CI/CD provider to add (github or gitlab)")):
    check_virtual_environment()
    provider = provider.lower()
    
    if provider not in ["github", "gitlab"]:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported providers are: github, gitlab.[/red]")
        raise typer.Exit(code=1)
    
    icon = "⚡" if provider == "github" else "🦊"
    name = "GitHub Actions" if provider == "github" else "GitLab CI"
    
    print(f"\n[bold green]{icon} Adding {name} to your project...[/bold green]\n")
    
    print("[cyan]📝 Generating CI/CD pipeline...[/cyan]")
    if provider == "github":
        generate_github_actions()
        print("[green]  ✔ .github/workflows/django.yml created[/green]")
    else:
        generate_gitlab_ci()
        print("[green]  ✔ .gitlab-ci.yml created[/green]")
    
    print("[cyan]⚙️  Configuring pipeline steps...[/cyan]")
    print("[green]  ✔ Lint & test stage[/green]")
    print("[green]  ✔ Build & deploy stage[/green]")
    
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
