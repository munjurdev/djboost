"""Integration tests — end-to-end CLI commands."""
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


def _env():  # type: ignore[no-untyped-def]
    """Return env dict with UTF-8 IO encoding for subprocess."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


@pytest.fixture
def live_project():
    """Create a real Django project in a temp dir for integration tests."""
    original_dir = os.getcwd()
    tmp = Path(tempfile.mkdtemp(prefix="djboost_integ_"))
    os.chdir(tmp)
    project_name = "integtest"
    subprocess.run([_REAL_PYTHON, "-m", "pip", "install", "Django", "-q"], capture_output=True, env=_env())
    subprocess.run([_REAL_PYTHON, "-m", "django", "startproject", project_name, "."], capture_output=True, env=_env())
    (tmp / "apps").mkdir(exist_ok=True)
    (tmp / "apps" / "__init__.py").touch()
    (tmp / "common").mkdir(exist_ok=True)
    (tmp / "common" / "__init__.py").touch()
    (tmp / "static").mkdir(exist_ok=True)
    (tmp / "media").mkdir(exist_ok=True)
    (tmp / "requirements.txt").write_text("Django>=4.2,<7\n", encoding="utf-8")
    (tmp / ".env").write_text("DEBUG=True\nSECRET_KEY=test-secret\n", encoding="utf-8")
    yield tmp
    os.chdir(original_dir)
    shutil.rmtree(tmp, ignore_errors=True)


def run_cli(*args):  # type: ignore[no-untyped-def]
    """Run djboost CLI with UTF-8 encoding."""
    return subprocess.run(
        ["djboost", *args],
        capture_output=True, text=True, errors="replace", env=_env(),
    )


class TestVersionCommand:
    def test_version_returns_version(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "0.8.0" in (result.stdout or "")


class TestFeaturesCommand:
    def test_features_lists_all(self):
        result = run_cli("features")
        output = (result.stdout or result.stderr or "").lower()
        assert "celery" in output
        assert "docker" in output
        assert "sentry" in output


class TestValidateCommand:
    def test_validate_with_project(self, live_project):
        result = run_cli("validate")
        assert result.returncode == 0


class TestDoctorCommand:
    def test_doctor_with_project(self, live_project):
        result = run_cli("doctor")
        assert result.returncode == 0


class TestInfoCommand:
    def test_info_without_project(self, tmp_path):
        os.chdir(tmp_path)
        result = run_cli("info")
        output = (result.stdout or result.stderr or "")
        assert "manage.py" in output.lower() or "error" in output.lower()

    def test_info_with_project(self, live_project):
        result = run_cli("info")
        assert result.returncode == 0


class TestDryRunCommands:
    def test_add_celery_dry_run(self, live_project):
        original_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        result = run_cli("add", "celery", "--dry-run")
        assert result.returncode == 0
        current_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        assert original_req == current_req

    def test_add_docker_dry_run(self, live_project):
        original_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        result = run_cli("add", "docker", "--dry-run")
        assert result.returncode == 0
        current_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        assert original_req == current_req
