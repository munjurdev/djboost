"""Standard app structure generator — creates beautiful, production-ready app layout."""
import os
from pathlib import Path
from rich import print


def create_standard_app_structure(app_name: str):
    """Create standard app directory structure."""
    
    # Create directories
    dirs = [
        f"apps/{app_name}",
        f"apps/{app_name}/views",
        f"apps/{app_name}/serializers",
        f"apps/{app_name}/service",
        f"apps/{app_name}/migrations",
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        init_path = Path(d) / "__init__.py"
        if not init_path.exists():
            init_path.touch()
    
    print(f"[green]✔ Created directory structure for apps/{app_name}[/green]")


def create_app_views(app_name: str):
    """Create views/ directory with __init__.py and example views."""
    
    # views/__init__.py
    init_content = f"""from apps.{app_name}.views.{app_name} import (
    {app_name.capitalize()}ListView,
    {app_name.capitalize()}DetailView,
)
"""
    Path(f"apps/{app_name}/views/__init__.py").write_text(init_content, encoding="utf-8")
    
    # views/{app_name}.py
    view_content = f"""from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class {app_name.capitalize()}ListView(APIView):
    \"\"\"List all {app_name}s.\"\"\"
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implement list logic
        return Response({{"success": True, "message": "List {app_name}s"}})


class {app_name.capitalize()}DetailView(APIView):
    \"\"\"Get, update, or delete a {app_name}.\"\"\"
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # TODO: Implement detail logic
        return Response({{"success": True, "message": f"Detail {app_name} {{pk}}"}})

    def put(self, request, pk):
        # TODO: Implement update logic
        return Response({{"success": True, "message": f"Update {app_name} {{pk}}"}})

    def delete(self, request, pk):
        # TODO: Implement delete logic
        return Response({{"success": True, "message": f"Delete {app_name} {{pk}}"}})
"""
    Path(f"apps/{app_name}/views/{app_name}.py").write_text(view_content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/views/[/green]")


def create_app_serializers(app_name: str):
    """Create serializers/ directory with __init__.py and example serializers."""
    
    # serializers/__init__.py
    init_content = f"""from apps.{app_name}.serializers.{app_name} import (
    {app_name.capitalize()}Serializer,
    {app_name.capitalize()}ListSerializer,
)
"""
    Path(f"apps/{app_name}/serializers/__init__.py").write_text(init_content, encoding="utf-8")
    
    # serializers/{app_name}.py
    serializer_content = f"""from rest_framework import serializers
# from apps.{app_name}.models import {app_name.capitalize()}


class {app_name.capitalize()}Serializer(serializers.ModelSerializer):
    \"\"\"Serializer for {app_name} detail view.\"\"\"
    
    class Meta:
        # model = {app_name.capitalize()}
        fields = '__all__'


class {app_name.capitalize()}ListSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for {app_name} list view (lighter version).\"\"\"
    
    class Meta:
        # model = {app_name.capitalize()}
        fields = ['id', 'name', 'created_at']
"""
    Path(f"apps/{app_name}/serializers/{app_name}.py").write_text(serializer_content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/serializers/[/green]")


def create_app_permissions(app_name: str):
    """Create permissions.py with standard permission classes."""
    
    content = f"""from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    \"\"\"Allow access only to the owner of the object.\"\"\"
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    \"\"\"Allow read-only for anyone, write only for admins.\"\"\"
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# Add custom permissions here as needed.
# Example:
# class CanManage{app_name.capitalize()}(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated
"""
    path = Path(f"apps/{app_name}/permissions.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/permissions.py[/green]")


def create_app_tasks(app_name: str):
    """Create tasks.py with Celery task template."""
    
    content = f'''"""
Celery background tasks for the {app_name} app.

Tasks are auto-discovered by Celery via autodiscover_tasks().
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={{"max_retries": 3}},
)
def sample_{app_name}_task(item_id):
    """
    Sample task - replace with your own logic.
    
    Args:
        item_id: ID of the item to process.
    """
    # TODO: Implement task logic
    logger.info(f"Processing {app_name} item: {{item_id}}")
    return f"Done: {{item_id}}"
'''
    path = Path(f"apps/{app_name}/tasks.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/tasks.py[/green]")


def create_app_service(app_name: str):
    """Create service/ directory for business logic."""
    
    # service/__init__.py
    init_content = f"""# Business logic for {app_name} app
# Keep complex logic here, not in views.
"""
    Path(f"apps/{app_name}/service/__init__.py").write_text(init_content, encoding="utf-8")
    
    # service/helpers.py
    helpers_content = f'''"""
Helper functions for {app_name} app.

Keep business logic here instead of views.
This makes code reusable and testable.
"""


def get_{app_name}_by_id(item_id):
    """Get {app_name} by ID."""
    # TODO: Implement
    pass


def validate_{app_name}_data(data):
    """Validate {app_name} data."""
    # TODO: Implement
    pass


def process_{app_name}(item):
    """Process {app_name} item."""
    # TODO: Implement
    pass
'''
    Path(f"apps/{app_name}/service/helpers.py").write_text(helpers_content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/service/[/green]")


def create_standard_urls(app_name: str):
    """Create urls.py with standard patterns."""
    
    content = f"""from django.urls import path
from apps.{app_name}.views import {app_name}

app_name = '{app_name}'

urlpatterns = [
    path('', {app_name}.{app_name.capitalize()}ListView.as_view(), name='list'),
    path('/<uuid:pk>/', {app_name}.{app_name.capitalize()}DetailView.as_view(), name='detail'),
]
"""
    path = Path(f"apps/{app_name}/urls.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/urls.py[/green]")


def create_standard_models(app_name: str):
    """Create models.py with standard model template."""
    
    import uuid
    
    content = f"""import uuid

from django.db import models
from django.conf import settings


class {app_name.capitalize()}(models.Model):
    \"\"\"
    {app_name.capitalize()} model.
    \"\"\"
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='{app_name}s',
        verbose_name='User',
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name='Name',
    )
    
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Description',
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active',
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '{app_name}s'
        ordering = ['-created_at']
        verbose_name = '{app_name.capitalize()}'
        verbose_name_plural = '{app_name.capitalize()}s'

    def __str__(self):
        return self.name
"""
    path = Path(f"apps/{app_name}/models.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/models.py[/green]")


def create_standard_admin(app_name: str):
    """Create admin.py with standard admin config."""
    
    content = f"""from django.contrib import admin
from apps.{app_name}.models import {app_name.capitalize()}


@admin.register({app_name.capitalize()})
class {app_name.capitalize()}Admin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
"""
    path = Path(f"apps/{app_name}/admin.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/admin.py[/green]")


def create_standard_apps(app_name: str):
    """Create apps.py with proper config."""
    
    content = f"""from django.apps import AppConfig


class {app_name.capitalize()}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{app_name}"
    verbose_name = "{app_name.capitalize()}"
"""
    path = Path(f"apps/{app_name}/apps.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/apps.py[/green]")


def create_standard_tests(app_name: str):
    """Create tests.py - fresh default Django test file."""
    
    content = """from django.test import TestCase

# Create your tests here.
"""
    path = Path(f"apps/{app_name}/tests.py")
    path.write_text(content, encoding="utf-8")
    
    print(f"[green]✔ Created apps/{app_name}/tests.py[/green]")


def generate_standard_app(app_name: str):
    """Main function to generate standard app structure."""
    
    print(f"\n[bold green]🚀 Creating standard app: {app_name}[/bold green]\n")
    
    # Create directories
    print("[cyan]📁 Creating directory structure...[/cyan]")
    create_standard_app_structure(app_name)
    
    # Create files
    print("[cyan]👁️  Creating views...[/cyan]")
    create_app_views(app_name)
    
    print("[cyan]📦 Creating serializers...[/cyan]")
    create_app_serializers(app_name)
    
    print("[cyan]🔐 Creating permissions...[/cyan]")
    create_app_permissions(app_name)
    
    print("[cyan]📋 Creating tasks...[/cyan]")
    create_app_tasks(app_name)
    
    print("[cyan]⚙️  Creating service layer...[/cyan]")
    create_app_service(app_name)
    
    print("[cyan]🔗 Creating URLs...[/cyan]")
    create_standard_urls(app_name)
    
    print("[cyan]📝 Creating models...[/cyan]")
    create_standard_models(app_name)
    
    print("[cyan]🛡️  Creating admin...[/cyan]")
    create_standard_admin(app_name)
    
    print("[cyan]⚙️  Creating app config...[/cyan]")
    create_standard_apps(app_name)
    
    print("[cyan]🧪 Creating tests...[/cyan]")
    create_standard_tests(app_name)
    
    print()
    print("[bold green]✅ Standard app created successfully![/bold green]")
    print()
    print("[cyan]Structure:[/cyan]")
    print(f"  apps/{app_name}/")
    print(f"    ├── views/           ← Multiple view files")
    print(f"    ├── serializers/     ← Multiple serializer files")
    print(f"    ├── service/         ← Business logic")
    print(f"    ├── permissions.py   ← Custom permissions")
    print(f"    ├── tasks.py         ← Celery tasks")
    print(f"    ├── models.py        ← Database models")
    print(f"    ├── admin.py         ← Admin config")
    print(f"    ├── urls.py          ← URL patterns")
    print(f"    ├── apps.py          ← App config")
    print(f"    └── tests.py         ← Tests")
    print()
    print("[cyan]Next steps:[/cyan]")
    print(f"  1. Run [bold]python manage.py makemigrations {app_name}[/bold]")
    print("  2. Run [bold]python manage.py migrate[/bold]")
    print("  3. Run [bold]python manage.py runserver[/bold]")
