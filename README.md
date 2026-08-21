# djboost 🚀

[![PyPI version](https://badge.fury.io/py/djboost.svg)](https://pypi.org/project/djboost/)
[![Python](https://img.shields.io/pypi/pyversions/djboost)](https://pypi.org/project/djboost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**One command. Production-ready Django REST API.**

`djboost` generates a fully-configured Django REST API project in seconds — DRF, JWT, pagination, standard response format, and more. Add Celery, Docker, Swagger anytime with `djboost add`. No boilerplate. No config hunting.

```bash
pip install djboost
djboost create project myproject
```

That's it. Your project is ready.

---

## ✨ What you get

| Feature | Details |
|---|---|
| **REST API** | Django REST Framework + Simple JWT pre-configured |
| **API Docs** | Swagger UI + ReDoc at `/api/schema/swagger-ui/` |
| **Async Tasks** | Celery + Redis (add only when needed) |
| **WebSockets** | Django Channels + Daphne ASGI server |
| **Database** | PostgreSQL config ready (SQLite default for dev) |
| **Environment** | `python-decouple` with fully pre-filled `.env` |
| **Docker** | `Dockerfile` + `docker-compose.yml` with 6 services |
| **Security** | CORS, CSRF, XSS headers, throttling all configured |
| **Static Files** | Whitenoise for efficient static file serving |
| **Code Quality** | `pre-commit` with `black`, `flake8`, `isort` |
| **Testing** | `pytest` + `pytest-django` with coverage |
| **CI/CD** | GitHub Actions and GitLab CI pipelines |
| **Exception Handler** | Global DRF handler → `{"success": false, "message": "..."}` |
| **Response Format** | Standard success/error/pagination format |
| **Pagination** | Custom pagination with meta info |
| **Modular CLI** | Add/remove features anytime with `djboost add` |

---

## 🚀 Quick Start

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
2. Configure `settings.py` with production-ready settings
3. Generate `.env` pre-filled with all required keys
4. Set up `pytest.ini`, `.pre-commit-config.yaml`, `.gitignore`
5. Install only 13 essential dependencies (add more later as needed)
6. Create `apps/common/service/` with response helpers and pagination
7. Freeze `requirements.txt`

---

## 📱 Creating Apps

```bash
cd myproject
djboost create app users
```

This creates a **standard app structure**:

```
apps/users/
├── views/           ← Multiple view files (not single file)
│   ├── __init__.py
│   └── users.py     ← List + Detail views
├── serializers/     ← Multiple serializer files
│   ├── __init__.py
│   └── users.py     ← Detail + List serializers
├── service/         ← Business logic layer
│   ├── __init__.py
│   └── helpers.py   ← Helper functions
├── permissions.py   ← Custom permissions (IsOwner, IsAdminOrReadOnly)
├── tasks.py         ← Celery tasks template
├── models.py        ← Standard model with UUID, user, timestamps
├── admin.py         ← Admin config with list_display, filters
├── urls.py          ← Standard URL patterns
├── apps.py          ← App config (name = 'apps.users')
└── tests.py         ← Fresh default Django test file
```

---

## 🔐 Creating Accounts App (Full Auth System)

Create a complete accounts app with all auth APIs ready:

```bash
djboost create accounts
```

This creates a production-ready accounts module:

```
apps/accounts/
├── models.py           ← Custom User (email login), EmailOTP, AdminSectionPermission
├── permissions.py      ← IsSuperAdmin, IsAdmin, HasSectionAccess, IsOwner
├── tasks.py            ← Celery tasks for OTP emails, admin invitations
├── views/
│   ├── auth.py         ← SignUp, SignIn, VerifyEmail, SocialLogin, RefreshToken
│   ├── password.py     ← ForgotPassword, ResetPassword, ChangePassword
│   └── profile.py      ← MyAccount (GET/PUT)
├── serializers/
│   ├── auth.py         ← SignUp, SignIn, VerifyEmail, SocialLogin
│   ├── password.py     ← ForgotPassword, ResetPassword, ChangePassword
│   └── profile.py      ← UserProfile
├── urls.py             ← All auth endpoints
├── admin.py            ← User admin with role management
├── apps.py
├── tests.py
└── migrations/
```

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/sign-up` | Register new user |
| POST | `/api/auth/verify-email` | Verify email with OTP |
| POST | `/api/auth/resend-code` | Resend verification code |
| POST | `/api/auth/sign-in` | Login with email/password |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/verify-reset-code` | Verify reset code |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/refresh-token` | Refresh JWT token |
| POST | `/api/auth/social-login` | Social login (Google/Facebook/Apple) |
| POST | `/api/auth/change-password` | Change password (authenticated) |
| GET | `/api/auth/my-account` | Get profile (authenticated) |
| PUT | `/api/auth/my-account` | Update profile (authenticated) |

---

## 📋 CI/CD Pipelines

Add or remove CI/CD any time — it's modular.

```bash
djboost add cicd github    # GitHub Actions
djboost add cicd gitlab    # GitLab CI

djboost remove cicd github
djboost remove cicd gitlab
```

---

## ⚡ Adding Celery

Add Celery to your existing Django project:

```bash
djboost add celery          # Add Celery worker
djboost add celery-beat     # Add Celery Beat scheduler
```

This will:
1. Install `celery` + `redis` packages
2. Generate `celery.py` and `tasks.py` in your project
3. Update `settings.py` with Celery configuration
4. Update `requirements.txt`

### Removing Celery

```bash
djboost remove celery
```

This will:
1. **Uninstall** `celery` + `redis` packages
2. Remove `celery.py` and `tasks.py` files
3. Remove Celery configuration from `settings.py`
4. Remove Celery from `requirements.txt`

---

## 🐳 Adding Docker

Add Docker configuration to your existing Django project:

```bash
djboost add docker
```

This will:
1. Generate `Dockerfile`
2. Generate `docker-compose.yml` with 6 services:
   - `web` - Django application
   - `db` - PostgreSQL database
   - `redis` - Redis cache/broker
   - `celery` - Celery worker
   - `celery-beat` - Celery Beat scheduler
   - `flower` - Celery monitoring dashboard
3. Generate `.dockerignore`
4. Install `flower` package

---

## 📚 Adding API Documentation

Add Swagger/ReDoc API documentation:

```bash
djboost add api-docs swagger    # Add Swagger UI
djboost add api-docs redoc      # Add ReDoc
djboost add api-docs both       # Add both
```

After adding, access your API docs at:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

---

## 📊 Response Format

All responses follow a consistent format:

**Success Response:**
```json
{
    "success": true,
    "message": "Data retrieved successfully.",
    "data": [...]
}
```

**Paginated Response:**
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

**Error Response:**
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
from apps.common.service.responses import success_response, error_response
from apps.common.service.pagination import CustomPagination

# Success response
return success_response(message="User created", data=user_data)

# Error response
return error_response(message="Invalid credentials", status_code=401)

# Pagination
paginator = CustomPagination()
return paginator.paginate_data(
    queryset=users,
    request=request,
    serializer_class=UserSerializer,
)
```

---

## 🏃 Running Your Project

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

---

## 📖 CLI Reference

```
djboost --version                  # Show version
djboost --help                     # Show help

# Create commands
djboost create project [NAME]      # Create new Django project (default: core)
djboost create app NAME            # Create standard app with directory structure
djboost create accounts            # Create full accounts app with auth APIs

# Add commands
djboost add cicd github|gitlab     # Add CI/CD pipeline
djboost add celery                 # Add Celery worker + packages
djboost add celery-beat            # Add Celery Beat scheduler
djboost add docker                 # Add Docker configuration
djboost add api-docs swagger|redoc|both  # Add API documentation

# Remove commands
djboost remove cicd github|gitlab  # Remove CI/CD pipeline
djboost remove celery              # Remove Celery + uninstall packages
```

---

## 📦 Dependencies

**Essential (installed with create project):**
- Django REST Framework + Simple JWT
- django-cors-headers, python-decouple, Pillow
- drf-spectacular, whitenoise
- pytest, black, flake8, isort

**Optional (add only when needed):**
- `djboost add celery` → celery, redis
- `djboost add docker` → flower

---

## 📋 Requirements

- Python 3.10+
- Virtual environment (djboost will warn you if not activated)

---

## 📄 License

MIT — [Munjur Alom](https://github.com/munjurdev)
