import typer
from rich import print
from djboost.generator import check_virtual_environment
from djboost.generators.accounts_app import get_project_name, create_accounts_app


def create_accounts_command():
    """Create a complete accounts app with auth APIs like famka."""
    check_virtual_environment()
    
    name = get_project_name()
    if not name:
        raise typer.Exit(1)
    
    create_accounts_app(name)
