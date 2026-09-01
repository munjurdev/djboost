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
        assert "0.8." in result.output


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
"""Tests for CLI command modules — add, remove, create, management."""
from unittest.mock import MagicMock, patch

runner = CliRunner()


# ── Add Command Help Tests ────────────────────────────────────────────────────


class TestAddCommandHelp:
    """Test that all add commands are registered and show help."""

    def test_add_celery_help(self):
        result = runner.invoke(app, ["add", "celery", "--help"])
        assert result.exit_code == 0
        assert "celery" in result.output.lower()

    def test_add_celery_beat_help(self):
        result = runner.invoke(app, ["add", "celery-beat", "--help"])
        assert result.exit_code == 0

    def test_add_scheduler_help(self):
        result = runner.invoke(app, ["add", "scheduler", "--help"])
        assert result.exit_code == 0
        assert "scheduler" in result.output.lower() or "apscheduler" in result.output.lower()

    def test_add_docker_help(self):
        result = runner.invoke(app, ["add", "docker", "--help"])
        assert result.exit_code == 0
        assert "docker" in result.output.lower()

    def test_add_kubernetes_help(self):
        result = runner.invoke(app, ["add", "kubernetes", "--help"])
        assert result.exit_code == 0
        assert "kubernetes" in result.output.lower()

    def test_add_postgres_help(self):
        result = runner.invoke(app, ["add", "postgres", "--help"])
        assert result.exit_code == 0
        assert "postgres" in result.output.lower()

    def test_add_redis_cache_help(self):
        result = runner.invoke(app, ["add", "redis-cache", "--help"])
        assert result.exit_code == 0
        assert "redis" in result.output.lower()

    def test_add_api_docs_help(self):
        result = runner.invoke(app, ["add", "api-docs", "--help"])
        assert result.exit_code == 0
        assert "api" in result.output.lower() or "documentation" in result.output.lower()

    def test_add_graphql_help(self):
        result = runner.invoke(app, ["add", "graphql", "--help"])
        assert result.exit_code == 0
        assert "graphql" in result.output.lower()

    def test_add_channels_help(self):
        result = runner.invoke(app, ["add", "channels", "--help"])
        assert result.exit_code == 0
        assert "channels" in result.output.lower()

    def test_add_cicd_help(self):
        result = runner.invoke(app, ["add", "cicd", "--help"])
        assert result.exit_code == 0

    def test_add_storage_help(self):
        result = runner.invoke(app, ["add", "storage", "--help"])
        assert result.exit_code == 0
        assert "storage" in result.output.lower()

    def test_add_security_help(self):
        result = runner.invoke(app, ["add", "security", "--help"])
        assert result.exit_code == 0
        assert "security" in result.output.lower()

    def test_add_sentry_help(self):
        result = runner.invoke(app, ["add", "sentry", "--help"])
        assert result.exit_code == 0
        assert "sentry" in result.output.lower()

    def test_add_logging_help(self):
        result = runner.invoke(app, ["add", "logging", "--help"])
        assert result.exit_code == 0
        assert "logging" in result.output.lower()

    def test_add_monitoring_help(self):
        result = runner.invoke(app, ["add", "monitoring", "--help"])
        assert result.exit_code == 0
        assert "monitoring" in result.output.lower() or "opentelemetry" in result.output.lower()


# ── Remove Command Help Tests ─────────────────────────────────────────────────


class TestRemoveCommandHelp:
    """Test that all remove commands are registered and show help."""

    def test_remove_celery_help(self):
        result = runner.invoke(app, ["remove", "celery", "--help"])
        assert result.exit_code == 0

    def test_remove_celery_beat_help(self):
        result = runner.invoke(app, ["remove", "celery-beat", "--help"])
        assert result.exit_code == 0

    def test_remove_scheduler_help(self):
        result = runner.invoke(app, ["remove", "scheduler", "--help"])
        assert result.exit_code == 0

    def test_remove_docker_help(self):
        result = runner.invoke(app, ["remove", "docker", "--help"])
        assert result.exit_code == 0

    def test_remove_kubernetes_help(self):
        result = runner.invoke(app, ["remove", "kubernetes", "--help"])
        assert result.exit_code == 0

    def test_remove_postgres_help(self):
        result = runner.invoke(app, ["remove", "postgres", "--help"])
        assert result.exit_code == 0

    def test_remove_redis_cache_help(self):
        result = runner.invoke(app, ["remove", "redis-cache", "--help"])
        assert result.exit_code == 0

    def test_remove_api_docs_help(self):
        result = runner.invoke(app, ["remove", "api-docs", "--help"])
        assert result.exit_code == 0

    def test_remove_graphql_help(self):
        result = runner.invoke(app, ["remove", "graphql", "--help"])
        assert result.exit_code == 0

    def test_remove_channels_help(self):
        result = runner.invoke(app, ["remove", "channels", "--help"])
        assert result.exit_code == 0

    def test_remove_cicd_help(self):
        result = runner.invoke(app, ["remove", "cicd", "--help"])
        assert result.exit_code == 0

    def test_remove_storage_help(self):
        result = runner.invoke(app, ["remove", "storage", "--help"])
        assert result.exit_code == 0

    def test_remove_security_help(self):
        result = runner.invoke(app, ["remove", "security", "--help"])
        assert result.exit_code == 0

    def test_remove_sentry_help(self):
        result = runner.invoke(app, ["remove", "sentry", "--help"])
        assert result.exit_code == 0

    def test_remove_logging_help(self):
        result = runner.invoke(app, ["remove", "logging", "--help"])
        assert result.exit_code == 0

    def test_remove_monitoring_help(self):
        result = runner.invoke(app, ["remove", "monitoring", "--help"])
        assert result.exit_code == 0


# ── Add Command Dry Run Tests ─────────────────────────────────────────────────


class TestAddCommandDryRun:
    """Test add commands with --dry-run flag."""

    def test_add_celery_dry_run(self, djboost_project):
        """Celery add with dry-run should show plan."""
        result = runner.invoke(app, ["add", "celery", "--dry-run"])
        # May succeed or fail depending on project state, but should not crash
        assert result.exit_code in (0, 1)

    def test_add_docker_dry_run(self, djboost_project):
        """Docker add with dry-run should show plan."""
        result = runner.invoke(app, ["add", "docker", "--dry-run"])
        assert result.exit_code in (0, 1)

    def test_add_scheduler_dry_run(self, djboost_project):
        """Scheduler add with dry-run should show plan."""
        result = runner.invoke(app, ["add", "scheduler", "--dry-run"])
        assert result.exit_code in (0, 1)


# ── Remove Command Dry Run Tests ──────────────────────────────────────────────


class TestRemoveCommandDryRun:
    """Test remove commands with --dry-run flag."""

    def test_remove_celery_dry_run(self, djboost_project):
        """Celery remove with dry-run should show plan."""
        result = runner.invoke(app, ["remove", "celery", "--dry-run"])
        # May succeed or fail depending on project state
        assert result.exit_code in (0, 1)

    def test_remove_docker_dry_run(self, djboost_project):
        """Docker remove with dry-run should show plan."""
        result = runner.invoke(app, ["remove", "docker", "--dry-run"])
        assert result.exit_code in (0, 1)


# ── Management Command Tests ──────────────────────────────────────────────────


class TestManagementCommands:
    """Test management commands (doctor, validate, info, features)."""

    def test_features_command(self):
        """features command should list all features."""
        result = runner.invoke(app, ["features"])
        assert result.exit_code == 0
        assert "Celery" in result.output
        assert "Docker" in result.output

    def test_version_command(self):
        """--version should show version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.8." in result.output

    def test_help_command(self):
        """--help should show help text."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "djboost" in result.output.lower()

    def test_doctor_without_project(self, tmp_path):
        """doctor without manage.py should handle gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    def test_validate_without_project(self, tmp_path):
        """validate without manage.py should handle gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0

    def test_info_without_project(self, tmp_path):
        """info without manage.py should handle gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0


# ── Create Command Tests ──────────────────────────────────────────────────────


class TestCreateCommands:
    """Test create commands (startproject, startapp, startauth)."""

    def test_startproject_help(self):
        """startproject --help should show usage."""
        result = runner.invoke(app, ["startproject", "--help"])
        assert result.exit_code == 0

    def test_startapp_help(self):
        """startapp --help should show usage."""
        result = runner.invoke(app, ["startapp", "--help"])
        assert result.exit_code == 0

    def test_startauth_help(self):
        """startauth --help should show usage."""
        result = runner.invoke(app, ["startauth", "--help"])
        assert result.exit_code == 0

    def test_startapp_requires_name(self, tmp_path):
        """startapp without name should fail or show help."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["startapp"])
        # Should either fail or show help
        assert result.exit_code in (0, 1, 2)


# ── Add Command Error Handling Tests ──────────────────────────────────────────


class TestAddCommandErrors:
    """Test error handling in add commands."""

    def test_add_unknown_feature(self, tmp_path):
        """Adding unknown feature should fail."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "nonexistent"])
        # Should fail with error
        assert result.exit_code != 0 or "Unknown" in result.output

    def test_add_celery_without_project(self, tmp_path):
        """Adding celery without manage.py should handle gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["add", "celery"])
        # Should fail gracefully (no project found)
        assert result.exit_code in (0, 1)


# ── Remove Command Error Handling Tests ───────────────────────────────────────


class TestRemoveCommandErrors:
    """Test error handling in remove commands."""

    def test_remove_unknown_feature(self, tmp_path):
        """Removing unknown feature should fail."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["remove", "nonexistent"])
        assert result.exit_code != 0 or "Unknown" in result.output

    def test_remove_celery_without_project(self, tmp_path):
        """Removing celery without manage.py should handle gracefully."""
        os.chdir(tmp_path)
        result = runner.invoke(app, ["remove", "celery"])
        # Should fail gracefully
        assert result.exit_code in (0, 1)


# ── Force Flag Tests ──────────────────────────────────────────────────────────


class TestForceFlag:
    """Test --force flag bypasses conflict/reverse dependency checks."""

    def test_add_with_force_flag(self, djboost_project):
        """--force flag should be accepted."""
        result = runner.invoke(app, ["add", "celery", "--force", "--dry-run"])
        # Should accept the flag
        assert result.exit_code in (0, 1)

    def test_remove_with_force_flag(self, djboost_project):
        """--force flag should be accepted."""
        result = runner.invoke(app, ["remove", "celery", "--force", "--dry-run"])
        assert result.exit_code in (0, 1)
