import sys
import subprocess
from rich import print


PACKAGES = [
    "djangorestframework>=3.14,<4",
    "djangorestframework-simplejwt>=5.3,<6",
    "django-cors-headers>=4.3,<5",
    "python-decouple>=3.8,<4",
    "psycopg2-binary>=2.9,<3",
    "Pillow>=10.0,<12",
    "celery>=5.3,<6",
    "redis>=5.0,<6",
    "daphne>=4.0,<5",
    "channels>=4.0,<5",
    "channels-redis>=4.1,<5",
    "whitenoise>=6.6,<7",
    "drf-spectacular>=0.27,<1",
    "pytest>=7.4,<9",
    "pytest-django>=4.7,<5",
    "pytest-cov>=4.1,<6",
    "black>=23.0,<25",
    "flake8>=6.0,<8",
    "isort>=5.12,<6",
]


def install_dependencies():
    total = len(PACKAGES)
    print("[cyan]📦 Installing dependencies...[/cyan]")
    for i, package in enumerate(PACKAGES, 1):
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


def freeze_requirements():
    print("[cyan]📄 Freezing requirements...[/cyan]")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--local"],
        capture_output=True, text=True
    )
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
    print("[green]✔ requirements.txt created.[/green]")
