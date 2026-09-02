"""
Safe operation engine — makes add/remove operations deterministic and reversible.

Flow for every add/remove:
  1. Scan current project state
  2. Resolve dependencies / conflicts
  3. Generate a change plan
  4. Execute (or preview with --dry-run)
  5. Validate with Django checks
  6. Record reversible change set
  7. Auto-rollback on validation failure
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from rich import print

# Capture the real Python executable at import time, before any code
# can mutate sys.executable via check_virtual_environment().
_REAL_PYTHON = sys.executable

from djboost.generators.features import (
    FEATURES,
    Feature,
    detect_conflicts,
    detect_reverse_dependencies,
    get_feature,
    resolve_dependencies,
    scan_enabled_features,
)

# ── Change tracking ─
@dataclass
class FileChange:
    """A single file change to be applied."""

    path: str
    action: str  # "create", "modify", "delete", "backup"
    content: Optional[str] = None
    backup_path: Optional[str] = None


@dataclass
class ChangePlan:
    """A complete plan for an add or remove operation."""

    feature_name: str
    operation: str
    dry_run: bool
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    reverse_deps: List[str] = field(default_factory=list)
    files_to_change: List[FileChange] = field(default_factory=list)
    packages_to_install: List[str] = field(default_factory=list)
    packages_to_uninstall: List[str] = field(default_factory=list)
    settings_changes: List[Tuple[str, str]] = field(default_factory=list)
    env_vars_to_add: List[str] = field(default_factory=list)
    idempotent: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ChangeRecord:
    """A recorded change set for rollback."""

    feature_name: str
    operation: str
    timestamp: str
    files_backed_up: Dict[str, str]
    files_created: List[str]
    files_deleted: List[str]
    packages_installed: List[str]
    packages_uninstalled: List[str]
    settings_content_backup: Optional[str] = None


# ── Plan generation ─
def generate_add_plan(
    feature_name: str, dry_run: bool = False, project_name: Optional[str] = None, force: bool = False
) -> ChangePlan:
    """Generate a complete plan for adding a feature."""
    plan = ChangePlan(feature_name=feature_name, operation="add", dry_run=dry_run)

    feat = get_feature(feature_name)
    if feat is None:
        plan.errors.append(f"Unknown feature: {feature_name}")
        return plan

    try:
        plan.dependencies = resolve_dependencies(feature_name)
        plan.dependencies = [d for d in plan.dependencies if d != feature_name]
    except ValueError as e:
        plan.errors.append(str(e))
        return plan

    enabled = scan_enabled_features(project_name)

    if feature_name in enabled:
        plan.idempotent = True
        plan.warnings.append(f"Feature '{feature_name}' is already enabled.")
        return plan

    plan.conflicts = detect_conflicts(feature_name, enabled)
    if plan.conflicts and not force:
        plan.errors.append(f"Conflicts detected: {', '.join(plan.conflicts)}. Use --force to override.")
        return plan

    for dep in plan.dependencies:
        if dep not in enabled:
            dep_feat = get_feature(dep)
            if dep_feat:
                plan.packages_to_install.extend(dep_feat.required_packages)
                plan.files_to_change.extend(_plan_feature_files(dep_feat, project_name, "add"))

    plan.packages_to_install.extend(feat.required_packages)
    plan.files_to_change.extend(_plan_feature_files(feat, project_name, "add"))
    plan.env_vars_to_add.extend(feat.env_vars)
    plan.packages_to_install = list(dict.fromkeys(plan.packages_to_install))

    return plan


def generate_remove_plan(
    feature_name: str, dry_run: bool = False, project_name: Optional[str] = None, force: bool = False
) -> ChangePlan:
    """Generate a complete plan for removing a feature."""
    plan = ChangePlan(feature_name=feature_name, operation="remove", dry_run=dry_run)

    feat = get_feature(feature_name)
    if feat is None:
        plan.errors.append(f"Unknown feature: {feature_name}")
        return plan

    enabled = scan_enabled_features(project_name)
    if feature_name not in enabled:
        plan.idempotent = True
        plan.warnings.append(f"Feature '{feature_name}' is not currently enabled.")
        return plan

    plan.reverse_deps = detect_reverse_dependencies(feature_name, enabled)
    if plan.reverse_deps and not force:
        plan.errors.append(
            f"These features depend on '{feature_name}': {', '.join(plan.reverse_deps)}. Remove them first, or use --force."
        )
        return plan

    plan.files_to_change.extend(_plan_feature_files(feat, project_name, "remove"))
    plan.packages_to_uninstall.extend(feat.required_packages)

    return plan


# ── File planning ─
def _plan_feature_files(feat: Feature, project_name: Optional[str], operation: str) -> List[FileChange]:
    """Plan file changes for a feature."""
    changes = []

    if operation == "add":
        for file_pattern in feat.files_created:
            path = _resolve_pattern(file_pattern, project_name)
            if not path.exists():
                changes.append(FileChange(path=str(path), action="create"))

        for file_pattern in feat.files_modified:
            path = _resolve_pattern(file_pattern, project_name)
            if path.exists():
                changes.append(FileChange(path=str(path), action="modify", backup_path=f".djboost_backup/{path}.bak"))

    elif operation == "remove":
        for file_pattern in feat.files_created:
            path = _resolve_pattern(file_pattern, project_name)
            if path.exists():
                changes.append(FileChange(path=str(path), action="delete", backup_path=f".djboost_backup/{path}.bak"))

        for file_pattern in feat.files_modified:
            path = _resolve_pattern(file_pattern, project_name)
            if path.exists():
                changes.append(FileChange(path=str(path), action="modify", backup_path=f".djboost_backup/{path}.bak"))

    return changes


def _resolve_pattern(pattern: str, project_name: Optional[str] = None) -> Path:
    """Resolve a file pattern like '{project}/celery.py'."""
    if project_name and "{project}" in pattern:
        return Path(pattern.replace("{project}", project_name))
    return Path(pattern)


# ── Plan execution ─
def execute_plan(
    plan: ChangePlan, project_name: Optional[str] = None, apply_fn: Optional[Callable[[], None]] = None
) -> Optional[ChangeRecord]:
    """Execute a change plan, or preview it if dry_run=True."""
    _print_plan(plan)

    if plan.dry_run:
        print("\n[cyan]🔍 Dry run — no changes made.[/cyan]\n")
        return None

    if plan.errors:
        print("\n[red]❌ Cannot proceed due to errors.[/red]\n")
        return None

    if plan.idempotent:
        print("\n[yellow]⚠️  No changes needed (already in desired state).[/yellow]\n")
        return None

    record = ChangeRecord(
        feature_name=plan.feature_name,
        operation=plan.operation,
        timestamp=datetime.now().isoformat(),
        files_backed_up={},
        files_created=[],
        files_deleted=[],
        packages_installed=[],
        packages_uninstalled=[],
    )

    backup_dir = Path(".djboost_backup")
    backup_dir.mkdir(exist_ok=True)

    try:
        print("\n[cyan]━━━ Step 1/5: Backing up files ━━━[/cyan]")
        for change in plan.files_to_change:
            if change.action in ("modify", "delete"):
                src = Path(change.path)
                if src.exists():
                    bak = backup_dir / change.path
                    bak.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, bak)
                    record.files_backed_up[str(src)] = str(bak)
                    print(f"  [dim]Backed up {change.path}[/dim]")

        print("\n[cyan]━━━ Step 2/5: Applying changes ━━━[/cyan]")
        for change in plan.files_to_change:
            if change.action == "create":
                _apply_create(change, project_name)
                record.files_created.append(change.path)
            elif change.action == "delete":
                _apply_delete(change)
                record.files_deleted.append(change.path)
            elif change.action == "modify":
                _apply_modify(change, plan, project_name)

        if apply_fn is not None:
            print("\n[cyan]━━━ Step 3/5: Generating files ━━━[/cyan]")
            apply_fn()

        print("\n[cyan]━━━ Step 4/5: Managing packages ━━━[/cyan]")
        if plan.packages_to_install:
            _install_packages(plan.packages_to_install)
            record.packages_installed = plan.packages_to_install
        if plan.packages_to_uninstall:
            _uninstall_packages(plan.packages_to_uninstall)
            record.packages_uninstalled = plan.packages_to_uninstall

        print("\n[cyan]━━━ Step 5/5: Validating ━━━[/cyan]")
        is_valid, errors = _validate_project(project_name)

        if not is_valid:
            print("\n[red]❌ Validation failed! Rolling back...[/red]")
            _rollback(record)
            print("[green]✔ Rollback complete.[/green]\n")
            return None

        _save_change_record(record)
        print("\n[bold green]✅ Operation completed successfully![/bold green]\n")
        return record

    except Exception as e:
        print(f"\n[red]❌ Error during execution: {e}[/red]")
        print("[cyan]Rolling back...[/cyan]")
        _rollback(record)
        print("[green]✔ Rollback complete.[/green]\n")
        return None


# ── Apply helpers ─
def _apply_create(change: FileChange, project_name: Optional[str] = None):
    """Create a new file."""
    path = Path(change.path)
    if path.exists():
        print(f"  [yellow]⚠ {change.path} already exists, skipping[/yellow]")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  [green]✔ Will create {change.path}[/green]")


def _apply_delete(change: FileChange):
    """Delete a file."""
    path = Path(change.path)
    if path.exists():
        path.unlink()
        print(f"  [green]✔ Deleted {change.path}[/green]")
    else:
        print(f"  [yellow]⚠ {change.path} not found, skipping[/yellow]")


def _apply_modify(change: FileChange, plan: ChangePlan, project_name: Optional[str] = None):
    """Modify an existing file — the actual logic is in the feature generators."""
    path = Path(change.path)
    if path.exists():
        print(f"  [green]✔ Will modify {change.path}[/green]")
    else:
        print(f"  [yellow]⚠ {change.path} not found, skipping[/yellow]")


# ── Package management ─
def _install_packages(packages: List[str]):
    """Install pip packages in a single batch call."""
    if not packages:
        return
    result = subprocess.run(
        [_REAL_PYTHON, "-m", "pip", "install", "-q", *packages],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        for pkg in packages:
            print(f"  [green]✔ Installed {pkg}[/green]")
    else:
        print(f"  [red]✘ Failed to install packages: {result.stderr}[/red]")


def _uninstall_packages(packages: List[str]):
    """Uninstall pip packages in a single batch call."""
    if not packages:
        return
    pkg_names = [pkg.split(">=")[0].split("<")[0].split("==")[0].strip() for pkg in packages]
    result = subprocess.run(
        [_REAL_PYTHON, "-m", "pip", "uninstall", "-y", "-q", *pkg_names],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        for name in pkg_names:
            print(f"  [green]✔ Uninstalled {name}[/green]")
    else:
        for name in pkg_names:
            print(f"  [yellow]⚠ {name} not installed, skipping[/yellow]")


# ── Validation ─
def _validate_project(project_name: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Run Django system checks to validate the project."""
    errors = []

    env = os.environ.copy()
    if project_name:
        env["DJANGO_SETTINGS_MODULE"] = f"{project_name}.settings"

    result = subprocess.run(
        [_REAL_PYTHON, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        result2 = subprocess.run([_REAL_PYTHON, "manage.py", "check"], capture_output=True, text=True, env=env)
        if result2.returncode != 0:
            errors.append(result2.stderr)

    import_code = (
        f"import django; django.setup(); import {project_name}.settings"
        if project_name
        else "import django; django.setup()"
    )
    result3 = subprocess.run([_REAL_PYTHON, "-c", import_code], capture_output=True, text=True, env=env)
    if result3.returncode != 0:
        errors.append(f"Import check failed: {result3.stderr}")

    return len(errors) == 0, errors


# ── Rollback ─
def _rollback(record: ChangeRecord):
    """Rollback a completed change using the change record."""
    for orig_path, bak_path in record.files_backed_up.items():
        bak = Path(bak_path)
        orig = Path(orig_path)
        if bak.exists():
            orig.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bak, orig)
            print(f"  [green]✔ Restored {orig_path}[/green]")

    for file_path in record.files_created:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  [green]✔ Removed created file {file_path}[/green]")

    if record.packages_uninstalled:
        subprocess.run(
            [_REAL_PYTHON, "-m", "pip", "install", "-q", *record.packages_uninstalled],
            capture_output=True,
            text=True,
        )

    if record.packages_installed:
        pkg_names = [pkg.split(">=")[0].split("<")[0].split("==")[0].strip() for pkg in record.packages_installed]
        subprocess.run(
            [_REAL_PYTHON, "-m", "pip", "uninstall", "-y", "-q", *pkg_names],
            capture_output=True,
            text=True,
        )

    backup_dir = Path(".djboost_backup")
    if backup_dir.exists() and not any(backup_dir.iterdir()):
        backup_dir.rmdir()


# ── Change record persistence ─
def _save_change_record(record: ChangeRecord):
    """Save a change record to .djboost_backup/changes.json."""
    changes_file = Path(".djboost_backup/changes.json")

    existing = []
    if changes_file.exists():
        try:
            existing = json.loads(changes_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            existing = []

    entry = {
        "feature_name": record.feature_name,
        "operation": record.operation,
        "timestamp": record.timestamp,
        "files_backed_up": record.files_backed_up,
        "files_created": record.files_created,
        "files_deleted": record.files_deleted,
        "packages_installed": record.packages_installed,
        "packages_uninstalled": record.packages_uninstalled,
    }
    existing.append(entry)

    changes_file.parent.mkdir(parents=True, exist_ok=True)
    changes_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def load_change_history() -> List[dict]:
    """Load the change history from .djboost_backup/changes.json."""
    changes_file = Path(".djboost_backup/changes.json")
    if changes_file.exists():
        try:
            return json.loads(changes_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return []
    return []


# ── Plan display ─
def _print_plan(plan: ChangePlan):
    """Pretty-print the change plan."""
    mode = "[yellow]DRY RUN[/yellow]" if plan.dry_run else "[green]EXECUTE[/green]"
    action = "Add" if plan.operation == "add" else "Remove"

    print(f"\n[bold]{action} feature: {plan.feature_name}[/bold] {mode}\n")

    if plan.errors:
        print("[red]Errors:[/red]")
        for err in plan.errors:
            print(f"  ✘ {err}")

    if plan.warnings:
        print("[yellow]Warnings:[/yellow]")
        for warn in plan.warnings:
            print(f"  ⚠ {warn}")

    if plan.dependencies:
        print("\n[cyan]Dependencies to install:[/cyan]")
        for dep in plan.dependencies:
            print(f"  → {dep}")

    if plan.conflicts:
        print("\n[red]Conflicts:[/red]")
        for conflict in plan.conflicts:
            print(f"  ✘ {conflict}")

    if plan.reverse_deps:
        print("\n[red]Reverse dependencies (must remove first):[/red]")
        for dep in plan.reverse_deps:
            print(f"  ✘ {dep}")

    if plan.packages_to_install:
        print("\n[cyan]Packages to install:[/cyan]")
        for pkg in plan.packages_to_install:
            print(f"  + {pkg}")

    if plan.packages_to_uninstall:
        print("\n[cyan]Packages to uninstall:[/cyan]")
        for pkg in plan.packages_to_uninstall:
            print(f"  - {pkg}")

    if plan.files_to_change:
        print("\n[cyan]Files to change:[/cyan]")
        for change in plan.files_to_change:
            icon = {"create": "+", "delete": "-", "modify": "~"}.get(change.action, "?")
            print(f"  {icon} {change.path} ({change.action})")

    if plan.env_vars_to_add:
        print("\n[cyan]Environment variables:[/cyan]")
        for var in plan.env_vars_to_add:
            print(f"  → {var}")
