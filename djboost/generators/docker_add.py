from pathlib import Path
from rich import print


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
    dockerfile_content = """FROM python:3.11-slim

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


def generate_docker_compose(name: str):
    """Generate docker-compose.yml for existing project."""
    compose_content = f"""version: '3.8'

services:

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: {name}_db
      POSTGRES_USER: {name}_user
      POSTGRES_PASSWORD: {name}_password
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
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      REDIS_URL: redis://redis:6379/1
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery:
    build: .
    restart: unless-stopped
    command: celery -A {name} worker -l info
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      REDIS_URL: redis://redis:6379/1
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    restart: unless-stopped
    command: celery -A {name} beat -l info
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      REDIS_URL: redis://redis:6379/1
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    depends_on:
      - db
      - redis

  flower:
    build: .
    restart: unless-stopped
    command: celery -A {name} flower --port=5555
    volumes:
      - .:/app
    ports:
      - "5555:5555"
    env_file:
      - .env
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      REDIS_URL: redis://redis:6379/1
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
"""
    compose_path = Path("docker-compose.yml")
    if compose_path.exists():
        print("[yellow]Warning: docker-compose.yml already exists. Skipping.[/yellow]")
        return False
    
    compose_path.write_text(compose_content, encoding="utf-8")
    print("[green]✔ Created docker-compose.yml[/green]")
    return True


def generate_dockerignore():
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
    """Add flower to requirements.txt if not present."""
    requirements_path = Path("requirements.txt")
    
    existing_packages = []
    if requirements_path.exists():
        existing_content = requirements_path.read_text(encoding="utf-8")
        existing_packages = existing_content.lower()
    
    packages_to_add = []
    if "flower" not in existing_packages:
        packages_to_add.append("flower>=2.0,<3")
    
    if packages_to_add:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for package in packages_to_add:
                f.write(f"{package}\n")
        print(f"[green]✔ Added flower to requirements.txt[/green]")
    else:
        print("[yellow]Warning: flower already in requirements.txt. Skipping.[/yellow]")
