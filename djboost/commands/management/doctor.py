"""djboost doctor — check project health and configuration."""

import os
import sys
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table


def doctor_command():
    """Check project health and configuration."""
    console = Console()

    print("\n[bold green]🏥 djboost doctor — Project Health Check[/bold green]\n")

    checks = []

    # 1. Check manage.py exists
    if Path("manage.py").exists():
        checks.append(("✅", "manage.py", "Found"))
    else:
        checks.append(("❌", "manage.py", "Not found — are you in project root?"))

    # 2. Check settings.py
    settings_files = list(Path(".").glob("*/settings.py"))
    if settings_files:
        checks.append(("✅", "settings.py", f"Found at {settings_files[0]}"))
    else:
        checks.append(("❌", "settings.py", "Not found"))

    # 3. Check .env
    if Path(".env").exists():
        env_content = Path(".env").read_text(encoding="utf-8")
        if "DEBUG=True" in env_content:
            checks.append(("⚠️", ".env — DEBUG", "DEBUG=True (not safe for production)"))
        elif "DEBUG=False" in env_content:
            checks.append(("✅", ".env — DEBUG", "DEBUG=False (production safe)"))
        else:
            checks.append(("✅", ".env — DEBUG", "Configured"))

        if "SECRET_KEY=your-secret-key" in env_content or "SECRET_KEY=your-generated-secret" in env_content:
            checks.append(("⚠️", ".env — SECRET_KEY", "Default value — change for production"))
        else:
            checks.append(("✅", ".env — SECRET_KEY", "Custom value set"))
    else:
        checks.append(("❌", ".env", "Not found — create one"))

    # 4. Check requirements.txt
    if Path("requirements.txt").exists():
        req_content = Path("requirements.txt").read_text(encoding="utf-8").lower()

        # Core packages
        for pkg in [
            "djangorestframework",
            "simplejwt",
            "corsheaders",
            "drf-spectacular",
        ]:
            if pkg in req_content:
                checks.append(("✅", f"Package: {pkg}", "Installed"))
            else:
                checks.append(("⚠️", f"Package: {pkg}", "Not found"))

        # Optional packages
        if "celery" in req_content:
            checks.append(("✅", "Package: celery", "Installed"))
        else:
            checks.append(("ℹ️", "Package: celery", "Not installed (optional)"))

        if "redis" in req_content:
            checks.append(("✅", "Package: redis", "Installed"))
        else:
            checks.append(("ℹ️", "Package: redis", "Not installed (optional)"))

        if "channels" in req_content:
            checks.append(("✅", "Package: channels", "Installed"))
        else:
            checks.append(("ℹ️", "Package: channels", "Not installed (optional)"))

        if "flower" in req_content:
            checks.append(("✅", "Package: flower", "Installed"))
        else:
            checks.append(("ℹ️", "Package: flower", "Not installed (optional)"))
    else:
        checks.append(("❌", "requirements.txt", "Not found"))

    # 5. Check common package
    if Path("common/__init__.py").exists():
        checks.append(("✅", "common/ package", "Found"))
        for f in ["responses.py", "pagination.py", "exceptions.py"]:
            if Path(f"common/{f}").exists():
                checks.append(("✅", f"common/{f}", "Found"))
            else:
                checks.append(("⚠️", f"common/{f}", "Missing"))
    else:
        checks.append(("❌", "common/ package", "Not found"))

    # 6. Check apps directory
    if Path("apps/__init__.py").exists():
        apps = [d.name for d in Path("apps").iterdir() if d.is_dir() and (d / "apps.py").exists()]
        if apps:
            checks.append(("✅", "apps/", f"Found: {', '.join(apps)}"))
        else:
            checks.append(("ℹ️", "apps/", "Empty — no apps created yet"))
    else:
        checks.append(("❌", "apps/", "Not found"))

    # 7. Check Docker
    if Path("docker-compose.yml").exists():
        checks.append(("✅", "Docker", "docker-compose.yml found"))
        compose_content = Path("docker-compose.yml").read_text(encoding="utf-8")
        services = []
        for svc in ["web", "db", "redis", "celery", "celery-beat", "flower"]:
            if svc in compose_content:
                services.append(svc)
        checks.append(("ℹ️", "Docker services", ", ".join(services)))
    else:
        checks.append(("ℹ️", "Docker", "Not configured (run: djboost add docker)"))

    # 8. Check CI/CD
    if Path(".github/workflows/main.yml").exists():
        checks.append(("✅", "CI/CD", "GitHub Actions configured"))
    elif Path(".gitlab-ci.yml").exists():
        checks.append(("✅", "CI/CD", "GitLab CI configured"))
    else:
        checks.append(("ℹ️", "CI/CD", "Not configured (run: djboost add cicd github)"))

    # 9. Check API docs
    urls_file = None
    for f in Path(".").glob("*/urls.py"):
        if f.name == "urls.py":
            urls_file = f
            break
    if urls_file:
        urls_content = urls_file.read_text(encoding="utf-8")
        if "SpectacularSwaggerView" in urls_content:
            checks.append(("✅", "API Docs", "Swagger UI configured"))
        elif "SpectacularRedocView" in urls_content:
            checks.append(("✅", "API Docs", "ReDoc configured"))
        else:
            checks.append(("ℹ️", "API Docs", "Not configured (run: djboost add api-docs)"))

    # 10. Check Celery files
    settings_dir = settings_files[0].parent if settings_files else None
    if settings_dir:
        if (settings_dir / "celery.py").exists():
            checks.append(("✅", "Celery config", f"{settings_dir}/celery.py found"))
        else:
            checks.append(("ℹ️", "Celery config", "Not configured (run: djboost add celery)"))

    # 11. Check .pre-commit-config.yaml
    if Path(".pre-commit-config.yaml").exists():
        checks.append(("✅", "Pre-commit", "Configured"))
    else:
        checks.append(("⚠️", "Pre-commit", "Not found"))

    # 12. Check .gitignore
    if Path(".gitignore").exists():
        checks.append(("✅", ".gitignore", "Found"))
    else:
        checks.append(("⚠️", ".gitignore", "Not found"))

    # Print results
    table = Table(title="Project Health Report")
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Result")

    for status, check, result in checks:
        table.add_row(status, check, result)

    console.print(table)

    # Summary
    passed = sum(1 for s, _, _ in checks if s == "✅")
    warnings = sum(1 for s, _, _ in checks if s == "⚠️")
    failed = sum(1 for s, _, _ in checks if s == "❌")
    info = sum(1 for s, _, _ in checks if s == "ℹ️")

    print()
    print(f"[bold green]✅ Passed: {passed}[/bold green]  ", end="")
    if warnings:
        print(f"[bold yellow]⚠️ Warnings: {warnings}[/bold yellow]  ", end="")
    if failed:
        print(f"[bold red]❌ Failed: {failed}[/bold red]  ", end="")
    print(f"[cyan]ℹ️ Info: {info}[/cyan]")
    print()
