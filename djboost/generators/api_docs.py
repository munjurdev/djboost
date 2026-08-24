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


def add_spectacular_to_installed_apps(name: str):
    """Add drf-spectacular to INSTALLED_APPS in settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    # Check if already installed
    if "drf_spectacular" in content:
        print("[yellow]Warning: drf-spectacular already in INSTALLED_APPS. Skipping.[/yellow]")
        return True

    # Add to INSTALLED_APPS
    content = content.replace("'rest_framework',", "'rest_framework',\n    'drf_spectacular',")

    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added drf-spectacular to INSTALLED_APPS[/green]")
    return True


def add_spectacular_settings(name: str):
    """Add Spectacular settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    # Check if already configured
    if "SPECTACULAR_SETTINGS" in content:
        print("[yellow]Warning: SPECTACULAR_SETTINGS already in settings.py. Skipping.[/yellow]")
        return True

    # Add Spectacular settings
    spectacular_settings = """

# ── Swagger / ReDoc ───────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Documentation',
    'DESCRIPTION': 'Project API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Update REST_FRAMEWORK to use Spectacular as schema class
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
"""

    content += spectacular_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Spectacular settings to {name}/settings.py[/green]")
    return True


def generate_api_docs_urls(name: str):
    """Generate API documentation URLs."""
    urls_path = Path(f"{name}/urls.py")
    if not urls_path.exists():
        print(f"[red]Error: {name}/urls.py not found.[/red]")
        return False

    content = urls_path.read_text(encoding="utf-8")

    # Check if already configured
    if "SpectacularAPIView" in content:
        print("[yellow]Warning: API docs URLs already configured. Skipping.[/yellow]")
        return True

    # Add imports
    content = content.replace(
        "from django.urls import path",
        """from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView""",
    )

    # Add API docs URLs
    api_docs_urls = """
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),"""

    content = content.replace("urlpatterns = [", f"urlpatterns = [{api_docs_urls}")

    urls_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added API docs URLs to {name}/urls.py[/green]")
    return True


def add_spectacular_to_requirements():
    """Add drf-spectacular to requirements.txt if not present."""
    requirements_path = Path("requirements.txt")

    existing_packages = []
    if requirements_path.exists():
        existing_content = requirements_path.read_text(encoding="utf-8")
        existing_packages = existing_content.lower()

    packages_to_add = []
    if "drf-spectacular" not in existing_packages:
        packages_to_add.append("drf-spectacular>=0.27,<1")

    if packages_to_add:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for package in packages_to_add:
                f.write(f"{package}\n")
        print(f"[green]✔ Added drf-spectacular to requirements.txt[/green]")
    else:
        print("[yellow]Warning: drf-spectacular already in requirements.txt. Skipping.[/yellow]")
