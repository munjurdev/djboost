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
from unittest.mock import MagicMock, patch

import pytest

# Capture the real Python executable at import time, before any test
# can mutate sys.executable via check_virtual_environment().
_REAL_PYTHON = sys.executable


def _fast_subprocess(original_run):
    """Intercept slow subprocess calls (pip installs) and return instantly.

    Passes through all other calls (django-admin, manage.py check, etc.) unchanged.
    """
    def _wrapper(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args", [])
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            # pip install/uninstall → pretend success
            # Match: python -m pip install ... or pip install ...
            if "pip" in cmd and any(kw in cmd for kw in ("install", "uninstall")):
                # But NOT venv creation (python -m venv ...)
                if "venv" not in cmd:
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = ""
                    result.stderr = ""
                    return result
        return original_run(*args, **kwargs)
    return _wrapper


# Capture the REAL subprocess.run before any patches are applied.
_REAL_SUBPROCESS_RUN = subprocess.run


@pytest.fixture(autouse=True)
def _mock_check_venv():
    """Prevent check_virtual_environment from creating venvs during tests.

    Without this, every CLI command invocation (add/remove --dry-run) triggers
    check_virtual_environment(), which on a bare CI runner:
      1. Creates a new venv in each temp directory
      2. Installs ~13 packages (DRF, JWT, CORS, ...)
      3. Mutates sys.executable / os.environ globally
    This makes tests extremely slow (~30 s each) and pollutes global state,
    causing cascading failures after temp dirs are cleaned up.
    """
    patches = []
    for name, mod in list(sys.modules.items()):
        if (
            name.startswith("djboost.commands.")
            or name == "djboost.generator"
        ) and hasattr(mod, "check_virtual_environment"):
            p = patch.object(mod, "check_virtual_environment", return_value=True)
            p.start()
            patches.append(p)

    # Mock slow pip install/uninstall at the command-module level
    # so CLI commands get fast fakes, but direct tests of the underlying
    # functions (safe_engine, dependencies) still test the real code.
    for cmd_name in list(sys.modules.keys()):
        if not cmd_name.startswith("djboost.commands."):
            continue
        mod = sys.modules[cmd_name]
        for attr in ("check_virtual_environment",):
            if hasattr(mod, attr) and attr not in patches:
                pass  # already patched above

    # Mock pip operations at the safe_engine level so execute_plan is fast
    safe_engine = sys.modules.get("djboost.generators.safe_engine")
    if safe_engine:
        for attr, val in [
            ("_install_packages", lambda pkgs: None),
            ("_uninstall_packages", lambda pkgs: None),
        ]:
            orig = getattr(safe_engine, attr, None)
            if orig is not None:
                p = patch.object(safe_engine, attr, side_effect=val)
                p.start()
                patches.append(p)
    # Note: we do NOT mock uninstall_packages here because tests
    # directly test that function. The pip uninstall call is fast anyway.

    yield
    for p in patches:
        p.stop()


@pytest.fixture
def temp_dir():
    """Create a temporary directory and clean up after."""
    original_dir = os.getcwd()
    tmp = tempfile.mkdtemp(prefix="djboost_test_")
    os.chdir(tmp)
    yield Path(tmp)
    os.chdir(original_dir)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="session")
def _ensure_django_installed():
    """Install Django once per test session instead of per test."""
    subprocess.run(
        [_REAL_PYTHON, "-m", "pip", "install", "Django", "-q"],
        capture_output=True,
        text=True,
    )
    yield


@pytest.fixture(scope="session")
def _django_template():
    """Create a Django project template once per session for fast copying."""
    import tempfile as _tmp
    tmpl = Path(_tmp.mkdtemp(prefix="djboost_tmpl_"))
    subprocess.run(
        [_REAL_PYTHON, "-m", "django", "startproject", "testproject", str(tmpl)],
        capture_output=True,
        text=True,
    )
    yield tmpl
    shutil.rmtree(tmpl, ignore_errors=True)


@pytest.fixture
def djboost_project(temp_dir, _ensure_django_installed, _django_template):
    """
    Create a real Django project using djboost's create command.
    Returns the project path.
    """
    # Copy the pre-built template instead of calling django-admin each time
    shutil.copytree(_django_template, temp_dir, dirs_exist_ok=True)

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
