# djboost 🚀

[![PyPI version](https://badge.fury.io/py/djboost.svg)](https://pypi.org/project/djboost/)
[![Python](https://img.shields.io/pypi/pyversions/djboost)](https://pypi.org/project/djboost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**One command. Production-ready Django.**

`djboost` generates a fully-configured Django project in seconds — DRF, JWT, Celery, Redis, WebSockets, Docker, Swagger, and more. All pre-wired and ready to go. No boilerplate. No config hunting.

```bash
pip install djboost
djboost create project myproject
```

That's it. Your project is ready.

---

## What you get

| Feature | Details |
|---|---|
| **REST API** | Django REST Framework + Simple JWT pre-configured |
| **API Docs** | Swagger UI + ReDoc at `/api/schema/swagger-ui/` |
| **Async Tasks** | Celery + Redis, including Celery Beat schedule |
| **WebSockets** | Django Channels + Daphne ASGI server |
| **Database** | PostgreSQL config ready (SQLite default for dev) |
| **Environment** | `python-decouple` with fully pre-filled `.env` |
| **Docker** | `Dockerfile` + `docker-compose.yml` with 4 services |
| **Security** | CORS, CSRF, XSS headers, throttling all configured |
| **Static Files** | Whitenoise for efficient static file serving |
| **Code Quality** | `pre-commit` with `black`, `flake8`, `isort` |
| **Testing** | `pytest` + `pytest-django` with coverage |
| **CI/CD** | GitHub Actions and GitLab CI pipelines |
| **Exception Handling** | Global DRF handler → `{"success": false, "message": "..."}` |

---

## Quick Start

### 1 — Create a virtual environment

```bash
python -m venv env

# Windows
env\Scripts\activate

# Mac / Linux
source env/bin/activate
```

### 2 — Install djboost

```bash
pip install djboost
```

### 3 — Create your project

Navigate to an **empty folder** and run:

```bash
djboost create project myproject
```

This single command will:
1. Install Django and scaffold the project
2. Configure `settings.py` with 50+ production settings
3. Generate `.env` pre-filled with all required keys
4. Create `Dockerfile` + `docker-compose.yml` (web, db, redis, celery)
5. Set up `pytest.ini`, `.pre-commit-config.yaml`, `.gitignore`
6. Install all 19 dependencies with version pinning
7. Freeze `requirements.txt`

---

## Creating Apps

```bash
cd myproject
djboost create app users
```

This creates `apps/users/` and auto-generates:

```
apps/users/
  views.py        ← APIView boilerplate (List + Detail)
  serializers.py  ← ModelSerializer template
  urls.py         ← URL patterns
  tests.py        ← Test boilerplate
  models.py
  admin.py
  apps.py         ← name auto-set to 'apps.users'
```

Also automatically:
- Adds `'apps.users'` to `INSTALLED_APPS`
- Maps `/api/users/` in `urls.py`

---

## CI/CD Pipelines

Add or remove CI/CD any time — it's modular.

```bash
djboost add cicd github    # GitHub Actions
djboost add cicd gitlab    # GitLab CI

djboost remove cicd github
djboost remove cicd gitlab
```

---

## Running Your Project

```bash
python manage.py migrate
python manage.py runserver
```

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Health check |
| `http://127.0.0.1:8000/admin/` | Django Admin |
| `http://127.0.0.1:8000/api/schema/swagger-ui/` | Swagger UI |
| `http://127.0.0.1:8000/api/schema/redoc/` | ReDoc |

### With Docker

```bash
docker-compose up --build
```

Spins up PostgreSQL, Redis, Celery worker, and Daphne ASGI server.

---

## CLI Reference

```
djboost --version
djboost --help

djboost create project [NAME]      Create a new Django project (default: core)
djboost create app NAME            Create a new app inside apps/

djboost add cicd github|gitlab     Add CI/CD pipeline
djboost remove cicd github|gitlab  Remove CI/CD pipeline
```

---

## Requirements

- Python 3.10+
- Virtual environment (djboost will warn you if not activated)

---

## License

MIT — [Munjur Alom](https://github.com/munjurdev)
