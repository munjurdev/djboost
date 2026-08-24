"""Cloud Storage generator — add S3-compatible file storage with django-storages."""
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


def update_settings_storage(name: str):
    """Add S3 storage config to settings.py."""
    settings_path = Path(f"{name}/settings.py")
    if not settings_path.exists():
        print(f"[red]Error: {name}/settings.py not found.[/red]")
        return False

    content = settings_path.read_text(encoding="utf-8")

    if "AWS_STORAGE_BUCKET_NAME" in content:
        print("[yellow]Warning: S3 storage already configured. Skipping.[/yellow]")
        return True

    storage_settings = """

# ── S3 / Cloud Storage ────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {{'CacheControl': 'max-age=86400'}}
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

STORAGES = {{
    'default': {{
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    }},
    'staticfiles': {{
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    }},
}}
"""
    content += storage_settings
    settings_path.write_text(content, encoding="utf-8")
    print(f"[green]✔ Added S3 storage config to {name}/settings.py[/green]")
    return True


def update_env_storage(name: str):
    """Update .env with S3 variables."""
    env_path = Path(".env")
    if not env_path.exists():
        return False

    content = env_path.read_text(encoding="utf-8")

    if "AWS_ACCESS_KEY_ID" in content:
        print("[yellow]Warning: AWS vars already in .env. Skipping.[/yellow]")
        return True

    s3_env = """
# ── S3 / Cloud Storage ────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=
"""
    content += s3_env
    env_path.write_text(content, encoding="utf-8")
    print("[green]✔ Added S3 vars to .env[/green]")
    return True


def add_storage_to_requirements():
    """Add django-storages and boto3 to requirements.txt."""
    requirements_path = Path("requirements.txt")
    existing = ""
    if requirements_path.exists():
        existing = requirements_path.read_text(encoding="utf-8").lower()

    packages = []
    if "django-storages" not in existing:
        packages.append("django-storages[boto3]>=1.14,<2")
    if "boto3" not in existing:
        packages.append("boto3>=1.28,<2")

    if packages:
        with open(requirements_path, "a", encoding="utf-8") as f:
            for pkg in packages:
                f.write(pkg + "\n")
        print(f"[green]✔ Added {', '.join(packages)} to requirements.txt[/green]")
    else:
        print("[yellow]Warning: Storage packages already in requirements.txt. Skipping.[/yellow]")
