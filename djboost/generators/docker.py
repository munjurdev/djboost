"""Docker generators — create project docker + add docker — all in one file."""

from pathlib import Path

from rich import print


def _check_installed_features():
    """Check which optional features are currently installed in the project."""
    requirements_path = Path("requirements.txt")
    features = {
        "celery": False,
        "channels": False,
        "daphne": False,
        "flower": False,
        "redis": False,
    }
    if requirements_path.exists():
        content = requirements_path.read_text(encoding="utf-8").lower()
        features["celery"] = "celery" in content
        features["channels"] = "channels" in content
        features["daphne"] = "daphne" in content
        features["flower"] = "flower" in content
        features["redis"] = "redis" in content
    return features


# ── CREATE PROJECT DOCKER ─
def generate_docker_files(name):
    """Generate Dockerfile, docker-compose.yml, and .dockerignore.

    Only generates services that match the project's installed features.
    """
    _write_dockerfile()
    _write_docker_compose(name)
    _write_dockerignore()


def _write_dockerfile():
    content = """FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \\
    && apt-get install -y --no-install-recommends gcc libpq-dev \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
"""
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(content)


def _write_docker_compose(name):
    """Generate docker-compose.yml with only installed features."""
    content = f"""version: '3.8'

services:

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${{POSTGRES_DB:-{name}_db}}
      POSTGRES_USER: ${{POSTGRES_USER:-{name}_user}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD:-{name}_password}}
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"

  web:
    build: .
    restart: unless-stopped
    command: gunicorn {name}.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_HOST: redis
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
"""
    with open("docker-compose.yml", "w", encoding="utf-8") as f:
        f.write(content)


def _write_dockerignore():
    content = """.env
.venv
env/
venv/
__pycache__/
*.pyc
*.pyo
db.sqlite3
media/
static/
.git/
.pytest_cache/
htmlcov/
"""
    with open(".dockerignore", "w", encoding="utf-8") as f:
        f.write(content)


# ── ADD DOCKER ─
def get_project_name():
    """Extract project name from manage.py."""
    import re

    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in the project root?[/red]")
        return None

    content = Path("manage.py").read_text(encoding="utf-8")
    match = re.search(r"['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^.]+)\.settings['\"]", content)
    if match:
        return match.group(1)

    print("[red]Error: Could not determine project name from manage.py[/red]")
    return None


def generate_dockerfile():
    """Generate Dockerfile for existing project."""
    dockerfile_content = """FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \\
    && apt-get install -y --no-install-recommends gcc libpq-dev \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
"""
    dockerfile_path = Path("Dockerfile")
    if dockerfile_path.exists():
        print("[yellow]Warning: Dockerfile already exists. Skipping.[/yellow]")
        return False

    dockerfile_path.write_text(dockerfile_content, encoding="utf-8")
    print("[green]✔ Created Dockerfile[/green]")
    return True


def generate_docker_compose_add(name):
    """Generate docker-compose.yml — only includes services for installed features."""
    features = _check_installed_features()

    lines = []
    lines.append("version: '3.8'")
    lines.append("")
    lines.append("services:")
    lines.append("")

    # --- db (always) ---
    lines.append("  db:")
    lines.append("    image: postgres:15-alpine")
    lines.append("    restart: unless-stopped")
    lines.append("    volumes:")
    lines.append("      - postgres_data:/var/lib/postgresql/data")
    lines.append("    environment:")
    lines.append("      POSTGRES_DB: " + name + "_db")
    lines.append("      POSTGRES_USER: " + name + "_user")
    lines.append("      POSTGRES_PASSWORD: " + name + "_password")
    lines.append("    ports:")
    lines.append('      - "5432:5432"')
    lines.append("")

    # --- redis (always) ---
    lines.append("  redis:")
    lines.append("    image: redis:7-alpine")
    lines.append("    restart: unless-stopped")
    lines.append("    ports:")
    lines.append('      - "6379:6379"')
    lines.append("")

    # --- web (always) ---
    if features["daphne"]:
        web_command = "daphne -b 0.0.0.0 -p 8000 " + name + ".asgi:application"
    else:
        web_command = "gunicorn " + name + ".wsgi:application --bind 0.0.0.0:8000 --workers 3"

    lines.append("  web:")
    lines.append("    build: .")
    lines.append("    restart: unless-stopped")
    lines.append("    command: " + web_command)
    lines.append("    volumes:")
    lines.append("      - .:/app")
    lines.append("    ports:")
    lines.append('      - "8000:8000"')
    lines.append("    env_file:")
    lines.append("      - .env")
    lines.append("    environment:")
    lines.append("      DB_HOST: db")
    lines.append("      REDIS_HOST: redis")
    if features["celery"]:
        lines.append("      CELERY_BROKER_URL: redis://redis:6379/0")
        lines.append("      CELERY_RESULT_BACKEND: redis://redis:6379/0")
    lines.append("    depends_on:")
    lines.append("      - db")
    lines.append("      - redis")
    lines.append("")

    # --- celery (only if installed) ---
    if features["celery"]:
        lines.append("  celery:")
        lines.append("    build: .")
        lines.append("    restart: unless-stopped")
        lines.append("    command: celery -A " + name + " worker -l info")
        lines.append("    volumes:")
        lines.append("      - .:/app")
        lines.append("    env_file:")
        lines.append("      - .env")
        lines.append("    environment:")
        lines.append("      DB_HOST: db")
        lines.append("      REDIS_HOST: redis")
        lines.append("      CELERY_BROKER_URL: redis://redis:6379/0")
        lines.append("      CELERY_RESULT_BACKEND: redis://redis:6379/0")
        lines.append("    depends_on:")
        lines.append("      - db")
        lines.append("      - redis")
        lines.append("")

        lines.append("  celery-beat:")
        lines.append("    build: .")
        lines.append("    restart: unless-stopped")
        lines.append("    command: celery -A " + name + " beat -l info")
        lines.append("    volumes:")
        lines.append("      - .:/app")
        lines.append("    env_file:")
        lines.append("      - .env")
        lines.append("    environment:")
        lines.append("      DB_HOST: db")
        lines.append("      REDIS_HOST: redis")
        lines.append("      CELERY_BROKER_URL: redis://redis:6379/0")
        lines.append("      CELERY_RESULT_BACKEND: redis://redis:6379/0")
        lines.append("    depends_on:")
        lines.append("      - db")
        lines.append("      - redis")
        lines.append("")

        lines.append("  flower:")
        lines.append("    build: .")
        lines.append("    restart: unless-stopped")
        lines.append("    command: celery -A " + name + " flower --port=5555")
        lines.append("    volumes:")
        lines.append("      - .:/app")
        lines.append("    ports:")
        lines.append('      - "5555:5555"')
        lines.append("    env_file:")
        lines.append("      - .env")
        lines.append("    environment:")
        lines.append("      DB_HOST: db")
        lines.append("      REDIS_HOST: redis")
        lines.append("      CELERY_BROKER_URL: redis://redis:6379/0")
        lines.append("      CELERY_RESULT_BACKEND: redis://redis:6379/0")
        lines.append("    depends_on:")
        lines.append("      - db")
        lines.append("      - redis")
        lines.append("")

    lines.append("volumes:")
    lines.append("  postgres_data:")
    lines.append("")

    compose_content = "\n".join(lines)

    compose_path = Path("docker-compose.yml")
    if compose_path.exists():
        print("[yellow]Warning: docker-compose.yml already exists. Skipping.[/yellow]")
        return False

    compose_path.write_text(compose_content, encoding="utf-8")
    print("[green]✔ Created docker-compose.yml[/green]")

    # Show what services were included
    included = ["web", "db", "redis"]
    if features["celery"]:
        included.extend(["celery", "celery-beat", "flower"])
    print("[cyan]   Services: " + ", ".join(included) + "[/cyan]")

    return True


def generate_dockerignore_add():
    """Generate .dockerignore for existing project."""
    dockerignore_content = """.env
.venv
env/
venv/
__pycache__/
*.pyc
*.pyo
db.sqlite3
media/
static/
.git/
.pytest_cache/
htmlcov/
"""
    dockerignore_path = Path(".dockerignore")
    if dockerignore_path.exists():
        print("[yellow]Warning: .dockerignore already exists. Skipping.[/yellow]")
        return False

    dockerignore_path.write_text(dockerignore_content, encoding="utf-8")
    print("[green]✔ Created .dockerignore[/green]")
    return True


def add_docker_to_requirements():
    """Add flower to requirements.txt if Celery is installed."""
    features = _check_installed_features()
    requirements_path = Path("requirements.txt")

    existing_packages = ""
    if requirements_path.exists():
        existing_packages = requirements_path.read_text(encoding="utf-8").lower()

    packages_to_add = []

    if features["celery"] and "flower" not in existing_packages:
        packages_to_add.append("flower>=2.0,<3")

    if not features["daphne"] and "gunicorn" not in existing_packages:
        packages_to_add.append("gunicorn>=21.2,<23")

    if packages_to_add:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for package in packages_to_add:
                f.write(package + "\n")
        print("[green]✔ Added " + ", ".join(packages_to_add) + " to requirements.txt[/green]")
    else:
        print("[yellow]No additional Docker packages needed.[/yellow]")
