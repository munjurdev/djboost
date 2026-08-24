"""djboost validate — validate project structure and configuration."""

import os
import re
import sys
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table


def validate_command():
    """Validate project structure and configuration integrity."""
    console = Console()

    print("\n[bold green]🔍 djboost validate — Structure Integrity Check[/bold green]\n")

    issues = []

    # 1. Check manage.py
    if not Path("manage.py").exists():
        issues.append(("❌", "manage.py", "Missing — not a Django project"))
        print("[red]Cannot validate without manage.py. Run this from project root.[/red]")
        return

    # 2. Find settings file
    settings_files = list(Path(".").glob("*/settings.py"))
    if not settings_files:
        issues.append(("❌", "settings.py", "Missing"))
    else:
        settings_path = settings_files[0]
        settings_content = settings_path.read_text(encoding="utf-8")
        project_name = settings_path.parent.name

        # Check INSTALLED_APPS
        if "INSTALLED_APPS" in settings_content:
            issues.append(("✅", "INSTALLED_APPS", "Defined"))

            # Check essential packages
            essential = ["corsheaders", "rest_framework", "drf_spectacular"]
            for pkg in essential:
                if pkg in settings_content:
                    issues.append(("✅", f"INSTALLED_APPS.{pkg}", "Present"))
                else:
                    issues.append(("❌", f"INSTALLED_APPS.{pkg}", "Missing"))

            # Check optional packages NOT in base
            optional_in_base = ["channels", "daphne"]
            for pkg in optional_in_base:
                if f"'{pkg}'" in settings_content or f'"{pkg}"' in settings_content:
                    issues.append(
                        (
                            "⚠️",
                            f"INSTALLED_APPS.{pkg}",
                            "Optional package in base settings",
                        )
                    )
        else:
            issues.append(("❌", "INSTALLED_APPS", "Missing"))

        # Check REST_FRAMEWORK
        if "REST_FRAMEWORK" in settings_content:
            issues.append(("✅", "REST_FRAMEWORK", "Defined"))

            if "EXCEPTION_HANDLER" in settings_content:
                issues.append(("✅", "REST_FRAMEWORK.EXCEPTION_HANDLER", "Configured"))
            else:
                issues.append(("⚠️", "REST_FRAMEWORK.EXCEPTION_HANDLER", "Missing"))

            if "DEFAULT_PAGINATION_CLASS" in settings_content:
                issues.append(("✅", "REST_FRAMEWORK.DEFAULT_PAGINATION_CLASS", "Configured"))
            else:
                issues.append(("⚠️", "REST_FRAMEWORK.DEFAULT_PAGINATION_CLASS", "Missing"))
        else:
            issues.append(("❌", "REST_FRAMEWORK", "Missing"))

        # Check SECURITY settings
        security_checks = [
            ("SECURE_BROWSER_XSS_FILTER", "XSS Filter"),
            ("SECURE_CONTENT_TYPE_NOSNIFF", "Content-Type Nosniff"),
            ("X_FRAME_OPTIONS", "X-Frame-Options"),
        ]
        for setting, name in security_checks:
            if setting in settings_content:
                issues.append(("✅", f"Security.{name}", "Configured"))
            else:
                issues.append(("⚠️", f"Security.{name}", "Missing"))

        # Check CORS
        if "CORS_ALLOWED_ORIGINS" in settings_content:
            issues.append(("✅", "CORS", "Configured"))
        else:
            issues.append(("⚠️", "CORS", "Not configured"))

        # Check JWT
        if "SIMPLE_JWT" in settings_content:
            issues.append(("✅", "JWT", "Configured"))
            if "ROTATE_REFRESH_TOKENS" in settings_content:
                issues.append(("✅", "JWT.RefreshRotation", "Enabled"))
            if "BLACKLIST_AFTER_ROTATION" in settings_content:
                issues.append(("✅", "JWT.Blacklist", "Enabled"))
        else:
            issues.append(("⚠️", "JWT", "Not configured"))

        # Check ASGI/WSGI
        if "ASGI_APPLICATION" in settings_content:
            issues.append(("✅", "ASGI", "Configured"))
        else:
            issues.append(("ℹ️", "ASGI", "Not configured"))

    # 3. Check common package
    common_dir = Path("common")
    if common_dir.exists():
        issues.append(("✅", "common/", "Directory exists"))

        expected_files = [
            "__init__.py",
            "responses.py",
            "pagination.py",
            "exceptions.py",
        ]
        for f in expected_files:
            if (common_dir / f).exists():
                issues.append(("✅", f"common/{f}", "Present"))
            else:
                issues.append(("❌", f"common/{f}", "Missing"))
    else:
        issues.append(("❌", "common/", "Missing"))

    # 4. Check apps directory
    apps_dir = Path("apps")
    if apps_dir.exists():
        issues.append(("✅", "apps/", "Directory exists"))
        if (apps_dir / "__init__.py").exists():
            issues.append(("✅", "apps/__init__.py", "Present"))
        else:
            issues.append(("❌", "apps/__init__.py", "Missing"))
    else:
        issues.append(("❌", "apps/", "Missing"))

    # 5. Check .env
    if Path(".env").exists():
        issues.append(("✅", ".env", "Present"))
    else:
        issues.append(("❌", ".env", "Missing"))

    # 6. Check requirements.txt
    if Path("requirements.txt").exists():
        req = Path("requirements.txt").read_text(encoding="utf-8").lower()
        issues.append(("✅", "requirements.txt", "Present"))

        # Check essential packages are frozen
        for pkg in ["django", "djangorestframework", "simplejwt"]:
            if pkg in req:
                issues.append(("✅", f"requirements.{pkg}", "Frozen"))
            else:
                issues.append(("⚠️", f"requirements.{pkg}", "Not frozen"))
    else:
        issues.append(("❌", "requirements.txt", "Missing"))

    # 7. Check URL structure
    urls_files = list(Path(".").glob("*/urls.py"))
    if urls_files:
        for urls_file in urls_files:
            urls_content = urls_file.read_text(encoding="utf-8")
            # Check for leading slash bug
            if "path('/" in urls_content:
                issues.append(("❌", f"{urls_file}", "Contains leading slash in URL pattern"))
            else:
                issues.append(("✅", f"{urls_file}", "URL patterns OK"))

    # 8. Check for circular imports in common/
    if common_dir.exists():
        for f in common_dir.glob("*.py"):
            content = f.read_text(encoding="utf-8")
            if f.name != "__init__.py":
                if "from common." in content and f.name in content:
                    issues.append(("⚠️", f"common/{f.name}", "Potential circular import"))

    # Print results
    table = Table(title="Validation Report")
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Result")

    for status, check, result in issues:
        table.add_row(status, check, result)

    console.print(table)

    # Summary
    passed = sum(1 for s, _, _ in issues if s == "✅")
    warnings = sum(1 for s, _, _ in issues if s == "⚠️")
    failed = sum(1 for s, _, _ in issues if s == "❌")
    info = sum(1 for s, _, _ in issues if s == "ℹ️")

    print()
    print(f"[bold green]✅ Passed: {passed}[/bold green]  ", end="")
    if warnings:
        print(f"[bold yellow]⚠️ Warnings: {warnings}[/bold yellow]  ", end="")
    if failed:
        print(f"[bold red]❌ Failed: {failed}[/bold red]  ", end="")
    print(f"[cyan]ℹ️ Info: {info}[/cyan]")
    print()

    if failed:
        print("[red]❌ Fix failed checks before deploying![/red]")
    elif warnings:
        print("[yellow]⚠️ Review warnings — some may need attention.[/yellow]")
    else:
        print("[green]✅ All checks passed![/green]")
    print()
