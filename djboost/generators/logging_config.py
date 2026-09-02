"""Structured Logging generator — add structlog with JSON output."""

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


def generate_logging_config(name: str):
    """Create a logging_config.py with structlog setup."""
    config_content = '''"""
Structured logging configuration with structlog.

Usage:
    import structlog
    logger = structlog.get_logger()
    logger.info("user_logged_in", user_id=user.id, ip=request.META["REMOTE_ADDR"])
"""
import logging
import structlog


def setup_logging(log_level: str = "INFO", log_format: str = "json"):
    """Configure structlog and standard logging."""

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Quiet noisy loggers
    for name in ["django", "urllib3", "django.server"]:
        logging.getLogger(name).setLevel(logging.WARNING)
'''
    path = Path(f"{name}/logging_config.py")
    if path.exists():
        print(f"[yellow]Warning: {name}/logging_config.py already exists. Skipping.[/yellow]")
        return False
    path.write_text(config_content, encoding="utf-8")
    print(f"[green]✔ Created {name}/logging_config.py[/green]")
    return True


def add_logging_settings(name: str):
    """Add logging initialization to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "structlog" in content:
        print("[yellow]Warning: structlog already in settings. Skipping.[/yellow]")
        return True

    logging_settings = """

# ── Structured Logging ─
import os
from {name}.logging_config import setup_logging

LOG_LEVEL = config('LOG_LEVEL', default='INFO')
LOG_FORMAT = config('LOG_FORMAT', default='json')

setup_logging(log_level=LOG_LEVEL, log_format=LOG_FORMAT)
""".format(name=name)

    content += logging_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added logging config to {name}/settings.py[/green]")
    return True


def add_logging_to_requirements():
    """Add structlog to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    packages = []
    if "structlog" not in existing:
        packages.append("structlog>=24.0,<25")
    if "python-json-logger" not in existing:
        packages.append("python-json-logger>=2.0,<3")

    if packages:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for pkg in packages:
                f.write(pkg + "\n")
        print(f"[green]✔ Added {', '.join(packages)} to requirements.txt[/green]")
    else:
        print("[yellow]Warning: Logging packages already in requirements.txt. Skipping.[/yellow]")
