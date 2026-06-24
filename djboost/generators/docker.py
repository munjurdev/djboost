def generate_docker_files(name: str):
    """Generate Dockerfile, docker-compose.yml, and .dockerignore."""
    _write_dockerfile()
    _write_docker_compose(name)
    _write_dockerignore()


def _write_dockerfile():
    content = """FROM python:3.11-slim

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


def _write_docker_compose(name: str):
    content = f"""version: '3.8'

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
    command: daphne -b 0.0.0.0 -p 8000 {name}.asgi:application
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
