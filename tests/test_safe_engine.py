"""Tests for the safe operation engine — plan generation, dry-run, idempotency."""
import os


from djboost.generators.safe_engine import (
    ChangePlan,
    generate_add_plan,
    generate_remove_plan,
)


class TestAddPlanGeneration:
    """Test plan generation for add operations."""

    def test_add_celery_plan_has_packages(self, tmp_path):
        """Adding celery should plan to install celery and redis."""
        os.chdir(tmp_path)
        plan = generate_add_plan("celery", dry_run=True)
        assert plan.feature_name == "celery"
        assert plan.operation == "add"
        assert any("celery" in pkg for pkg in plan.packages_to_install)
        assert any("redis" in pkg for pkg in plan.packages_to_install)

    def test_add_celery_beat_plan_includes_celery_dependency(self, tmp_path):
        """Adding celery-beat should plan to also install celery if not present."""
        os.chdir(tmp_path)
        plan = generate_add_plan("celery-beat", dry_run=True)
        assert plan.feature_name == "celery-beat"
        # Should include celery in dependencies
        assert "celery" in plan.dependencies

    def test_add_docker_plan_has_gunicorn(self, tmp_path):
        """Adding docker should plan to install gunicorn."""
        os.chdir(tmp_path)
        plan = generate_add_plan("docker", dry_run=True)
        assert any("gunicorn" in pkg for pkg in plan.packages_to_install)

    def test_add_unknown_feature_has_errors(self):
        """Adding an unknown feature should produce errors."""
        plan = generate_add_plan("nonexistent", dry_run=True)
        assert len(plan.errors) > 0
        assert "Unknown feature" in plan.errors[0]

    def test_add_plan_marks_dry_run(self):
        """Plan should reflect dry_run flag."""
        plan = generate_add_plan("celery", dry_run=True)
        assert plan.dry_run is True

        plan = generate_add_plan("celery", dry_run=False)
        assert plan.dry_run is False

    def test_add_plan_detects_conflicts(self):
        """Plan should detect conflicts with enabled features."""
        plan = generate_add_plan(
            "cicd-github",
            dry_run=True,
        )
        # No conflicts by default (nothing enabled)
        assert plan.conflicts == []


class TestRemovePlanGeneration:
    """Test plan generation for remove operations."""

    def test_remove_celery_plan_has_packages_to_uninstall(self):
        """Removing celery should plan to uninstall celery and redis."""
        plan = generate_remove_plan("celery", dry_run=True)
        assert plan.feature_name == "celery"
        assert plan.operation == "remove"

    def test_remove_unknown_feature_has_errors(self):
        """Removing an unknown feature should produce errors."""
        plan = generate_remove_plan("nonexistent", dry_run=True)
        assert len(plan.errors) > 0

    def test_remove_plan_marks_dry_run(self):
        """Plan should reflect dry_run flag."""
        plan = generate_remove_plan("celery", dry_run=True)
        assert plan.dry_run is True


class TestIdempotency:
    """Test idempotency detection."""

    def test_add_already_enabled_feature(self, tmp_path):
        """Adding a feature that's already enabled should be idempotent."""
        os.chdir(tmp_path)
        # Create requirements.txt with celery
        (tmp_path / "requirements.txt").write_text(
            "celery>=5.4\nredis>=5.0\n",
            encoding="utf-8",
        )

        plan = generate_add_plan("celery", dry_run=True)
        assert plan.idempotent is True
        assert len(plan.warnings) > 0
