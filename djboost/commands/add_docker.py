import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.docker_add import (
    get_project_name,
    generate_dockerfile,
    generate_docker_compose,
    generate_dockerignore,
    add_docker_to_requirements,
)


def add_docker_command():
    """Add Docker configuration to an existing Django project."""
    check_virtual_environment()
    
    name = get_project_name()
    if not name:
        raise typer.Exit(1)
    
    print(f"\n[bold green]🐳 Adding Docker to project: {name}[/bold green]\n")
    
    # Step 1: Generate Dockerfile
    print("[cyan]📝 Generating Dockerfile...[/cyan]")
    generate_dockerfile()
    
    # Step 2: Generate docker-compose.yml
    print("[cyan]📝 Generating docker-compose.yml...[/cyan]")
    generate_docker_compose(name)
    
    # Step 3: Generate .dockerignore
    print("[cyan]📝 Generating .dockerignore...[/cyan]")
    generate_dockerignore()
    
    # Step 4: Add flower to requirements
    print("[cyan]📦 Adding flower to requirements...[/cyan]")
    add_docker_to_requirements()
    
    print()
    print("[bold green]✅ Docker added successfully![/bold green]")
    print()
    print("[cyan]Services included:[/cyan]")
    print("  • [bold]web[/bold] - Django application")
    print("  • [bold]db[/bold] - PostgreSQL database")
    print("  • [bold]redis[/bold] - Redis cache/broker")
    print("  • [bold]celery[/bold] - Celery worker")
    print("  • [bold]celery-beat[/bold] - Celery Beat scheduler")
    print("  • [bold]flower[/bold] - Celery monitoring dashboard")
    print()
    print("[cyan]Next steps:[/cyan]")
    print("  1. Update [bold].env[/bold] with your database credentials")
    print("  2. Run [bold]docker-compose up --build[/bold]")
    print("  3. Access Django at [bold]http://localhost:8000[/bold]")
    print("  4. Access Flower at [bold]http://localhost:5555[/bold]")
