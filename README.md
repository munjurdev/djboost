# djboost 🚀

[![PyPI version](https://img.shields.io/pypi/v/djboost.svg)](https://pypi.org/project/djboost/)
[![Python](https://img.shields.io/pypi/pyversions/djboost.svg)](https://pypi.org/project/djboost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/munjurdev/djboost/actions/workflows/ci.yml/badge.svg)](https://github.com/munjurdev/djboost/actions/workflows/ci.yml)

**The modern lifecycle CLI for Django — create, build, extend, validate, and maintain. Safely evolve your project with modular features.**

djboost gives you a production-ready Django foundation in seconds — DRF, JWT, testing, and more. Build incrementally, ship confidently.

```bash
pip install djboost
djboost startproject myproject

# or
python -m djboost startproject myproject
```

---

## Table of Contents

- [Getting Started](#-getting-started)
- [What You Get by Default](#-what-you-get-by-default)
- [Available Features](#-available-features-17)
- [Safe Feature Lifecycle](#-safe-feature-lifecycle)
- [Creating Apps](#-creating-apps)
- [Creating Accounts App](#-creating-accounts-app)
- [Project Management](#-project-management)
- [Response Format](#-response-format)
- [Running Your Project](#-running-your-project)
- [Dependencies](#-dependencies)
- [CLI Reference](#-cli-reference)

---

## 🏁 Getting Started

### Step 1 — Create a virtual environment

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

### Step 3 — Create your project

```bash
mkdir myproject && cd myproject
djboost startproject core
```

### Step 4 — Run it

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — you'll see:

```json
{"message": "API Server Running", "status": "ok"}
```

---

## 📦 What You Get by Default

When you run `djboost startproject core`, you get a complete foundation **without installing any optional packages**.

### Core Features (Always Included)

| Feature | What You Get | Why |
|---------|-------------|-----|
| **Django REST Framework** | Full API framework | Build REST APIs instantly |
| **Simple JWT** | Access + refresh tokens, rotation, blacklist | Secure authentication out of the box |
| **CORS Headers** | Cross-origin request handling | Frontend can call your API |
| **Environment Variables** | `.env` file with all required keys | Secrets stay out of source code |
| **Security Headers** | XSS filter, content-type nosniff, X-Frame-Options | Basic security baseline |
| **Throttling** | 100/day anonymous, 1000/day authenticated | Prevent abuse |
| **Static Files** | WhiteNoise for efficient serving | No extra server needed |
| **Testing** | pytest + pytest-django + coverage | Testing ready from day one |
| **Code Quality** | Black, Flake8, isort, pre-commit hooks | Consistent code style automatically |
| **API Docs Ready** | drf-spectacular installed | Add Swagger/ReDoc anytime |
| **Standard Responses** | `{success, message, data}` format | Consistent API contract |
| **Pagination** | Custom pagination with meta info | List endpoints paginated |
| **Exception Handler** | Global DRF error handler | Clean, predictable errors |
| **Email Config** | SMTP settings in `.env` | Ready for transactional emails |
| **Logging** | Console logging configured | Debug in development |

### What `startproject` Generates

```
myproject/
├── apps/                        ← Your Django apps go here
│   └── __init__.py
├── common/                      ← Shared utilities
│   ├── __init__.py
│   ├── responses.py             ← success_response(), error_response()
│   ├── pagination.py            ← CustomPagination
│   └── exceptions.py            ← custom_exception_handler
├── core/                        ← Project configuration
│   ├── __init__.py
│   ├── settings.py              ← Production-oriented settings
│   ├── urls.py                  ← Root URL configuration
│   ├── utils.py                 ← Exception handler
│   ├── wsgi.py
│   └── asgi.py
├── static/                      ← Static files
├── media/                       ← Uploaded files
├── .env                         ← Environment variables (auto-generated)
├── .gitignore                   ← Git ignore rules
├── .pre-commit-config.yaml      ← Code quality hooks
├── manage.py                    ← Django management
├── pytest.ini                   ← Test configuration
└── requirements.txt             ← Frozen dependencies (13 packages)
```

### Installed Packages (14 Total)

| Package | Version | Purpose |
|---------|---------|---------|
| Django | >=4.2,<7 | Web framework (4.2 LTS, 5.x, 6.x supported) |
| djangorestframework | >=3.15,<4 | REST API |
| djangorestframework-simplejwt | >=5.3,<6 | JWT authentication |
| django-cors-headers | >=4.3,<6 | CORS configuration |
| python-decouple | >=3.8,<4 | Environment variables |
| Pillow | >=10.0,<13 | Image handling |
| drf-spectacular | >=0.27,<1 | OpenAPI/Swagger support |
| whitenoise | >=6.6,<8 | Static file serving |
| pytest | >=7.4,<9 | Testing framework |
| pytest-django | >=4.7,<6 | Django test integration |
| pytest-cov | >=4.1,<7 | Test coverage |
| black | >=23.0,<26 | Code formatting |
| flake8 | >=6.0,<9 | Linting |
| isort | >=5.12,<7 | Import sorting |

---

## 🧩 Available Features (17)

djboost manages **17 features** with full dependency tracking. See them all with:

```bash
djboost features
```

### Core Features

| Feature | Command | Description |
|---------|---------|-------------|
| Celery | `djboost add celery` | Background task processing with Redis broker |
| Celery Beat | `djboost add celery-beat` | Periodic task scheduler |
| APScheduler | `djboost add scheduler` | Lightweight in-process job scheduler |

### Infrastructure

| Feature | Command | Description |
|---------|---------|-------------|
| Docker | `djboost add docker` | Containerization with Docker Compose |
| Kubernetes | `djboost add kubernetes` | K8s deployment/service/ingress/configmap/secrets |

### Database & Caching

| Feature | Command | Description |
|---------|---------|-------------|
| PostgreSQL | `djboost add postgres` | PostgreSQL backend with env-based config |
| Redis Cache | `djboost add redis-cache` | Redis-backed caching and session storage |

### API Features

| Feature | Command | Description |
|---------|---------|-------------|
| API Documentation | `djboost add api-docs swagger\|redoc\|both` | Swagger UI and/or ReDoc |
| GraphQL | `djboost add graphql` | Strawberry GraphQL API (type-safe, async-ready) |

### Realtime

| Feature | Command | Description |
|---------|---------|-------------|
| Django Channels | `djboost add channels` | WebSocket and async protocol support |

### CI/CD

| Feature | Command | Description |
|---------|---------|-------------|
| GitHub Actions | `djboost add cicd github` | GitHub Actions CI/CD pipeline |
| GitLab CI | `djboost add cicd gitlab` | GitLab CI/CD pipeline |

### Storage

| Feature | Command | Description |
|---------|---------|-------------|
| Cloud Storage | `djboost add storage` | S3-compatible file storage via django-storages |

### Security

| Feature | Command | Description |
|---------|---------|-------------|
| Security Headers | `djboost add security` | CSP, HSTS, secure cookies |

### Observability

| Feature | Command | Description |
|---------|---------|-------------|
| Sentry | `djboost add sentry` | Error tracking and performance monitoring |
| Structured Logging | `djboost add logging` | Structlog with JSON output |
| OpenTelemetry | `djboost add monitoring` | Distributed tracing and metrics |

### Feature Dependency Graph

```
celery-beat  →  celery          (must have celery first)
kubernetes   →  docker          (must have docker first)
scheduler    ✕  celery-beat     (conflict — pick one)
cicd-github  ✕  cicd-gitlab    (conflict — pick one)
```

---

## 🔒 Safe Feature Lifecycle

Every `add` and `remove` command goes through a **safe engine** that makes operations deterministic and reversible.

### What the Safe Engine Does

1. **Scans project state** — detects which features are already enabled
2. **Resolves dependencies** — installs required features automatically
3. **Detects conflicts** — blocks incompatible feature combinations
4. **Checks reverse dependencies** — warns if other features depend on what you're removing
5. **Shows a dry-run plan** — preview all changes before applying
6. **Backs up files** — saves originals before modifying
7. **Validates** — runs Django checks after changes
8. **Auto-rollbacks** — reverts everything if validation fails

### Dry-Run Mode

Preview what a command would do without making any changes:

```bash
djboost add celery --dry-run          # Preview adding Celery
djboost remove docker --dry-run       # Preview removing Docker
djboost add redis-cache --dry-run     # Preview adding Redis Cache
```

Example output:
```
Add feature: celery DRY RUN

Packages to install:
  + celery>=5.4,<6
  + redis>=5.0,<6

Files to change:
  + core/celery.py (create)
  + core/tasks.py (create)
  ~ core/__init__.py (modify)
  ~ core/settings.py (modify)
  ~ requirements.txt (modify)
```

### Force Mode

Override conflict checks when you know what you're doing:

```bash
djboost remove celery --force         # Remove even if celery-beat depends on it
djboost add scheduler --force         # Add even if celery-beat is installed
```

### What Happens on Failure

If Django validation fails after changes, the safe engine automatically:
1. Restores all backed-up files
2. Removes any created files
3. Reverts package installs/uninstalls
4. Prints what was rolled back

---

## 📱 Creating Apps

### What

Use `djboost startapp` to scaffold a new Django app with a professional structure.

### Why

Django's built-in `startapp` gives you a flat, minimal structure. djboost creates an API-oriented layout that separates concerns and scales with your project.

### How

```bash
cd myproject
djboost startapp products
```

### Generated Structure

```
apps/products/
├── views/              ← View files (one per resource)
│   ├── __init__.py
│   └── products.py     ← List + Detail views
├── serializers/        ← Serializer files (one per resource)
│   ├── __init__.py
│   └── products.py     ← Detail + List serializers
├── service/            ← Business logic layer
│   ├── __init__.py
│   └── helpers.py      ← Helper functions
├── permissions.py      ← Custom permissions
├── tasks.py            ← Celery tasks (auto-detects if installed)
├── models.py           ← Model with UUID, user FK, timestamps
├── admin.py            ← Admin with list_display, filters
├── urls.py             ← URL patterns (list + detail)
├── apps.py             ← App config
└── tests.py            ← Smoke tests (model, URL, API)
```

### After Creating App

```bash
python manage.py makemigrations products
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Creating Accounts App

### What

`djboost startauth` generates a complete authentication system with email-based login, OTP verification, password reset, and profile management.

### How

```bash
djboost startauth
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/sign-up` | Register new user | No |
| POST | `/api/auth/verify-email` | Verify email with OTP | No |
| POST | `/api/auth/resend-code` | Resend verification code | No |
| POST | `/api/auth/sign-in` | Login with email/password | No |
| POST | `/api/auth/forgot-password` | Request password reset | No |
| POST | `/api/auth/verify-reset-code` | Verify reset code | No |
| POST | `/api/auth/reset-password` | Reset password | No |
| POST | `/api/auth/refresh-token` | Refresh JWT token | No |
| POST | `/api/auth/social-login` | Social login (Google/Facebook/Apple) | No |
| POST | `/api/auth/change-password` | Change password | Yes |
| GET | `/api/auth/my-account` | Get profile | Yes |
| PUT | `/api/auth/my-account` | Update profile | Yes |

---

## 🔧 Project Management

### Commands

```bash
djboost doctor                     # Check project health
djboost validate                   # Validate project structure
djboost info                       # Show project info and modules
djboost features                   # List all available features
```

### `djboost features`

Shows all 17 features and whether each is enabled:

```
┌──────────┬─────────────────────┬───────────────────────────────────────────┬──────────────┐
│  Status  │ Feature             │ Description                               │ Dependencies │
├──────────┼─────────────────────┼───────────────────────────────────────────┼──────────────┤
│    ✅    │ Celery              │ Background task processing with Redis      │ —            │
│    ○     │ Celery Beat         │ Periodic task scheduler                   │ celery       │
│    ○     │ APScheduler         │ Lightweight in-process job scheduler      │ —            │
│    ○     │ Docker              │ Containerization with Docker Compose      │ —            │
│    ○     │ Kubernetes          │ K8s deployment manifests                  │ docker       │
│    ○     │ PostgreSQL          │ PostgreSQL database backend               │ —            │
│    ○     │ Redis Cache         │ Redis-backed caching and sessions         │ —            │
│    ○     │ API Documentation   │ Swagger UI and ReDoc                      │ —            │
│    ○     │ GraphQL             │ Strawberry GraphQL API                    │ —            │
│    ○     │ Django Channels     │ WebSocket and async protocol support      │ —            │
│    ○     │ GitHub Actions      │ GitHub Actions CI/CD pipeline             │ —            │
│    ○     │ GitLab CI           │ GitLab CI/CD pipeline                     │ —            │
│    ○     │ Cloud Storage       │ S3-compatible file storage                │ —            │
│    ○     │ Security Headers    │ CSP, HSTS, secure cookies                 │ —            │
│    ○     │ Sentry              │ Error tracking and performance monitoring │ —            │
│    ○     │ Structured Logging  │ Structlog with JSON output                │ —            │
│    ○     │ OpenTelemetry       │ Distributed tracing and metrics           │ —            │
└──────────┴─────────────────────┴───────────────────────────────────────────┴──────────────┘
```

### `djboost doctor`

Checks your project health:
- ✅ Django configuration
- ✅ Database configuration
- ✅ Environment variables
- ✅ Required packages
- ✅ Common package
- ✅ Apps directory
- ⚠️ DEBUG mode
- ⚠️ SECRET_KEY security

### `djboost validate`

Validates project structure integrity:
- ✅ INSTALLED_APPS configuration
- ✅ REST_FRAMEWORK settings
- ✅ Security headers
- ✅ CORS configuration
- ✅ JWT configuration
- ✅ Common package files
- ✅ URL patterns

---

## 📊 Response Format

### Success Response

```json
{
    "success": true,
    "message": "Data retrieved successfully.",
    "data": [...]
}
```

### Paginated Response

```json
{
    "success": true,
    "message": "Data retrieved successfully.",
    "data": [...],
    "meta": {
        "count": 100,
        "total_pages": 10,
        "current_page": 1,
        "page_size": 10
    }
}
```

### Error Response

```json
{
    "success": false,
    "message": "Invalid email or password.",
    "data": null,
    "errors": {
        "email": ["This field is required."]
    }
}
```

### Usage in Views

```python
from common.responses import success_response, error_response
from common.pagination import CustomPagination
from apps.products.serializers import ProductSerializer

# Success response
def list_products(request):
    products = Product.objects.all()
    return success_response(
        message="Products retrieved",
        data=ProductSerializer(products, many=True).data
    )

# Error response
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(message="Validation failed", errors=serializer.errors)

# Paginated response
def list_products(request):
    paginator = CustomPagination()
    return paginator.paginate_data(
        queryset=Product.objects.all(),
        request=request,
        serializer_class=ProductSerializer,
    )
```

---

## 🏃 Running Your Project

### Without Docker

```bash
python manage.py migrate
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Health check |
| `http://127.0.0.1:8000/admin/` | Django Admin |
| `http://127.0.0.1:8000/api/schema/swagger-ui` | Swagger UI (if added) |
| `http://127.0.0.1:8000/api/schema/redoc` | ReDoc (if added) |
| `http://127.0.0.1:8000/graphql` | GraphQL (if added) |

### With Docker

```bash
docker-compose up --build
```

### With Celery

```bash
# Terminal 1 — Django
python manage.py runserver

# Terminal 2 — Celery Worker
celery -A core worker -l info

# Terminal 3 — Celery Beat (optional)
celery -A core beat -l info
```

### With Kubernetes

```bash
# Edit k8s/secrets.yaml with real credentials
# Edit k8s/ingress.yaml with your domain
kubectl apply -f k8s/
```

---

## 📋 Dependencies

### Essential (installed with `startproject`)

| Package | Version | Purpose |
|---------|---------|---------|
| Django | >=4.2,<7 | Web framework (4.2 LTS, 5.x, 6.x) |
| djangorestframework | >=3.15,<4 | REST API |
| djangorestframework-simplejwt | >=5.3,<6 | JWT authentication |
| django-cors-headers | >=4.3,<6 | CORS configuration |
| python-decouple | >=3.8,<4 | Environment variables |
| Pillow | >=10.0,<13 | Image handling |
| drf-spectacular | >=0.27,<1 | OpenAPI/Swagger support |
| whitenoise | >=6.6,<8 | Static file serving |
| pytest | >=7.4,<9 | Testing framework |
| pytest-django | >=4.7,<6 | Django test integration |
| pytest-cov | >=4.1,<7 | Test coverage |
| black | >=23.0,<26 | Code formatting |
| flake8 | >=6.0,<9 | Linting |
| isort | >=5.12,<7 | Import sorting |

### Optional (add only when needed)

| Command | Packages Installed |
|---------|--------------------|
| `djboost add celery` | celery>=5.4,<6, redis>=5.0,<6 |
| `djboost add docker` | gunicorn>=21.2,<23 |
| `djboost add postgres` | psycopg2-binary>=2.9,<3 |
| `djboost add redis-cache` | django-redis>=5.4,<6, redis>=5.0,<6 |
| `djboost add storage` | django-storages[boto3]>=1.14,<2, boto3>=1.28,<2 |
| `djboost add graphql` | strawberry-graphql[django]>=0.22,<1 |
| `djboost add channels` | daphne>=4.1,<5, channels>=4.1,<5, channels-redis>=4.2,<5 |
| `djboost add security` | django-csp>=3.8,<4, django-feature-policy>=3.1,<4 |
| `djboost add sentry` | sentry-sdk[django]>=2.0,<3 |
| `djboost add logging` | structlog>=24.0,<25, python-json-logger>=2.0,<3 |
| `djboost add monitoring` | opentelemetry-api>=1.25,<2, opentelemetry-sdk>=1.25,<2, opentelemetry-exporter-otlp>=1.25,<2, opentelemetry-instrumentation-django>=0.46b0,<1, opentelemetry-instrumentation-requests>=0.46b0,<1, opentelemetry-instrumentation-dbapi>=0.46b0,<1 |
| `djboost add scheduler` | django-apscheduler>=0.7,<1 |

---

## 📖 CLI Reference

```
djboost --version                  Show version
djboost --help                     Show help

# Create
djboost startproject [NAME]       Create new project (default: core)
djboost startapp NAME             Create standard app
djboost startauth               Create full auth system

# Add (all support --dry-run and --force)
djboost add celery                 Add Celery worker
djboost add celery-beat            Add Celery Beat scheduler
djboost add scheduler              Add APScheduler (alternative to Beat)
djboost add docker                 Add Docker configuration
djboost add kubernetes             Add Kubernetes manifests
djboost add postgres               Add PostgreSQL backend
djboost add redis-cache            Add Redis caching
djboost add api-docs [swagger|redoc|both]  Add API documentation
djboost add graphql                Add GraphQL API
djboost add channels               Add Django Channels (WebSocket)
djboost add cicd github|gitlab     Add CI/CD pipeline
djboost add storage                Add S3 cloud storage
djboost add security               Add security headers (CSP, HSTS)
djboost add sentry                 Add Sentry error tracking
djboost add logging                Add structured logging
djboost add monitoring             Add OpenTelemetry tracing

# Remove (all support --dry-run and --force)
djboost remove celery              Remove Celery
djboost remove celery-beat         Remove Celery Beat
djboost remove scheduler           Remove APScheduler
djboost remove docker              Remove Docker
djboost remove kubernetes          Remove Kubernetes
djboost remove postgres            Remove PostgreSQL (revert to SQLite)
djboost remove redis-cache         Remove Redis Cache
djboost remove api-docs            Remove Swagger/ReDoc
djboost remove graphql             Remove GraphQL
djboost remove channels            Remove Channels
djboost remove cicd github|gitlab  Remove CI/CD
djboost remove storage             Remove Cloud Storage
djboost remove security            Remove Security Headers
djboost remove sentry              Remove Sentry
djboost remove logging             Remove Structured Logging
djboost remove monitoring          Remove OpenTelemetry

# Project Management
djboost features                   List all features and their status
djboost doctor                     Check project health
djboost validate                   Validate project structure
djboost info                       Show project info and modules
```

---

## 🐛 Troubleshooting

### `UnicodeEncodeError` on Windows

If you see emoji encoding errors on Windows, set UTF-8 mode:

```bash
set PYTHONIOENCODING=utf-8
djboost features
```

Or add to your environment variables permanently.

### `manage.py not found`

Make sure you're in the **project root** directory (where `manage.py` lives):

```bash
ls manage.py    # must exist
djboost doctor  # check project health
```

### `virtual environment not activated`

djboost requires an active virtual environment:

```bash
# Windows
env\Scripts\activate

# Mac / Linux
source env/bin/activate
```

### Feature already enabled

```bash
# Check what's enabled
djboost features

# Force re-apply if needed
djboost add celery --force
```

### Undo changes

The safe engine auto-backs up files. If something goes wrong:

```bash
# Remove the feature (restores backed-up files)
djboost remove celery

# Preview without removing
djboost remove celery --dry-run
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `python -m pytest tests/ -v`
4. Commit your changes: `git commit -m "Add amazing feature"`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/munjurdev/djboost.git
cd djboost
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -e ".[dev]"
python -m pytest tests/ -v
```

### Adding a New Feature to djboost

1. Register in `djboost/generators/features.py`
2. Create generator in `djboost/generators/`
3. Create add/remove commands in `djboost/commands/add/` and `djboost/commands/remove/`
4. Add tests in `tests/`
5. Update README.md

---

## 📋 Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13, 3.14)
- Virtual environment (djboost will warn you if not activated)

---

## 📄 License

MIT — [Munjur Alom](https://github.com/munjurdev)
