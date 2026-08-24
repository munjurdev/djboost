"""Security Headers generator — add CSP, HSTS, and security middleware."""

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


def update_settings_security(name: str):
    """Add security headers to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "CSP_DEFAULT_SRC" in content:
        print("[yellow]Warning: Security headers already configured. Skipping.[/yellow]")
        return True

    # Add django-csp middleware
    if "csp.middleware.CSPMiddleware" not in content:
        content = content.replace(
            "MIDDLEWARE = [",
            "MIDDLEWARE = [\n    'csp.middleware.CSPMiddleware',",
        )

    security_settings = """

# ── Security Headers ───────────────────────────────────────────────────────────
# Content Security Policy (django-csp)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("'none'",)
CSP_OBJECT_SRC = ("'none'",)

# HSTS (enable in production)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

# Additional security headers
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
"""
    content += security_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added security headers to {name}/settings.py[/green]")
    return True


def add_security_to_requirements():
    """Add security packages to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    packages = []
    if "django-csp" not in existing:
        packages.append("django-csp>=3.8,<4")

    if packages:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for pkg in packages:
                f.write(pkg + "\n")
        print(f"[green]✔ Added {', '.join(packages)} to requirements.txt[/green]")
    else:
        print("[yellow]Warning: Security packages already in requirements.txt. Skipping.[/yellow]")
