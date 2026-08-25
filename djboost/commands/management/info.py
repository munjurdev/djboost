"""djboost info — show project information and installed modules."""

import sys
from pathlib import Path
from rich import print
from rich.console import Console
from rich.table import Table


def info_command():
    """Show project information and installed modules."""
    console = Console()

    print("\n[bold green]📋 djboost info — Project Information[/bold green]\n")

    # 1. Check manage.py
    if not Path("manage.py").exists():
        print("[red]Error: manage.py not found. Are you in project root?[/red]")
        return

    # 2. Find project name
    import re

    settings_files = list(Path(".").glob("*/settings.py"))
    if not settings_files:
        print("[red]Error: settings.py not found.[/red]")
        return

    settings_path = settings_files[0]
    project_name = settings_path.parent.name

    # 3. djboost version
    try:
        from djboost import __version__

        djboost_version = __version__
    except ImportError:
        djboost_version = "unknown"

    # 4. Get installed package versions
    packages = {}
    try:
        import django

        packages["Django"] = django.VERSION[:3]
    except ImportError:
        packages["Django"] = "not installed"

    try:
        import rest_framework

        packages["DRF"] = rest_framework.VERSION
    except ImportError:
        packages["DRF"] = "not installed"

    try:
        import rest_framework_simplejwt

        packages["SimpleJWT"] = rest_framework_simplejwt.VERSION
    except ImportError:
        packages["SimpleJWT"] = "not installed"

    try:
        import celery

        packages["Celery"] = celery.__version__
    except ImportError:
        packages["Celery"] = "not installed"

    try:
        import channels

        packages["Channels"] = channels.__version__
    except ImportError:
        packages["Channels"] = "not installed"

    try:
        import drf_spectacular

        packages["drf-spectacular"] = drf_spectacular.VERSION
    except ImportError:
        packages["drf-spectacular"] = "not installed"

    # 5. Print project info
    print(f"[bold cyan]Project:[/bold cyan] {project_name}")
    print(f"[bold cyan]Python:[/bold cyan] {sys.version.split()[0]}")
    print(f"[bold cyan]djboost:[/bold cyan] {djboost_version}")
    print()

    # 6. Package versions table
    table = Table(title="Installed Packages")
    table.add_column("Package", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Status")

    for pkg, version in packages.items():
        if version == "not installed":
            table.add_row(pkg, "—", "ℹ️ Not installed")
        else:
            table.add_row(pkg, str(version), "✅ Installed")

    console.print(table)
    print()

    # 7. Detected modules
    print("[bold cyan]Detected Modules:[/bold cyan]\n")

    modules = []

    # Check Celery
    if (settings_path.parent / "celery.py").exists():
        modules.append(("✅", "Celery", "Worker configured"))
    else:
        modules.append(("ℹ️", "Celery", "Not configured"))

    # Check Celery Beat
    settings_content = settings_path.read_text(encoding="utf-8")
    if "CELERY_BEAT_SCHEDULE" in settings_content:
        modules.append(("✅", "Celery Beat", "Scheduler configured"))
    else:
        modules.append(("ℹ️", "Celery Beat", "Not configured"))

    # Check Docker
    if Path("docker-compose.yml").exists():
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")
        services = []
        for svc in ["web", "db", "redis", "celery", "celery-beat", "flower"]:
            if svc in compose:
                services.append(svc)
        modules.append(("✅", "Docker", f"Services: {', '.join(services)}"))
    else:
        modules.append(("ℹ️", "Docker", "Not configured"))

    # Check API Docs
    urls_files = list(Path(".").glob("*/urls.py"))
    for urls_file in urls_files:
        urls_content = urls_file.read_text(encoding="utf-8")
        if "SpectacularSwaggerView" in urls_content:
            modules.append(("✅", "API Docs (Swagger)", "Configured"))
        if "SpectacularRedocView" in urls_content:
            modules.append(("✅", "API Docs (ReDoc)", "Configured"))

    # Check CI/CD
    if Path(".github/workflows/main.yml").exists():
        modules.append(("✅", "CI/CD", "GitHub Actions"))
    elif Path(".gitlab-ci.yml").exists():
        modules.append(("✅", "CI/CD", "GitLab CI"))
    else:
        modules.append(("ℹ️", "CI/CD", "Not configured"))

    # Check Accounts app
    if Path("apps/accounts").exists():
        modules.append(("✅", "Accounts", "Auth system installed"))
    else:
        modules.append(("ℹ️", "Accounts", "Not created"))

    # Check apps
    apps_dir = Path("apps")
    if apps_dir.exists():
        apps = [d.name for d in apps_dir.iterdir() if d.is_dir() and (d / "apps.py").exists() and d.name != "accounts"]
        if apps:
            modules.append(("✅", "Apps", ", ".join(apps)))

    table2 = Table(title="Modules")
    table2.add_column("Status", justify="center", style="bold")
    table2.add_column("Module", style="cyan")
    table2.add_column("Details")

    for status, module, details in modules:
        table2.add_row(status, module, details)

    console.print(table2)
    print()
