# djboost 🚀

`djboost` is a CLI tool that generates a fully-configured, production-ready Django project in one command. No more repetitive boilerplate setup.

With a single command you get Django REST Framework, JWT Authentication, Celery, Redis, WebSockets (Channels), Docker, Swagger docs, and more — all pre-wired and ready to go.

## ✨ Features

- **API Ready** — Django REST Framework + Simple JWT pre-configured
- **API Docs** — Auto-generated Swagger UI and ReDoc via `drf-spectacular`
- **Async Tasks** — Celery + Redis integrated out of the box
- **WebSockets** — Django Channels with Daphne and Redis channel layers
- **Environment Variables** — `python-decouple` with a generated `.env` file
- **Database** — Pre-configured for PostgreSQL (SQLite default for dev)
- **CORS & Security** — `django-cors-headers` + standard security headers
- **Docker** — Ready-to-use `Dockerfile` and `docker-compose.yml`
- **Static Files** — Whitenoise configured for efficient static file serving
- **Code Quality** — `pre-commit` with `black`, `flake8`, and `isort`
- **Testing** — `pytest` + `pytest-django` with coverage pre-configured
- **CI/CD** — Modular GitHub Actions and GitLab CI pipelines
- **Custom Exception Handling** — Global DRF exception handler included

---

## � Installation

```bash
pip install djboost
```

---

## 🚀 Quick Start

### Step 1 — Create a virtual environment and activate it

```bash
python -m venv env

# Windows
env\Scripts\activate

# Mac / Linux
source env/bin/activate
```

### Step 2 — Install djboost

```bash
pip install djboost
```

### Step 3 — Navigate to an empty folder and create your project

```bash
# Create a project with a custom name
djboost create project myproject

# Or use the default name 'core'
djboost create project
```

This single command will automatically:

1. Install Django and run `startproject`
2. Update `settings.py` with all advanced configurations
3. Generate `.env`, `Dockerfile`, `docker-compose.yml`, and `.gitignore`
4. Generate `pytest.ini` and `.pre-commit-config.yaml`
5. Create `/apps`, `/static`, and `/media` directories
6. Install all required dependencies
7. Initialize a `git` repository and set up `pre-commit` hooks
8. Freeze dependencies into `requirements.txt`

---

## 🧱 Creating Apps

Apps are created inside the `apps/` directory to keep your project root clean. Settings and URLs are auto-configured.

```bash
# Navigate to your project root first
cd myproject

# Create a new app
djboost create app users
```

This will:
- Create `apps/users/` with standard Django app structure
- Auto-add `'apps.users'` to `INSTALLED_APPS`
- Auto-map `api/users/` in `urls.py`
- Create a starter `urls.py` inside the app

---

## � Managing CI/CD Pipelines

CI/CD is modular — add or remove it any time after project creation.

### Add a pipeline

```bash
djboost add cicd github   # GitHub Actions
djboost add cicd gitlab   # GitLab CI
```

### Remove a pipeline

```bash
djboost remove cicd github
djboost remove cicd gitlab
```

---

## 🏃 Running Your Project

### Locally

```bash
# Apply migrations
python manage.py migrate

# Start the dev server
python manage.py runserver
```

### API Documentation

Once your server is running:

| Interface | URL |
|---|---|
| Swagger UI | `http://127.0.0.1:8000/api/schema/swagger-ui/` |
| ReDoc | `http://127.0.0.1:8000/api/schema/redoc/` |
| OpenAPI Schema | `http://127.0.0.1:8000/api/schema/` |

### Testing

```bash
pytest
```

### With Docker

```bash
docker-compose up --build
```

This spins up PostgreSQL, Redis, Celery worker, and a Daphne ASGI server together.

---

## ⚙️ CLI Reference

```
djboost --help
djboost --version

djboost create project [NAME]     Create a new Django project
djboost create app NAME           Create a new app inside apps/

djboost add cicd github|gitlab    Add a CI/CD pipeline
djboost remove cicd github|gitlab Remove a CI/CD pipeline
```

---

## 🐍 Requirements

- Python 3.10+
- Virtual environment (required — djboost will warn you if not activated)

---

## 📄 License

MIT
