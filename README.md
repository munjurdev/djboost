# djboost 🚀

[![PyPI version](https://badge.fury.io/py/djboost.svg)](https://pypi.org/project/djboost/)
[![Python](https://img.shields.io/pypi/pyversions/djboost)](https://pypi.org/project/djboost/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A CLI-based Django project generator for quickly scaffolding production-oriented backend projects.**

djboost eliminates repetitive Django setup. Instead of manually installing packages, configuring settings, and writing boilerplate, one command gives you a complete project foundation — DRF, JWT, testing, code quality, security defaults, and more. Add Celery, Docker, API docs, or CI/CD anytime with modular `add`/`remove` commands.

```bash
pip install djboost
djboost create project myproject
```


---

## Table of Contents

- [Getting Started](#-getting-started)
- [What You Get by Default](#-what-you-get-by-default)
- [Project Structure](#-project-structure)
- [Creating Apps](#-creating-apps)
- [Creating Accounts App](#-creating-accounts-app)
- [Features You Can Add](#-features-you-can-add)
- [Features You Can Remove](#-features-you-can-remove)
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
djboost create project core
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

When you run `djboost create project core`, you get a complete foundation **without installing any optional packages**.

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

### What `create project` Generates

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

### Installed Packages (13 Essential)

| Package | Version | Purpose |
|---------|---------|---------|
| Django | >=4.2,<5 | Web framework |
| djangorestframework | >=3.14,<4 | REST API |
| djangorestframework-simplejwt | >=5.3,<6 | JWT authentication |
| django-cors-headers | >=4.3,<5 | CORS configuration |
| python-decouple | >=3.8,<4 | Environment variables |
| Pillow | >=10.0,<12 | Image handling |
| drf-spectacular | >=0.27,<1 | OpenAPI/Swagger support |
| whitenoise | >=6.6,<7 | Static file serving |
| pytest | >=7.4,<9 | Testing framework |
| pytest-django | >=4.7,<5 | Django test integration |
| pytest-cov | >=4.1,<6 | Test coverage |
| black | >=23.0,<25 | Code formatting |
| flake8 | >=6.0,<8 | Linting |
| isort | >=5.12,<6 | Import sorting |

### Settings Configuration

Your `settings.py` is pre-configured with:

```python
# Authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'core.utils.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.CustomPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {'anon': '100/day', 'user': '1000/day'},
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Environment Variables (.env)

```env
# Django
DEBUG=True
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS & CSRF
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:8000
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:8000

# Database (commented — uncomment for PostgreSQL)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=core_db
# DB_USER=core_user
# DB_PASSWORD=your-db-password

# Email
EMAIL_USE_SSL=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=465
```

---

## 📁 Project Structure

After `djboost create project core`:

```
myproject/
├── apps/                        ← Your Django apps
│   └── __init__.py
│
├── common/                      ← Shared utilities (NOT an app)
│   ├── __init__.py
│   ├── responses.py             ← success_response(), error_response()
│   ├── pagination.py            ← CustomPagination
│   └── exceptions.py            ← custom_exception_handler
│
├── core/                        ← Project config
│   ├── __init__.py
│   ├── settings.py              ← Django settings
│   ├── urls.py                  ← Root URLs
│   ├── utils.py                 ← Exception handler
│   ├── wsgi.py
│   └── asgi.py
│
├── static/                      ← Static files (CSS, JS, images)
├── media/                       ← User uploads
│
├── .env                         ← Environment variables
├── .gitignore                   ← Git ignore rules
├── .pre-commit-config.yaml      ← Code quality hooks
├── manage.py                    ← Django management command
├── pytest.ini                   ← Test configuration
└── requirements.txt             ← Dependencies
```

### Directory Purpose

| Directory | Purpose | When to Use |
|-----------|---------|-------------|
| `apps/` | All your Django apps | Always — create apps here |
| `common/` | Response helpers, pagination, exceptions | Import in views |
| `core/` | Settings, URLs, WSGI/ASGI | Project configuration |
| `static/` | CSS, JavaScript, images | Static assets |
| `media/` | User-uploaded files | File uploads |

---

## 📱 Creating Apps

### What

Use `djboost create app` to scaffold a new Django app with a professional structure.

### Why

Django's built-in `startapp` gives you a flat, minimal structure. djboost creates an API-oriented layout that separates concerns and scales with your project.

### How

```bash
cd myproject
djboost create app products
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

### Generated Code Examples

**Model** (`models.py`):
```python
import uuid
from django.db import models
from django.conf import settings

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

**Serializer** (`serializers/products.py`):
```python
from rest_framework import serializers
from apps.products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'is_active', 'created_at']
```

**Views** (`views/products.py`):
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProductListView(APIView):
    """List all products."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implement list logic
        return Response({"success": True, "message": "List products"})

class ProductDetailView(APIView):
    """Get, update, or delete a product."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        return Response({"success": True, "message": f"Detail product {pk}"})
```

**URLs** (`urls.py`):
```python
from django.urls import path
from apps.products.views import products

app_name = 'products'

urlpatterns = [
    path('', products.ProductListView.as_view(), name='list'),
    path('<uuid:pk>/', products.ProductDetailView.as_view(), name='detail'),
]
```

**Tests** (`tests.py`):
```python
from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework.test import APITestCase
from rest_framework import status
from apps.products.models import Product
from apps.products.views.products import ProductListView, ProductDetailView

class ProductModelTest(TestCase):
    def test_create_product(self):
        obj = Product.objects.create(name='Test Product')
        self.assertEqual(str(obj), 'Test Product')
        self.assertTrue(obj.is_active)

class ProductURLTest(TestCase):
    def test_list_url_resolves(self):
        url = reverse('apps.products:list')
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, ProductListView)

class ProductAPITest(APITestCase):
    def test_list_unauthenticated(self):
        url = reverse('apps.products:list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [401, 403])
```

### After Creating App

```bash
# 1. Create migrations
python manage.py makemigrations products

# 2. Apply migrations
python manage.py migrate

# 3. Run server
python manage.py runserver
```

---

## 🔐 Creating Accounts App

### What

`djboost create accounts` generates a complete authentication system with email-based login, OTP verification, password reset, and profile management.

### Why

Every project needs auth. Instead of building it from scratch each time, djboost gives you a working auth system that you can customize.

### How

```bash
djboost create accounts
```

### Generated Structure

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

## ➕ Features You Can Add

These features are **optional** — add them only when you need them.

---

### Add Celery (Background Tasks)

#### What

Celery handles background tasks — sending emails, processing data, generating reports — without blocking your API.

#### Why

Long-running tasks (email, PDF generation, data processing) slow down your API. Celery runs them in the background.

#### How

```bash
# Add Celery worker
djboost add celery

# Add Celery Beat scheduler (for periodic tasks)
djboost add celery-beat
```

#### What `add celery` Does

1. Installs `celery` + `redis` packages
2. Creates `core/celery.py` — Celery app configuration
3. Creates `core/tasks.py` — sample tasks
4. Updates `core/__init__.py` — registers Celery app
5. Updates `settings.py` — adds `CELERY_BROKER_URL`

#### What `add celery-beat` Does

1. Adds `crontab` import to `settings.py`
2. Adds `CELERY_BEAT_SCHEDULE` configuration

#### After Adding

```bash
# Run Celery worker
celery -A core worker -l info

# Run Celery Beat (for periodic tasks)
celery -A core beat -l info
```

---

### Add Docker

#### What

Docker packages your app and all its services (database, cache, workers) into containers that run anywhere.

#### Why

"Works on my machine" problem disappears. Docker ensures your app runs the same in development, staging, and production.

#### How

```bash
djboost add docker
```

#### What `add docker` Does

1. Generates `Dockerfile`
2. Generates `docker-compose.yml` with **feature-aware** services
3. Generates `.dockerignore`
4. Installs additional packages if needed (flower, gunicorn)

#### Feature-Aware Services

Docker only includes services for packages you have installed:

| Your Setup | Docker Services |
|-----------|----------------|
| Base project only | web, db, redis |
| + Celery | web, db, redis, celery, celery-beat, flower |
| + Channels | web (daphne), db, redis |
| + Celery + Channels | web (daphne), db, redis, celery, celery-beat, flower |

#### Running with Docker

```bash
docker-compose up --build
```

---

### Add API Documentation

#### What

Swagger UI and ReDoc provide interactive API documentation where developers can explore and test your endpoints.

#### Why

Self-documenting APIs reduce communication overhead. Frontend developers can see all endpoints without asking.

#### How

```bash
# Add Swagger UI only
djboost add api-docs swagger

# Add ReDoc only
djboost add api-docs redoc

# Add both
djboost add api-docs both
```

#### What `add api-docs` Does

1. Adds imports to `urls.py`
2. Adds URL patterns:
   - `/api/schema/` — OpenAPI schema
   - `/api/schema/swagger-ui/` — Swagger UI
   - `/api/schema/redoc/` — ReDoc

#### After Adding

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/schema/swagger-ui/` | Interactive Swagger UI |
| `http://localhost:8000/api/schema/redoc/` | Clean ReDoc documentation |

---

### Add CI/CD

#### What

CI/CD pipelines automatically run tests and checks every time you push code.

#### Why

Catches bugs before they reach production. No more "it works on my computer" — CI verifies every push.

#### How

```bash
# GitHub Actions
djboost add cicd github

# GitLab CI
djboost add cicd gitlab
```

#### What `add cicd github` Does

1. Creates `.github/workflows/main.yml`
2. Runs on push/PR to `main` branch
3. Tests on Python 3.10, 3.11, 3.12
4. Installs dependencies, runs flake8 lint, runs pytest

#### What `add cicd gitlab` Does

1. Creates `.gitlab-ci.yml`
2. Runs on `main` branch and merge requests
3. Uses Python 3.11 image
4. Installs dependencies, runs flake8 lint, runs pytest

---

## 🔧 Project Management

### What

`doctor`, `validate`, and `info` commands help you check and understand your project.

### Why

Keep your project healthy and catch issues early.

### How

```bash
# Check project health
djboost doctor

# Validate project structure
djboost validate

# Show project info
djboost info
```

#### `djboost doctor`

Checks your project health:
- ✅ Django configuration
- ✅ Database configuration
- ✅ Environment variables
- ✅ Required packages
- ✅ Common package
- ✅ Apps directory
- ⚠️ DEBUG mode
- ⚠️ SECRET_KEY security

#### `djboost validate`

Validates project structure integrity:
- ✅ INSTALLED_APPS configuration
- ✅ REST_FRAMEWORK settings
- ✅ Security headers
- ✅ CORS configuration
- ✅ JWT configuration
- ✅ Common package files
- ✅ URL patterns (no leading slash bug)
- ❌ Missing files
- ❌ Broken configuration

#### `djboost info`

Shows project information:
- 📋 Project name and Python version
- 📦 Installed package versions
- 🧩 Detected modules (Celery, Docker, CI/CD, etc.)

---

## ➖ Features You Can Remove

Remove features you no longer need — djboost cleans up everything.

---

### Remove Celery

#### What

Completely removes Celery from your project — packages, files, and configuration.

#### Why

If you switch to a different task queue or don't need background tasks anymore.

#### How

```bash
djboost remove celery
```

#### What `remove celery` Does

1. **Uninstalls** `celery` + `redis` packages
2. Removes `core/celery.py` and `core/tasks.py`
3. Removes Celery configuration from `settings.py`
4. Removes Celery from `requirements.txt`

---

### Remove Celery Beat

#### What

Removes Celery Beat scheduler configuration.

#### How

```bash
djboost remove celery-beat
```

#### What `remove celery-beat` Does

1. Removes `crontab` import from `settings.py`
2. Removes `CELERY_BEAT_SCHEDULE` from `settings.py`

---

### Remove Docker

#### What

Removes all Docker configuration files.

#### How

```bash
djboost remove docker
```

#### What `remove docker` Does

1. Removes `Dockerfile`
2. Removes `docker-compose.yml`
3. Removes `.dockerignore`
4. Removes flower/gunicorn from `requirements.txt`

---

### Remove API Docs

#### What

Removes Swagger/ReDoc documentation from your project.

#### How

```bash
djboost remove api-docs
```

#### What `remove api-docs` Does

1. Removes Swagger/ReDoc imports from `urls.py`
2. Removes `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` URLs
3. Removes `drf-spectacular` from `requirements.txt`

---

### Remove CI/CD

#### What

Removes CI/CD pipeline configuration files.

#### Why

If you switch to a different CI/CD platform or don't need automated testing.

#### How

```bash
# Remove GitHub Actions
djboost remove cicd github

# Remove GitLab CI
djboost remove cicd gitlab
```

#### What `remove cicd` Does

- `djboost remove cicd github` — removes `.github/` directory
- `djboost remove cicd gitlab` — removes `.gitlab-ci.yml`

---

## 📊 Response Format

### What

All API responses follow a consistent JSON format.

### Why

Frontend developers know exactly what to expect. No guessing whether `data` is an object, array, or nested.

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
    # ... create product

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
| `http://127.0.0.1:8000/api/schema/swagger-ui/` | Swagger UI (if added) |
| `http://127.0.0.1:8000/api/schema/redoc/` | ReDoc (if added) |

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

---

## 📋 Dependencies

### Essential (installed with `create project`)

| Package | Version | Purpose |
|---------|---------|---------|
| Django | >=4.2,<5 | Web framework |
| djangorestframework | >=3.14,<4 | REST API |
| djangorestframework-simplejwt | >=5.3,<6 | JWT authentication |
| django-cors-headers | >=4.3,<5 | CORS configuration |
| python-decouple | >=3.8,<4 | Environment variables |
| Pillow | >=10.0,<12 | Image handling |
| drf-spectacular | >=0.27,<1 | OpenAPI/Swagger support |
| whitenoise | >=6.6,<7 | Static file serving |
| pytest | >=7.4,<9 | Testing framework |
| pytest-django | >=4.7,<5 | Django test integration |
| pytest-cov | >=4.1,<6 | Test coverage |
| black | >=23.0,<25 | Code formatting |
| flake8 | >=6.0,<8 | Linting |
| isort | >=5.12,<6 | Import sorting |

### Optional (add only when needed)

| Command | Packages Installed |
|---------|--------------------|
| `djboost add celery` | celery>=5.3,<6, redis>=5.0,<6 |
| `djboost add docker` | flower>=2.0,<3 (if Celery installed), gunicorn>=21.2,<23 (if no Daphne) |

---

## 📖 CLI Reference

```
djboost --version                  Show version
djboost --help                     Show help

# Create
djboost create project [NAME]      Create new project (default: core)
djboost create app NAME            Create standard app
djboost create accounts            Create full auth system

# Add
djboost add cicd github|gitlab     Add CI/CD pipeline
djboost add celery                 Add Celery worker
djboost add celery-beat            Add Celery Beat scheduler
djboost add docker                 Add Docker configuration
djboost add api-docs swagger|redoc|both  Add API documentation

# Remove
djboost remove cicd github|gitlab  Remove CI/CD pipeline
djboost remove celery              Remove Celery + uninstall packages
djboost remove celery-beat         Remove Celery Beat scheduler
djboost remove docker              Remove Docker configuration
djboost remove api-docs            Remove Swagger/ReDoc documentation

# Project Management
djboost doctor                     Check project health
djboost validate                   Validate project structure
djboost info                       Show project info and modules
```

---

## 📋 Requirements

- Python 3.10+
- Virtual environment (djboost will warn you if not activated)

---

## 📄 License

MIT — [Munjur Alom](https://github.com/munjurdev)
