"""
Tests for CLI management commands — validate, info, features, doctor.
"""
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from djboost.cli import app


runner = CliRunner()


class TestFeaturesCommand:
    """Test the djboost features command."""

    def test_features_command_runs(self):
        """features command should run without error."""
        result = runner.invoke(app, ["features"])
        assert result.exit_code == 0
        assert "Features" in result.output or "features" in result.output.lower()

    def test_features_shows_core_features(self):
        """features command should list core features."""
        result = runner.invoke(app, ["features"])
        assert "Celery" in result.output
        assert "Docker" in result.output
        assert "API Documentation" in result.output

    def test_features_shows_enterprise_features(self):
        """features command should list new enterprise features."""
        result = runner.invoke(app, ["features"])
        out = result.output.lower()
        assert "sentry" in out
        assert "postgresql" in out
        assert "redis cache" in out
        assert "cloud storage" in out
        assert "graphql" in out
        assert "security headers" in out
        assert "structured logging" in out
        assert "opentelemetry" in out
        assert "kubernetes" in out
        assert "apscheduler" in out


class TestVersionCommand:
    """Test the --version flag."""

    def test_version_shows_version(self):
        """--version should show the version number."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.7." in result.output


class TestValidateCommand:
    """Test the djboost validate command."""

    def test_validate_without_manage_py(self, tmp_path):
        """validate should fail gracefully without manage.py."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0

    def test_validate_with_manage_py(self, tmp_path):
        """validate should run with a basic manage.py present."""
        os.chdir(tmp_path)
        (tmp_path / "manage.py").write_text("#!/usr/bin/env python\nimport sys\n", encoding="utf-8")
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0


class TestDoctorCommand:
    """Test the djboost doctor command."""

    def test_doctor_without_manage_py(self, tmp_path):
        """doctor should handle missing manage.py gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    def test_doctor_with_manage_py(self, tmp_path):
        """doctor should run with a basic manage.py present."""
        os.chdir(tmp_path)
        (tmp_path / "manage.py").write_text("#!/usr/bin/env python\nimport sys\n", encoding="utf-8")
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Health" in result.output or "health" in result.output.lower()


class TestInfoCommand:
    """Test the djboost info command."""

    def test_info_without_manage_py(self, tmp_path):
        """info should handle missing manage.py gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0


class TestAddCommands:
    """Test that new add commands are registered and show --help."""

    def test_add_sentry_help(self):
        result = runner.invoke(app, ["add", "sentry", "--help"])
        assert result.exit_code == 0
        assert "Sentry" in result.output

    def test_add_postgres_help(self):
        result = runner.invoke(app, ["add", "postgres", "--help"])
        assert result.exit_code == 0
        assert "PostgreSQL" in result.output

    def test_add_redis_cache_help(self):
        result = runner.invoke(app, ["add", "redis-cache", "--help"])
        assert result.exit_code == 0
        assert "Redis" in result.output

    def test_add_storage_help(self):
        result = runner.invoke(app, ["add", "storage", "--help"])
        assert result.exit_code == 0
        assert "cloud storage" in result.output.lower()

    def test_add_graphql_help(self):
        result = runner.invoke(app, ["add", "graphql", "--help"])
        assert result.exit_code == 0
        assert "GraphQL" in result.output

    def test_add_security_help(self):
        result = runner.invoke(app, ["add", "security", "--help"])
        assert result.exit_code == 0
        assert "security" in result.output.lower()

    def test_add_logging_help(self):
        result = runner.invoke(app, ["add", "logging", "--help"])
        assert result.exit_code == 0
        assert "logging" in result.output.lower()

    def test_add_monitoring_help(self):
        result = runner.invoke(app, ["add", "monitoring", "--help"])
        assert result.exit_code == 0
        assert "OpenTelemetry" in result.output

    def test_add_kubernetes_help(self):
        result = runner.invoke(app, ["add", "kubernetes", "--help"])
        assert result.exit_code == 0
        assert "Kubernetes" in result.output

    def test_add_scheduler_help(self):
        result = runner.invoke(app, ["add", "scheduler", "--help"])
        assert result.exit_code == 0
        assert "APScheduler" in result.output

    def test_add_channels_help(self):
        result = runner.invoke(app, ["add", "channels", "--help"])
        assert result.exit_code == 0
        assert "Channels" in result.output


class TestRemoveCommands:
    """Test that new remove commands are registered and show --help."""

    def test_remove_sentry_help(self):
        result = runner.invoke(app, ["remove", "sentry", "--help"])
        assert result.exit_code == 0

    def test_remove_postgres_help(self):
        result = runner.invoke(app, ["remove", "postgres", "--help"])
        assert result.exit_code == 0

    def test_remove_channels_help(self):
        result = runner.invoke(app, ["remove", "channels", "--help"])
        assert result.exit_code == 0
        assert "Channels" in result.output
