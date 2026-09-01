import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich import print

# Capture the real Python executable at import time, before any code
# can mutate sys.executable via check_virtual_environment().
_REAL_PYTHON = sys.executable


def get_venv_python_path(venv_path: Optional[Path] = None) -> Optional[Path]:
    """Get the Python executable path inside a virtual environment.

    Works on Windows, Mac, and Linux.
    """
    if venv_path is None:
        venv_path = Path("env")

    if sys.platform == "win32":
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"

    return venv_python if venv_python.exists() else None


def get_activate_command(venv_path: Optional[Path] = None) -> str:
    """Return the platform-specific activation command string."""
    if venv_path is None:
        venv_path = Path("env")

    if sys.platform == "win32":
        return str(venv_path / "Scripts" / "activate")
    else:
        return f"source {venv_path / 'bin' / 'activate'}"


def check_virtual_environment():
    """Check if user is inside a virtual environment.

    If not, automatically create one and use it.
    Works on Windows, Mac, and Linux.
    """
    in_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

    if in_venv:
        return True

    # Not in venv — try to auto-create
    print("[yellow]⚠ Not inside a virtual environment.[/yellow]")
    print("[cyan]Creating virtual environment automatically...[/cyan]")
    print()

    venv_path = Path("env")

    # Check if env/ already exists
    if venv_path.exists():
        print("[green]✔ Virtual environment 'env/' already exists.[/green]")
    else:
        # Create virtual environment
        try:
            result = subprocess.run([_REAL_PYTHON, "-m", "venv", "env"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[red]Error creating virtual environment: {result.stderr}[/red]")
                print("[yellow]Please create manually: python -m venv env[/yellow]")
                import typer

                raise typer.Exit(1)
            print("[green]✔ Virtual environment created at env/[/green]")
        except Exception as e:
            print(f"[red]Error creating virtual environment: {e}[/red]")
            import typer

            raise typer.Exit(1)

    # Get the venv Python path
    venv_python = get_venv_python_path(venv_path)
    if venv_python is None:
        print(f"[red]Error: venv Python not found at {venv_path}[/red]")
        import typer

        raise typer.Exit(1)

    # Install packages in the venv
    print("[cyan]Installing packages in virtual environment...[/cyan]")

    essential_packages = [
        "djangorestframework>=3.15,<4",
        "djangorestframework-simplejwt>=5.3,<6",
        "django-cors-headers>=4.3,<6",
        "python-decouple>=3.8,<4",
        "Pillow>=10.0,<13",
        "drf-spectacular>=0.27,<1",
        "whitenoise>=6.6,<8",
        "pytest>=7.4,<9",
        "pytest-django>=4.7,<6",
        "pytest-cov>=4.1,<7",
        "black>=23.0,<26",
        "flake8>=6.0,<9",
        "isort>=5.12,<7",
    ]

    for package in essential_packages:
        print(f"[cyan]   + {package}[/cyan]")
    result = subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-q", *essential_packages],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[red]Error installing packages: {result.stderr}[/red]")

    print("[green]✔ All packages installed.[/green]")
    print()
    print("[bold green]✅ Virtual environment ready![/bold green]")
    print()
    print("[cyan]To activate it:[/cyan]")
    print(f"  [bold]{get_activate_command(venv_path)}[/bold]")
    print()

    # IMPORTANT: Update sys.executable to use venv Python
    # This ensures all subsequent subprocess calls use the venv
    os.environ["VIRTUAL_ENV"] = str(venv_path.resolve())
    os.environ["PATH"] = str(venv_python.parent) + os.pathsep + os.environ.get("PATH", "")
    sys.executable = str(venv_python)

    return True


def validate_name(name: str, label: str = "name"):
    """Validate that name is a valid Python identifier."""
    if not name.isidentifier():
        print(f"[red]Error: '{name}' is not a valid {label}. Use only letters, numbers, and underscores.[/red]")
        import typer

        raise typer.Exit(1)
