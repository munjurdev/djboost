"""
Tests for Django/Python compatibility — verify dependency version ranges
support modern Django releases (5.x, 6.x) and Python 3.12-3.14.
"""
import os
import sys
from pathlib import Path

import pytest

# Project root is one level up from tests/
PROJECT_ROOT = Path(__file__).parent.parent

from djboost.generators.dependencies import ESSENTIAL_PACKAGES, OPTIONAL_PACKAGES


class TestDependencyRanges:
    """Test that dependency version ranges support modern Django."""

    def test_drf_supports_django_5(self):
        """DRF version range should support Django 5.x."""
        drf_pkg = [p for p in ESSENTIAL_PACKAGES if "djangorestframework" in p and "simplejwt" not in p]
        assert len(drf_pkg) == 1
        assert ">=3.15" in drf_pkg[0]

    def test_cors_headers_supports_django_5(self):
        """django-cors-headers should support Django 5.x."""
        cors_pkg = [p for p in ESSENTIAL_PACKAGES if "cors-headers" in p]
        assert len(cors_pkg) == 1
        assert ">=4.3" in cors_pkg[0]

    def test_whitenoise_version_range(self):
        """whitenoise should have a modern version range."""
        wn_pkg = [p for p in ESSENTIAL_PACKAGES if "whitenoise" in p]
        assert len(wn_pkg) == 1
        assert ">=6.6" in wn_pkg[0]

    def test_celery_version_range(self):
        """Celery should have a modern version range."""
        celery_pkgs = OPTIONAL_PACKAGES["celery"]
        celery_pkg = [p for p in celery_pkgs if "celery" in p]
        assert len(celery_pkg) == 1
        assert ">=5.4" in celery_pkg[0]

    def test_channels_version_range(self):
        """Channels should have a modern version range."""
        channels_pkgs = OPTIONAL_PACKAGES["channels"]
        channels_pkg = [p for p in channels_pkgs if p.startswith("channels>=")]
        assert len(channels_pkg) == 1
        assert ">=4.1" in channels_pkg[0]

    def test_all_packages_have_version_bounds(self):
        """Every package should have upper version bounds."""
        for pkg in ESSENTIAL_PACKAGES:
            assert "<" in pkg, f"Package {pkg} has no upper bound"
            assert ">=" in pkg, f"Package {pkg} has no lower bound"

        for category, pkgs in OPTIONAL_PACKAGES.items():
            for pkg in pkgs:
                assert "<" in pkg, f"Package {pkg} in {category} has no upper bound"
                assert ">=" in pkg, f"Package {pkg} in {category} has no lower bound"


class TestPythonCompatibility:
    """Test that the project metadata declares modern Python support."""

    def test_pyproject_requires_python(self):
        """pyproject.toml should require Python >=3.10."""
        content = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'requires-python = ">=3.10' in content

    def test_pyproject_has_313_classifier(self):
        """pyproject.toml should list Python 3.13 classifier."""
        content = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "Programming Language :: Python :: 3.13" in content

    def test_pyproject_has_314_classifier(self):
        """pyproject.toml should list Python 3.14 classifier."""
        content = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "Programming Language :: Python :: 3.14" in content

    def test_pyproject_has_django_classifiers(self):
        """pyproject.toml should list Django framework classifiers."""
        content = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "Framework :: Django :: 5.2" in content
        assert "Framework :: Django :: 6.0" in content


class TestCIVersionMatrix:
    """Test that CI workflow uses modern Python versions."""

    def test_github_actions_python_matrix(self, tmp_path):
        """Generated GitHub Actions should test Python 3.12-3.14."""
        from djboost.generators.cicd import generate_github_actions

        os.chdir(tmp_path)
        generate_github_actions()
        content = (tmp_path / ".github" / "workflows" / "main.yml").read_text(encoding="utf-8")
        assert '"3.12"' in content
        assert '"3.13"' in content
        assert '"3.14"' in content
        # Should NOT have old versions
        assert '"3.10"' not in content
        assert '"3.11"' not in content

    def test_dockerfile_uses_python_312(self, tmp_path):
        """Generated Dockerfile should use Python 3.12."""
        from djboost.generators.docker import generate_dockerfile

        os.chdir(tmp_path)
        generate_dockerfile()
        content = (tmp_path / "Dockerfile").read_text(encoding="utf-8")
        assert "python:3.12-slim" in content
        assert "python:3.11-slim" not in content
