"""djboost.generators — Feature generators and safe operation engine.

Public API:
    - safe_engine: Plan generation, execution, rollback
    - features: Feature registry, dependency resolution
    - All generator modules (celery, docker, postgres, etc.)
"""

from djboost.generators.features import (
    FEATURES,
    Feature,
    detect_conflicts,
    detect_reverse_dependencies,
    get_feature,
    list_feature_names,
    list_features,
    resolve_dependencies,
    scan_enabled_features,
)
from djboost.generators.safe_engine import (
    ChangePlan,
    ChangeRecord,
    FileChange,
    execute_plan,
    generate_add_plan,
    generate_remove_plan,
    load_change_history,
)

__all__ = [
    # Safe engine
    "ChangePlan",
    "ChangeRecord",
    "FileChange",
    "execute_plan",
    "generate_add_plan",
    "generate_remove_plan",
    "load_change_history",
    # Features
    "FEATURES",
    "Feature",
    "detect_conflicts",
    "detect_reverse_dependencies",
    "get_feature",
    "list_feature_names",
    "list_features",
    "resolve_dependencies",
    "scan_enabled_features",
]
