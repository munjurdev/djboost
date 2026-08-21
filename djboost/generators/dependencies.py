import sys
import subprocess
from rich import print


# ── Essential packages (always installed with create project) ────────────────
ESSENTIAL_PACKAGES = [
    "djangorestframework>=3.14,<4",
    "djangorestframework-simplejwt>=5.3,<6",
    "django-cors-headers>=4.3,<5",
    "python-decouple>=3.8,<4",
    "Pillow>=10.0,<12",
    "drf-spectacular>=0.27,<1",
    "whitenoise>=6.6,<7",
    "pytest>=7.4,<9",
    "pytest-django>=4.7,<5",
    "pytest-cov>=4.1,<6",
    "black>=23.0,<25",
    "flake8>=6.0,<8",
    "isort>=5.12,<6",
]

# ── Optional packages (only installed when needed) ───────────────────────────
OPTIONAL_PACKAGES = {
    "celery": [
        "celery>=5.3,<6",
        "redis>=5.0,<6",
    ],
    "channels": [
        "daphne>=4.0,<5",
        "channels>=4.0,<5",
        "channels-redis>=4.1,<5",
    ],
    "postgresql": [
        "psycopg2-binary>=2.9,<3",
    ],
}


def install_dependencies(packages=None):
    """Install a list of packages. Defaults to ESSENTIAL_PACKAGES."""
    if packages is None:
        packages = ESSENTIAL_PACKAGES
    
    total = len(packages)
    print("[cyan]📦 Installing dependencies...[/cyan]")
    for i, package in enumerate(packages, 1):
        print(f"[cyan]   [{i}/{total}] {package}[/cyan]")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "-q"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[red]Error installing {package}:\n{result.stderr}[/red]")
            import typer
            raise typer.Exit(1)
    print("[green]✔ All dependencies installed.[/green]")


def install_optional_packages(category: str):
    """Install optional packages by category (celery, channels, postgresql)."""
    if category not in OPTIONAL_PACKAGES:
        print(f"[red]Unknown category: {category}. Available: {list(OPTIONAL_PACKAGES.keys())}[/red]")
        return False
    
    packages = OPTIONAL_PACKAGES[category]
    print(f"\n[cyan]📦 Installing {category} packages...[/cyan]")
    install_dependencies(packages)
    return True


def freeze_requirements():
    print("[cyan]📄 Freezing requirements...[/cyan]")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--local"],
        capture_output=True, text=True
    )
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)


def uninstall_packages(packages):
    """Uninstall a list of Python packages."""
    print("[cyan]📦 Uninstalling packages...[/cyan]")
    for package in packages:
        # Get package name without version
        pkg_name = package.split(">=")[0].split("<")[0].split("==")[0].strip()
        print(f"[cyan]   Uninstalling {pkg_name}...[/cyan]")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", pkg_name, "-y", "-q"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"[green]   ✔ Uninstalled {pkg_name}[/green]")
        else:
            print(f"[yellow]   ⚠ {pkg_name} not installed, skipping[/yellow]")


def uninstall_optional_packages(category: str):
    """Uninstall optional packages by category."""
    if category not in OPTIONAL_PACKAGES:
        print(f"[red]Unknown category: {category}. Available: {list(OPTIONAL_PACKAGES.keys())}[/red]")
        return False
    
    packages = OPTIONAL_PACKAGES[category]
    uninstall_packages(packages)
    return True
