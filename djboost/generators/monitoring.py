"""OpenTelemetry generator — add distributed tracing and metrics."""

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


def generate_telemetry(name: str):
    """Create the telemetry.py configuration file."""
    telemetry_content = '''"""
OpenTelemetry configuration — call init_telemetry() early in wsgi.py or asgi.py.

Usage in wsgi.py:
    from {name}.telemetry import init_telemetry
    init_telemetry()
"""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def init_telemetry():
    """Initialize OpenTelemetry tracing with OTLP exporter."""
    service_name = os.environ.get("OTEL_SERVICE_NAME", "{name}")
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    resource = Resource.create({{
        SERVICE_NAME: service_name,
    }})

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Auto-instrument Django
    try:
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        DjangoInstrumentor().instrument()
    except ImportError:
        pass

    # Auto-instrument HTTP requests
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        RequestsInstrumentor().instrument()
    except ImportError:
        pass
'''.format(name=name)

    path = Path(f"{name}/telemetry.py")
    if path.exists():
        print(f"[yellow]Warning: {name}/telemetry.py already exists. Skipping.[/yellow]")
        return False
    path.write_text(telemetry_content, encoding="utf-8")
    print(f"[green]✔ Created {name}/telemetry.py[/green]")
    return True


def add_monitoring_settings(name: str):
    """Add OpenTelemetry settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "OTEL_SERVICE_NAME" in content:
        print("[yellow]Warning: OpenTelemetry already in settings. Skipping.[/yellow]")
        return True

    settings = """

# ── OpenTelemetry ─
OTEL_SERVICE_NAME = config('OTEL_SERVICE_NAME', default='{name}')
OTEL_EXPORTER_OTLP_ENDPOINT = config('OTEL_EXPORTER_OTLP_ENDPOINT', default='http://localhost:4317')
""".format(name=name)

    content += settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added OpenTelemetry settings to {name}/settings.py[/green]")
    return True


def add_monitoring_to_wsgi(name: str):
    """Add telemetry init to wsgi.py."""
    wsgi_path = Path(f"{name}/wsgi.py")
    if not wsgi_path.exists():
        return False

    content = wsgi_path.read_text(encoding="utf-8")

    if "telemetry" in content:
        print("[yellow]Warning: Telemetry already in wsgi.py. Skipping.[/yellow]")
        return True

    content = content.replace(
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE',",
        "from {name}.telemetry import init_telemetry\ninit_telemetry()\n\nos.environ.setdefault('DJANGO_SETTINGS_MODULE',".format(
            name=name
        ),
    )

    wsgi_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added telemetry init to {name}/wsgi.py[/green]")
    return True


def add_monitoring_to_requirements():
    """Add OpenTelemetry packages to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    packages = [
        "opentelemetry-api>=1.25,<2",
        "opentelemetry-sdk>=1.25,<2",
        "opentelemetry-exporter-otlp>=1.25,<2",
        "opentelemetry-instrumentation-django>=0.46b0,<1",
        "opentelemetry-instrumentation-requests>=0.46b0,<1",
    ]

    to_add = [
        p
        for p in packages
        if p.split(">=")[0].split("<")[0].strip().lower().replace("-", "_") not in existing.replace("-", "_")
    ]

    if to_add:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for pkg in to_add:
                f.write(pkg + "\n")
        print(f"[green]✔ Added {len(to_add)} OpenTelemetry packages to requirements.txt[/green]")
    else:
        print("[yellow]Warning: OpenTelemetry packages already in requirements.txt. Skipping.[/yellow]")
