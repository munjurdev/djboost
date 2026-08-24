"""PostgreSQL generator — add PostgreSQL database backend to a Django project."""

import re
from pathlib import Path

from rich import print


def get_project_name():
    """Extract project name from manage.py."""
    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in the project root?[/red]")
        return None
    content = Path("manage.py").read_text(encoding="utf-8")
    match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^.]+)\.settings['\"]", content)
    if match:
        return match.group(1)
    print("[red]Error: Could not determine project name from manage.py[/red]")
    return None


def update_settings_postgres(name: str):
    """Update settings.py to use PostgreSQL database."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "django.db.backends.postgresql" in content:
        print("[yellow]Warning: PostgreSQL already configured in settings.py. Skipping.[/yellow]")
        return True

    # Replace the DATABASES block
    new_db = """DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='{name}_db'),
        'USER': config('DB_USER', default='{name}_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', default=600, cast=int),
    }
}""".format(name=name)

    content = re.sub(
        r"DATABASES\s*=\s*\{.*?\}\s*\}\s*}",
        new_db,
        content,
        flags=re.DOTALL,
    )

    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Updated DATABASES to PostgreSQL in {name}/settings.py[/green]")
    return True


def update_env_postgres(name: str):
    """Update .env with PostgreSQL variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("[yellow]Warning: .env not found. Skipping.[/yellow]")
        return False

    content = env_path.read_text(encoding="utf-8")

    if "DB_ENGINE" in content:
        print("[yellow]Warning: DB vars already in .env. Skipping.[/yellow]")
        return True

    pg_env = f"""
# ── PostgreSQL ────────────────────────────────────────────────────────────────
DB_ENGINE=django.db.backends.postgresql
DB_NAME={name}_db
DB_USER={name}_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
"""
    content += pg_env
    env_path.write_text(content, encoding="utf-8")
    print("[green]✔ Added PostgreSQL vars to .env[/green]")
    return True


def add_postgres_to_requirements():
    """Add psycopg2-binary to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    if "psycopg2" not in existing:
        with open(requirements_path, "a", encoding="utf-8") as f:
            f.write("psycopg2-binary>=2.9,<3\n")
        print("[green]✔ Added psycopg2-binary to requirements.txt[/green]")
    else:
        print("[yellow]Warning: psycopg2-binary already in requirements.txt. Skipping.[/yellow]")
