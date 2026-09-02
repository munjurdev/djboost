"""Integration tests — end-to-end CLI commands."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from djboost.cli import app

# Capture the real Python executable at import time, before any test
# can mutate sys.executable via check_virtual_environment().
_REAL_PYTHON = sys.executable

runner = CliRunner()


@pytest.fixture
def live_project(_ensure_django_installed):
    """Create a real Django project in a temp dir for integration tests."""
    original_dir = os.getcwd()
    tmp = Path(tempfile.mkdtemp(prefix="djboost_integ_"))
    os.chdir(tmp)
    project_name = "integtest"
    subprocess.run([_REAL_PYTHON, "-m", "django", "startproject", project_name, "."], capture_output=True)
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


class TestVersionCommand:
    def test_version_returns_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.8" in result.output


class TestFeaturesCommand:
    def test_features_lists_all(self):
        result = runner.invoke(app, ["features"])
        output = result.output.lower()
        assert "celery" in output
        assert "docker" in output
        assert "sentry" in output


class TestValidateCommand:
    def test_validate_with_project(self, live_project):
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0


class TestDoctorCommand:
    def test_doctor_with_project(self, live_project):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0


class TestInfoCommand:
    def test_info_without_project(self, tmp_path):
        os.chdir(tmp_path)
        result = runner.invoke(app, ["info"])
        output = result.output.lower()
        assert "manage.py" in output or "error" in output

    def test_info_with_project(self, live_project):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0


class TestDryRunCommands:
    def test_add_celery_dry_run(self, live_project):
        original_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        result = runner.invoke(app, ["add", "celery", "--dry-run"])
        assert result.exit_code == 0
        current_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        assert original_req == current_req

    def test_add_docker_dry_run(self, live_project):
        original_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        result = runner.invoke(app, ["add", "docker", "--dry-run"])
        assert result.exit_code == 0
        current_req = (live_project / "requirements.txt").read_text(encoding="utf-8")
        assert original_req == current_req
