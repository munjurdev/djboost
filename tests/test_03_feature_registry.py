"""Tests for the feature registry — dependency graph, conflict detection, state scanning."""
import os

import pytest


from djboost.generators.features import (
    FEATURES,
    detect_conflicts,
    detect_reverse_dependencies,
    get_feature,
    list_feature_names,
    resolve_dependencies,
    scan_enabled_features,
)


EXPECTED_FEATURES = {
    "celery", "celery-beat", "scheduler",
    "docker", "kubernetes",
    "postgres", "redis-cache",
    "api-docs", "graphql",
    "channels",
    "cicd-github", "cicd-gitlab",
    "storage",
    "security",
    "sentry", "logging", "monitoring",
}


class TestFeatureRegistry:
    """Test the feature registry is complete and consistent."""

    def test_all_features_registered(self):
        """All expected features should be registered."""
        assert EXPECTED_FEATURES == set(list_feature_names())

    def test_get_feature_returns_feature(self):
        """get_feature should return a Feature object."""
        feat = get_feature("celery")
        assert feat is not None
        assert feat.name == "celery"
        assert feat.display_name == "Celery"

    def test_get_unknown_feature_returns_none(self):
        """get_feature should return None for unknown features."""
        assert get_feature("nonexistent") is None

    def test_all_features_have_required_packages_or_files(self):
        """Every feature should have either packages or files."""
        for feat in FEATURES.values():
            assert (
                feat.required_packages
                or feat.files_created
                or feat.files_modified
                or feat.detection_settings
            ), f"Feature {feat.name} has no packages, files, or detection methods"

    def test_new_features_have_detection(self):
        """New enterprise features should have detection methods."""
        enterprise_features = ["sentry", "postgres", "redis-cache", "storage", "graphql",
                               "security", "logging", "monitoring", "kubernetes", "scheduler"]
        for name in enterprise_features:
            feat = get_feature(name)
            assert feat is not None, f"Feature {name} not found"
            has_detection = (
                feat.detection_packages
                or feat.detection_files
                or feat.detection_settings
            )
            assert has_detection, f"Feature {name} has no detection methods"


class TestDependencyResolution:
    """Test dependency graph resolution."""

    def test_celery_has_no_dependencies(self):
        """Celery should have no dependencies."""
        deps = resolve_dependencies("celery")
        assert deps == ["celery"]

    def test_celery_beat_requires_celery(self):
        """Celery Beat should require Celery."""
        deps = resolve_dependencies("celery-beat")
        assert "celery" in deps
        assert "celery-beat" in deps
        assert deps.index("celery") < deps.index("celery-beat")

    def test_docker_has_no_dependencies(self):
        """Docker should have no required feature dependencies."""
        deps = resolve_dependencies("docker")
        assert deps == ["docker"]

    def test_kubernetes_requires_docker(self):
        """Kubernetes should require Docker."""
        deps = resolve_dependencies("kubernetes")
        assert "docker" in deps
        assert "kubernetes" in deps
        assert deps.index("docker") < deps.index("kubernetes")

    def test_unknown_feature_raises_error(self):
        """Resolving an unknown feature should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown feature"):
            resolve_dependencies("nonexistent")

    def test_circular_dependency_detection(self):
        """Circular dependencies should be detected."""
        from djboost.generators import features
        original = features.FEATURES["celery"].requires
        features.FEATURES["celery"].requires = ["celery-beat"]
        try:
            with pytest.raises(ValueError, match="Circular dependency"):
                resolve_dependencies("celery-beat")
        finally:
            features.FEATURES["celery"].requires = original


class TestConflictDetection:
    """Test conflict detection between features."""

    def test_cicd_github_conflicts_with_gitlab(self):
        """GitHub Actions and GitLab CI should conflict."""
        conflicts = detect_conflicts("cicd-github", {"cicd-gitlab"})
        assert "cicd-gitlab" in conflicts

    def test_scheduler_conflicts_with_celery_beat(self):
        """APScheduler should conflict with Celery Beat."""
        conflicts = detect_conflicts("scheduler", {"celery-beat"})
        assert "celery-beat" in conflicts

    def test_no_conflict_for_independent_features(self):
        """Independent features should not conflict."""
        conflicts = detect_conflicts("celery", {"docker"})
        assert conflicts == []

    def test_no_conflict_when_not_enabled(self):
        """No conflict if the conflicting feature isn't enabled."""
        conflicts = detect_conflicts("cicd-github", {"celery"})
        assert conflicts == []


class TestReverseDependencies:
    """Test reverse dependency detection."""

    def test_celery_beat_depends_on_celery(self):
        """Removing celery should detect celery-beat as a dependent."""
        dependents = detect_reverse_dependencies("celery", {"celery", "celery-beat"})
        assert "celery-beat" in dependents

    def test_docker_has_kubernetes_dependent(self):
        """Removing docker should detect kubernetes as a dependent."""
        dependents = detect_reverse_dependencies("docker", {"docker", "kubernetes"})
        assert "kubernetes" in dependents

    def test_no_reverse_deps_for_independent(self):
        """Independent features should have no reverse deps."""
        dependents = detect_reverse_dependencies("docker", {"celery"})
        assert dependents == []


class TestStateScanning:
    """Test feature state detection from project files."""

    def test_scan_returns_empty_set_for_clean_project(self, tmp_path):
        """A clean project with no features should have no enabled features."""
        os.chdir(tmp_path)
        (tmp_path / "manage.py").write_text("# test", encoding="utf-8")
        enabled = scan_enabled_features()
        assert "celery" not in enabled
        assert "api-docs" not in enabled
        assert "cicd-github" not in enabled
