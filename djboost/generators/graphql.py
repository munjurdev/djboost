"""GraphQL generator — add Strawberry GraphQL API to a Django project."""

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


def generate_graphql_schema(name: str):
    """Create the root GraphQL schema file."""
    schema_content = '''"""
Root GraphQL schema — define your types, queries, and mutations here.

Docs: https://strawberry.rocks/docs
"""
import strawberry
from strawberry.scalars import JSON


@strawberry.type
class Query:
    """Root query type."""

    @strawberry.field
    def health(self) -> str:
        """Health check endpoint."""
        return "ok"

    @strawberry.field
    def version(self) -> str:
        """Return the API version."""
        return "1.0.0"


@strawberry.type
class Mutation:
    """Root mutation type — add your mutations here."""
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
'''
    path = Path(f"{name}/schema.py")
    if path.exists():
        print(f"[yellow]Warning: {name}/schema.py already exists. Skipping.[/yellow]")
        return False
    path.write_text(schema_content, encoding="utf-8")
    print(f"[green]✔ Created {name}/schema.py[/green]")
    return True


def add_graphql_urls(name: str):
    """Add GraphQL endpoint to project urls.py."""
    urls_path = Path(f"{name}/urls.py")
    if not urls_path.exists():
        print(f"[red]Error: {name}/urls.py not found.[/red]")
        return False

    content = urls_path.read_text(encoding="utf-8")

    if "graphql" in content.lower() and "strawberry" in content.lower():
        print("[yellow]Warning: GraphQL URLs already configured. Skipping.[/yellow]")
        return True

    # Add imports
    content = content.replace(
        "from django.urls import path",
        "from django.urls import path\nfrom strawberry.django.views import GraphQLView",
    )

    # Add URL pattern
    content = content.replace(
        "urlpatterns = [",
        'urlpatterns = [\n    path("/graphql", GraphQLView.as_view(schema="{name}.schema.schema"), name="graphql"),'.format(
            name=name
        ),
    )

    urls_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added GraphQL endpoint to {name}/urls.py[/green]")
    return True


def add_graphql_settings(name: str):
    """Add Strawberry settings to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "STRAWBERRY" in content:
        print("[yellow]Warning: Strawberry already in settings. Skipping.[/yellow]")
        return True

    settings = """

# ── Strawberry GraphQL ─
STRAWBERRY = {{
    'DEBUG': DEBUG,
}}
"""
    content += settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added Strawberry settings to {name}/settings.py[/green]")
    return True


def add_graphql_to_requirements():
    """Add strawberry-graphql to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    if "strawberry" not in existing:
        with open(requirements_path, "a", encoding="utf-8") as f:
            f.write("strawberry-graphql[django]>=0.22,<1\n")
        print("[green]✔ Added strawberry-graphql to requirements.txt[/green]")
    else:
        print("[yellow]Warning: strawberry-graphql already in requirements.txt. Skipping.[/yellow]")
