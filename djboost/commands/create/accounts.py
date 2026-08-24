from pathlib import Path

import typer
from rich import print

from djboost.generator import check_virtual_environment
from djboost.generators.accounts_app import create_accounts_app, get_project_name


def create_accounts_command():
    """Create a complete accounts app with auth APIs like famka."""
    check_virtual_environment()

    # Check if project was created by djboost
    if not Path("apps").exists() or not Path("common").exists():
        print("[yellow]Warning: This project was not created by djboost.[/yellow]")
        print("[yellow]Some features may not work correctly.[/yellow]")
        print("[cyan]Recommended: Run 'djboost startproject' first for best results.[/cyan]")
        print()

    name = get_project_name()
    if not name:
        raise typer.Exit(1)

    create_accounts_app(name)
