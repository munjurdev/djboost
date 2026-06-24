import sys
from rich import print


def check_virtual_environment():
    """Check if user is inside a virtual environment."""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    if not in_venv:
        print("[bold red]⚠ You are not inside a virtual environment![/bold red]")
        print("[yellow]Please create and activate a virtual environment first:[/yellow]")
        print()
        print("  [cyan]python -m venv env[/cyan]")
        print()
        print("  [cyan]# Windows:[/cyan]")
        print("  [cyan]env\\Scripts\\activate[/cyan]")
        print()
        print("  [cyan]# Mac/Linux:[/cyan]")
        print("  [cyan]source env/bin/activate[/cyan]")
        print()
        import typer
        raise typer.Exit(1)


def validate_name(name: str, label: str = "name"):
    """Validate that name is a valid Python identifier."""
    if not name.isidentifier():
        print(f"[red]Error: '{name}' is not a valid {label}. Use only letters, numbers, and underscores.[/red]")
        import typer
        raise typer.Exit(1)
    if name[0].isdigit():
        print(f"[red]Error: '{name}' must not start with a digit.[/red]")
        import typer
        raise typer.Exit(1)
