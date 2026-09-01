"""
API Documentation generator (Swagger / ReDoc).
"""

import re
from pathlib import Path

from rich import print

from djboost.generators.safe_engine import FileChange


def get_project_name():  # type: ignore[no-untyped-def]
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


def add_spectacular_to_installed_apps(name: str):  # type: ignore[no-untyped-def]
    """Add rest_framework to INSTALLED_APPS if not present."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return
    content = settings_path.read_text(encoding="utf-8")
    if "rest_framework" not in content:
        content = content.replace(
            "INSTALLED_APPS = [",
            'INSTALLED_APPS = [\n    "rest_framework",',
        )
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Added rest_framework to INSTALLED_APPS[/green]")
    if "drf_spectacular" not in content:
        content = settings_path.read_text(encoding="utf-8")
        content = content.replace(
            "INSTALLED_APPS = [",
            'INSTALLED_APPS = [\n    "drf_spectacular",',
        )
        settings_path.write_text(content, encoding="utf-8")
        print("[green]✔ Added drf_spectacular to INSTALLED_APPS[/green]")


def add_spectacular_settings(name: str):  # type: ignore[no-untyped-def]
    """Add drf-spectacular settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return
    content = settings_path.read_text(encoding="utf-8")
    if "SPECTACULAR_SETTINGS" in content:
        print("[yellow]⚠ SPECTACULAR_SETTINGS already exists in settings.py[/yellow]")
        return
    spectacular_settings = (
        "\n# ── API Documentation (drf-spectacular) ─────────────────────────────────\n"
        "SPECTACULAR_SETTINGS = {\n"
        f'    "TITLE": "{name.title()} API",\n'
        '    "DESCRIPTION": "API documentation",\n'
        '    "VERSION": "1.0.0",\n'
        '    "SERVE_INCLUDE_SCHEMA": False,\n'
        '    "SWAGGER_UI_SETTINGS": {\n'
        '        "deepLinking": True,\n'
        '        "filter": True,\n'
        "    },\n"
        '    "TAGS": [],\n'
        "}\n"
    )
    content += spectacular_settings
    settings_path.write_text(content, encoding="utf-8")
    print("[green]✔ Added SPECTACULAR_SETTINGS to settings.py[/green]")


def generate_api_docs_urls(name: str):  # type: ignore[no-untyped-def]
    """Add API documentation URL patterns to urls.py."""
    urls_path = Path(f"{name}/urls.py")
    if not urls_path.exists():
        print(f"[red]Error: {name}/urls.py not found.[/red]")
        return
    content = urls_path.read_text(encoding="utf-8")
    if "api/schema" in content:
        print("[yellow]⚠ API docs URLs already exist in urls.py[/yellow]")
        return
    content = content.replace(
        "from django.urls import path",
        "from django.urls import path, include",
    )
    doc_url = (
        '\n    path("/api/schema", SpectacularAPIView.as_view(), name="schema"),\n'
        '    path("/api/schema/swagger-ui", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),\n'
        '    path("/api/schema/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),\n'
    )
    content = content.replace(
        "urlpatterns = [",
        "from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView\n\nurlpatterns = ["
        + doc_url,
    )
    urls_path.write_text(content, encoding="utf-8")
    print("[green]✔ Added API documentation URLs to urls.py[/green]")


def add_spectacular_to_requirements():  # type: ignore[no-untyped-def]
    """Add drf-spectacular to requirements.txt."""
    req_path = Path("requirements.txt")
    packages = ["drf-spectacular>=0.27,<1", "uritemplate>=4.1,<5"]
    existing = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
    added = []
    for pkg in packages:
        name = pkg.split(">=")[0].split("<")[0].split("==")[0]
        if name not in existing:
            with open("requirements.txt", "a", encoding="utf-8") as f:
                f.write(f"{pkg}\n")
            added.append(pkg)
    if added:
        print(f"[green]✔ Added to requirements.txt: {', '.join(added)}[/green]")


def generate_api_docs_files(name: str, doc_type: str = "both"):  # type: ignore[no-untyped-def]
    """Generate API documentation files for the project."""
    changes = []
    if doc_type in ("swagger", "both"):
        changes.extend(_generate_spectacular_files(name))
    if doc_type in ("redoc", "both"):
        changes.extend(_generate_redoc_files(name))
    changes.extend(_update_url_patterns(name))
    changes.extend(_update_settings(name, doc_type))
    return changes


def _generate_spectacular_files(name: str):  # type: ignore[no-untyped-def]
    """Generate drf-spectacular configuration."""
    content = (
        "# Auto-generated API schema configuration\n"
        "from drf_spectacular.openapi import AutoSchema\n"
        "\n"
        "\n"
        "class CustomAutoSchema(AutoSchema):\n"
        '    """Custom schema class for drf-spectacular."""\n'
        "\n"
        "    def get_tags(self, path, method):  # type: ignore[no-untyped-def]\n"
        '        """Return tags based on path prefix."""\n'
        '        path_parts = path.strip("/").split("/")\n'
        '        if len(path_parts) >= 2 and path_parts[0] == "api":\n'
        "            return [path_parts[1].title()]\n"
        '        return ["default"]\n'
    )
    return [FileChange(path=f"{name}/schemas.py", content=content, action="create")]


def _generate_redoc_files(name: str):  # type: ignore[no-untyped-def]
    """Generate ReDoc configuration."""
    content = (
        "# ReDoc configuration\n"
        "REDOC_SETTINGS = {\n"
        '    "SPEC_URL": ["/api/schema", "yaml"],\n'
        '    "HIDE_HOSTNAME": True,\n'
        '    "NATIVE_SCROLLBAR": True,\n'
        '    "FOOTER": "",\n'
        "}\n"
    )
    return [FileChange(path=f"{name}/redoc_config.py", content=content, action="create")]


def _update_url_patterns(name: str):  # type: ignore[no-untyped-def]
    """Add API documentation URL patterns."""
    content = (
        "# Auto-generated URL patterns for API documentation\n"
        "from django.urls import path\n"
        "from drf_spectacular.views import (\n"
        "    SpectacularAPIView,\n"
        "    SpectacularSwaggerView,\n"
        "    SpectacularRedocView,\n"
        ")\n"
        "\n"
        "urlpatterns = [\n"
        '    path("/api/schema", SpectacularAPIView.as_view(), name="schema"),\n'
        '    path("/api/schema/swagger-ui", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),\n'
        '    path("/api/schema/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),\n'
        "]\n"
    )
    return [FileChange(path=f"{name}/urls_docs.py", content=content, action="create")]


def _update_settings(name: str, doc_type: str):  # type: ignore[no-untyped-def]
    """Add API documentation settings."""
    lines = [
        "# ── API Documentation (drf-spectacular) ─────────────────────────────────",
        "SPECTACULAR_SETTINGS = {",
        f'    "TITLE": "{name.title()} API",',
        '    "DESCRIPTION": "API documentation",',
        '    "VERSION": "1.0.0",',
        '    "SERVE_INCLUDE_SCHEMA": False,',
        '    "SWAGGER_UI_SETTINGS": {',
        '        "deepLinking": True,',
        '        "filter": True,',
        "    },",
        '    "TAGS": [],',
        "}",
    ]
    if doc_type in ("redoc", "both"):
        lines.extend(
            [
                "",
                "# ReDoc settings",
                "REDOC_SETTINGS = {",
                '    "HIDE_HOSTNAME": True,',
                "}",
            ]
        )

    return [FileChange(path=f"{name}/settings_docs.py", content="\n".join(lines), action="create")]
