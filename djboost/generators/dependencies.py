import subprocess
import sys

from rich import print

# Capture the real Python executable at import time, before any code
# can mutate sys.executable via check_virtual_environment().
_REAL_PYTHON = sys.executable

# ── Essential packages (always installed with create project) ────────────────
ESSENTIAL_PACKAGES = [
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

# ── Optional packages (only installed when needed) ───────────────────────────
OPTIONAL_PACKAGES = {
    "celery": ["celery>=5.4,<6", "redis>=5.0,<6"],
    "channels": ["daphne>=4.1,<5", "channels>=4.1,<5", "channels-redis>=4.2,<5"],
    "postgresql": ["psycopg2-binary>=2.9,<3"],
}


def install_dependencies(packages=None):
    """Install a list of packages in a single batch call. Defaults to ESSENTIAL_PACKAGES."""
    if packages is None:
        packages = ESSENTIAL_PACKAGES

    print("[cyan]📦 Installing dependencies...[/cyan]")
    for pkg in packages:
        print(f"[cyan]   + {pkg}[/cyan]")
    result = subprocess.run(
        [_REAL_PYTHON, "-m", "pip", "install", "-q", *packages],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[red]Error installing packages:\n{result.stderr}[/red]")
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


def add_to_requirements(packages):
    """Append specific packages to requirements.txt (no freeze)."""
    from pathlib import Path
    req_path = Path("requirements.txt")
    existing = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
    added = []
    for pkg in packages:
        pkg_name = pkg.split(">=")[0].split("<")[0].split("==")[0].strip()
        if pkg_name.lower() not in existing.lower():
            added.append(pkg)
    if added:
        with open(req_path, "a", encoding="utf-8") as f:
            for pkg in added:
                f.write(f"{pkg}\n")
        print(f"[green]✔ Added {len(added)} package(s) to requirements.txt[/green]")
    else:
        print("[yellow]⚠ Packages already in requirements.txt[/yellow]")


def remove_from_requirements(packages):
    """Remove specific packages from requirements.txt."""
    from pathlib import Path
    req_path = Path("requirements.txt")
    if not req_path.exists():
        return
    content = req_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []
    removed = []
    for line in lines:
        line_stripped = line.strip()
        should_remove = False
        for pkg in packages:
            pkg_name = pkg.split(">=")[0].split("<")[0].split("==")[0].strip()
            if line_stripped.lower().startswith(pkg_name.lower()):
                should_remove = True
                removed.append(line_stripped)
                break
        if not should_remove:
            new_lines.append(line)
    if removed:
        req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"[green]✔ Removed {len(removed)} package(s) from requirements.txt[/green]")


def uninstall_packages(packages):
    """Uninstall a list of Python packages in a single batch call."""
    if not packages:
        return
    print("[cyan]📦 Uninstalling packages...[/cyan]")
    pkg_names = [
        package.split(">=")[0].split("<")[0].split("==")[0].strip()
        for package in packages
    ]
    for name in pkg_names:
        print(f"[cyan]   - {name}[/cyan]")
    result = subprocess.run(
        [_REAL_PYTHON, "-m", "pip", "uninstall", "-y", "-q", *pkg_names],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        for name in pkg_names:
            print(f"[green]   ✔ Uninstalled {name}[/green]")
    else:
        for name in pkg_names:
            print(f"[yellow]   ⚠ {name} not installed, skipping[/yellow]")


def uninstall_optional_packages(category: str):
    """Uninstall optional packages by category."""
    if category not in OPTIONAL_PACKAGES:
        print(f"[red]Unknown category: {category}. Available: {list(OPTIONAL_PACKAGES.keys())}[/red]")
        return False

    packages = OPTIONAL_PACKAGES[category]
    uninstall_packages(packages)
    return True
