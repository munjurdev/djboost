import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.api_docs import (
    get_project_name,
    add_spectacular_to_installed_apps,
    add_spectacular_settings,
    generate_api_docs_urls,
    add_spectacular_to_requirements,
)


def add_api_docs_command(
    provider: str = typer.Argument(
        "swagger",
        help="API documentation provider (swagger or redoc)"
    )
):
    """Add API documentation (Swagger/ReDoc) to an existing Django project."""
    check_virtual_environment()
    
    name = get_project_name()
    if not name:
        raise typer.Exit(1)
    
    provider = provider.lower()
    if provider not in ["swagger", "redoc", "both"]:
        print(f"[red]Error: Unsupported provider '{provider}'. Supported providers are: swagger, redoc, both.[/red]")
        raise typer.Exit(1)
    
    print(f"\n[bold green]📚 Adding API Documentation to project: {name}[/bold green]\n")
    
    # Step 1: Add drf-spectacular to INSTALLED_APPS
    print("[cyan]📝 Adding drf-spectacular to INSTALLED_APPS...[/cyan]")
    add_spectacular_to_installed_apps(name)
    
    # Step 2: Add Spectacular settings
    print("[cyan]⚙️  Adding Spectacular settings...[/cyan]")
    add_spectacular_settings(name)
    
    # Step 3: Generate API docs URLs
    print("[cyan]🔗 Generating API docs URLs...[/cyan]")
    generate_api_docs_urls(name)
    
    # Step 4: Add dependencies
    print("[cyan]📦 Adding dependencies...[/cyan]")
    add_spectacular_to_requirements()
    
    print()
    print("[bold green]✅ API Documentation added successfully![/bold green]")
    print()
    
    if provider in ["swagger", "both"]:
        print("[cyan]Swagger UI:[/cyan]")
        print("  [bold]http://localhost:8000/api/schema/swagger-ui/[/bold]")
    
    if provider in ["redoc", "both"]:
        print("[cyan]ReDoc:[/cyan]")
        print("  [bold]http://localhost:8000/api/schema/redoc/[/bold]")
    
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Run [bold]pip install -r requirements.txt[/bold]")
    print("  2. Run [bold]python manage.py runserver[/bold]")
    print("  3. Access API docs at the URLs above")
