"""
Test fixtures for djboost integration tests.

Each test gets a fresh temporary directory with a real Django project
created by djboost's create command.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Capture the real Python executable at import time, before any test
# can mutate sys.executable via check_virtual_environment().
_REAL_PYTHON = sys.executable


@pytest.fixture
def temp_dir():
    """Create a temporary directory and clean up after."""
    original_dir = os.getcwd()
    tmp = tempfile.mkdtemp(prefix="djboost_test_")
    os.chdir(tmp)
    yield Path(tmp)
    os.chdir(original_dir)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def djboost_project(temp_dir):
    """
    Create a real Django project using djboost's create command.
    Returns the project path.
    """
    # Create a minimal Django project using django-admin directly
    # (faster than going through djboost CLI which installs packages)
    project_name = "testproject"

    # Install Django first
    subprocess.run(
        [_REAL_PYTHON, "-m", "pip", "install", "Django", "-q"],
        capture_output=True, text=True,
    )

    # Create project structure
    subprocess.run(
        [_REAL_PYTHON, "-m", "django", "startproject", project_name, "."],
        capture_output=True, text=True,
    )

    # Create required directories
    (temp_dir / "apps").mkdir(exist_ok=True)
    (temp_dir / "apps" / "__init__.py").touch()
    (temp_dir / "common").mkdir(exist_ok=True)
    (temp_dir / "common" / "__init__.py").touch()
    (temp_dir / "static").mkdir(exist_ok=True)
    (temp_dir / "media").mkdir(exist_ok=True)

    # Create manage.py marker (djboost checks for this)
    assert (temp_dir / "manage.py").exists()

    # Create a minimal requirements.txt
    (temp_dir / "requirements.txt").write_text(
        "Django>=4.2,<7\n",
        encoding="utf-8",
    )

    # Create .env
    (temp_dir / ".env").write_text(
        "DEBUG=True\nSECRET_KEY=test-secret-key-for-testing\n",
        encoding="utf-8",
    )

    return temp_dir


@pytest.fixture
def djboost_project_with_settings(djboost_project):
    """
    Create a Django project with settings that include the packages
    djboost expects (DRF, JWT, CORS, etc.).
    """
    settings_path = djboost_project / "testproject" / "settings.py"
    content = settings_path.read_text(encoding="utf-8")

    # Add required apps to INSTALLED_APPS
    content = content.replace(
        "'django.contrib.staticfiles',",
        """'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',""",
    )

    # Add middleware
    content = content.replace(
        "MIDDLEWARE = [",
        "MIDDLEWARE = [\n    'corsheaders.middleware.CorsMiddleware',",
    )

    settings_path.write_text(content, encoding="utf-8")

    return djboost_project
