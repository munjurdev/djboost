"""
Feature registry — the single source of truth for all DJBoost features.

Each feature declares:
  - required_packages: pip packages always needed
  - optional_packages: pip packages needed only when other features are present
  - requires: features that must be enabled first
  - conflicts: features that cannot coexist
  - files_created: files this feature creates (for rollback tracking)
  - files_modified: files this feature modifies (for rollback tracking)
  - env_vars: environment variables this feature adds
  - settings_keys: settings.py keys this feature adds
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class Feature:
    """A single DJBoost feature with its dependency graph metadata."""

    name: str
    display_name: str
    description: str

    # Package management
    required_packages: List[str] = field(default_factory=list)
    optional_packages: List[str] = field(default_factory=list)

    # Dependency graph
    requires: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    # File tracking (relative to project root)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)

    # Settings tracking
    settings_keys: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)

    # Detection: how to tell if this feature is already installed
    detection_files: List[str] = field(default_factory=list)
    detection_packages: List[str] = field(default_factory=list)
    detection_settings: List[str] = field(default_factory=list)


# ── Feature Registry ──────────────────────────────────────────────────────────

FEATURES: Dict[str, Feature] = {

    # ══════════════════════════════════════════════════════════════════════════
    # CORE FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "celery": Feature(
        name="celery",
        display_name="Celery",
        description="Background task processing with Redis broker",
        required_packages=["celery>=5.4,<6", "redis>=5.0,<6"],
        requires=[],
        conflicts=[],
        files_created=[
            "{project}/celery.py",
            "{project}/tasks.py",
        ],
        files_modified=[
            "{project}/__init__.py",
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", "CELERY_BEAT_SCHEDULE"],
        env_vars=["CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"],
        detection_files=["{project}/celery.py"],
        detection_packages=["celery", "redis"],
        detection_settings=["CELERY_BROKER_URL"],
    ),
    "celery-beat": Feature(
        name="celery-beat",
        display_name="Celery Beat",
        description="Periodic task scheduler for Celery",
        required_packages=[],
        requires=["celery"],
        conflicts=[],
        files_created=[],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["CELERY_BEAT_SCHEDULE"],
        detection_settings=["CELERY_BEAT_SCHEDULE"],
    ),
    "scheduler": Feature(
        name="scheduler",
        display_name="APScheduler",
        description="Lightweight in-process job scheduler (alternative to Celery Beat)",
        required_packages=["django-apscheduler>=0.7,<1"],
        requires=[],
        conflicts=["celery-beat"],
        files_created=[
            "{project}/scheduler.py",
        ],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["APSCHEDULER_DATETIME_FORMAT", "SCHEDULER_DEFAULT"],
        detection_packages=["django-apscheduler"],
        detection_settings=["APSCHEDULER_DATETIME_FORMAT"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # INFRASTRUCTURE FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "docker": Feature(
        name="docker",
        display_name="Docker",
        description="Containerization with Docker Compose",
        required_packages=["gunicorn>=21.2,<23"],
        optional_packages=[],
        requires=[],
        conflicts=[],
        files_created=[
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
        ],
        files_modified=["requirements.txt"],
        env_vars=["DB_HOST", "REDIS_HOST"],
        detection_files=["Dockerfile", "docker-compose.yml", ".dockerignore"],
        detection_packages=["gunicorn"],
    ),
    "kubernetes": Feature(
        name="kubernetes",
        display_name="Kubernetes",
        description="Kubernetes deployment manifests and Helm-ready config",
        required_packages=[],
        requires=["docker"],
        conflicts=[],
        files_created=[
            "k8s/deployment.yaml",
            "k8s/service.yaml",
            "k8s/ingress.yaml",
            "k8s/configmap.yaml",
            "k8s/secrets.yaml",
        ],
        detection_files=["k8s/deployment.yaml"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # DATABASE & CACHING FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "postgres": Feature(
        name="postgres",
        display_name="PostgreSQL",
        description="PostgreSQL database backend with connection pooling",
        required_packages=["psycopg2-binary>=2.9,<3"],
        requires=[],
        conflicts=[],
        files_modified=[
            "{project}/settings.py",
            ".env",
            "requirements.txt",
        ],
        settings_keys=["DATABASES"],
        env_vars=["DB_ENGINE", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"],
        detection_packages=["psycopg2-binary"],
    ),
    "redis-cache": Feature(
        name="redis-cache",
        display_name="Redis Cache",
        description="Redis-backed caching and session storage",
        required_packages=["django-redis>=5.4,<6", "redis>=5.0,<6"],
        requires=[],
        conflicts=[],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["CACHES", "SESSION_ENGINE"],
        env_vars=["REDIS_HOST", "REDIS_PORT", "REDIS_DB"],
        detection_packages=["django-redis"],
        detection_settings=["CACHES"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # API FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "api-docs": Feature(
        name="api-docs",
        display_name="API Documentation",
        description="Swagger UI and ReDoc for API documentation",
        required_packages=["drf-spectacular>=0.27,<1"],
        requires=[],
        conflicts=[],
        files_modified=[
            "{project}/urls.py",
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["SPECTACULAR_SETTINGS"],
        detection_packages=["drf-spectacular"],
        detection_settings=["SPECTACULAR_SETTINGS"],
    ),
    "graphql": Feature(
        name="graphql",
        display_name="GraphQL",
        description="GraphQL API with Strawberry (type-safe, async-ready)",
        required_packages=["strawberry-graphql[django]>=0.22,<1"],
        requires=[],
        conflicts=[],
        files_created=[
            "{project}/schema.py",
            "apps/{app_name}/gql.py",
        ],
        files_modified=[
            "{project}/urls.py",
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["STRAWBERRY"],
        env_vars=[],
        detection_packages=["strawberry-graphql"],
        detection_settings=["STRAWBERRY"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # REALTIME FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "channels": Feature(
        name="channels",
        display_name="Django Channels",
        description="WebSocket and async protocol support",
        required_packages=[
            "daphne>=4.1,<5",
            "channels>=4.1,<5",
            "channels-redis>=4.2,<5",
        ],
        requires=[],
        conflicts=[],
        files_created=[
            "{project}/asgi.py",
        ],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["ASGI_APPLICATION", "CHANNEL_LAYERS"],
        detection_packages=["channels", "daphne"],
        detection_settings=["ASGI_APPLICATION"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # CI/CD FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "cicd-github": Feature(
        name="cicd-github",
        display_name="GitHub Actions",
        description="GitHub Actions CI/CD pipeline",
        required_packages=[],
        requires=[],
        conflicts=["cicd-gitlab"],
        files_created=[
            ".github/workflows/main.yml",
        ],
        detection_files=[".github/workflows/main.yml"],
    ),
    "cicd-gitlab": Feature(
        name="cicd-gitlab",
        display_name="GitLab CI",
        description="GitLab CI/CD pipeline",
        required_packages=[],
        requires=[],
        conflicts=["cicd-github"],
        files_created=[
            ".gitlab-ci.yml",
        ],
        detection_files=[".gitlab-ci.yml"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # STORAGE FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "storage": Feature(
        name="storage",
        display_name="Cloud Storage",
        description="S3-compatible file storage with django-storages",
        required_packages=["django-storages[boto3]>=1.14,<2", "boto3>=1.28,<2"],
        requires=[],
        conflicts=[],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["STORAGES", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_STORAGE_BUCKET_NAME"],
        env_vars=[
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_STORAGE_BUCKET_NAME",
            "AWS_S3_REGION_NAME",
            "AWS_S3_CUSTOM_DOMAIN",
        ],
        detection_packages=["django-storages", "boto3"],
        detection_settings=["AWS_STORAGE_BUCKET_NAME"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # SECURITY FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "security": Feature(
        name="security",
        display_name="Security Headers",
        description="CSP, HSTS, X-Frame-Options and security middleware",
        required_packages=["django-csp>=3.8,<4", "django-feature-policy>=3.1,<4"],
        requires=[],
        conflicts=[],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=[
            "CSP_DEFAULT_SRC", "CSP_SCRIPT_SRC", "CSP_STYLE_SRC",
            "SECURE_HSTS_SECONDS", "SECURE_HSTS_INCLUDE_SUBDOMAINS",
            "SECURE_HSTS_PRELOAD",
        ],
        detection_packages=["django-csp"],
        detection_settings=["CSP_DEFAULT_SRC"],
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # OBSERVABILITY FEATURES
    # ══════════════════════════════════════════════════════════════════════════

    "sentry": Feature(
        name="sentry",
        display_name="Sentry",
        description="Error tracking and performance monitoring",
        required_packages=["sentry-sdk[django]>=2.0,<3"],
        requires=[],
        conflicts=[],
        files_modified=[
            "{project}/settings.py",
            "{project}/wsgi.py",
            "requirements.txt",
        ],
        settings_keys=["SENTRY_DSN", "SENTRY_TRACES_SAMPLE_RATE"],
        env_vars=["SENTRY_DSN", "SENTRY_ENVIRONMENT", "SENTRY_TRACES_SAMPLE_RATE"],
        detection_packages=["sentry-sdk"],
        detection_settings=["SENTRY_DSN"],
    ),
    "logging": Feature(
        name="logging",
        display_name="Structured Logging",
        description="Structured JSON logging with structlog",
        required_packages=["structlog>=24.0,<25", "python-json-logger>=2.0,<3"],
        requires=[],
        conflicts=[],
        files_created=[
            "{project}/logging_config.py",
        ],
        files_modified=[
            "{project}/settings.py",
            "requirements.txt",
        ],
        settings_keys=["LOGGING"],
        env_vars=["LOG_LEVEL", "LOG_FORMAT"],
        detection_packages=["structlog"],
        detection_settings=["structlog"],
    ),
    "monitoring": Feature(
        name="monitoring",
        display_name="OpenTelemetry",
        description="Distributed tracing and metrics with OpenTelemetry",
        required_packages=[
            "opentelemetry-api>=1.25,<2",
            "opentelemetry-sdk>=1.25,<2",
            "opentelemetry-exporter-otlp>=1.25,<2",
            "opentelemetry-instrumentation-django>=0.46b0,<1",
            "opentelemetry-instrumentation-requests>=0.46b0,<1",
            "opentelemetry-instrumentation-dbapi>=0.46b0,<1",
        ],
        requires=[],
        conflicts=[],
        files_created=[
            "{project}/telemetry.py",
        ],
        files_modified=[
            "{project}/settings.py",
            "{project}/wsgi.py",
            "requirements.txt",
        ],
        settings_keys=["OTEL_SERVICE_NAME", "OTEL_EXPORTER_OTLP_ENDPOINT"],
        env_vars=[
            "OTEL_SERVICE_NAME",
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "OTEL_EXPORTER_OTLP_HEADERS",
            "OTEL_RESOURCE_ATTRIBUTES",
        ],
        detection_packages=["opentelemetry-api"],
        detection_settings=["OTEL_SERVICE_NAME"],
    ),
}


# ── Registry helpers ──────────────────────────────────────────────────────────

def get_feature(name: str) -> Optional[Feature]:
    """Get a feature by name."""
    return FEATURES.get(name)


def list_features() -> List[Feature]:
    """Return all registered features."""
    return list(FEATURES.values())


def list_feature_names() -> List[str]:
    """Return all feature names."""
    return list(FEATURES.keys())


# ── Dependency resolution ─────────────────────────────────────────────────────

def resolve_dependencies(feature_name: str) -> List[str]:
    """
    Return the ordered list of features that must be installed
    before `feature_name`, including transitive dependencies.
    Uses DFS with cycle detection.
    """
    visited: Set[str] = set()
    order: List[str] = []
    in_stack: Set[str] = set()

    def _dfs(name: str):
        if name in in_stack:
            raise ValueError(f"Circular dependency detected: {name}")
        if name in visited:
            return

        in_stack.add(name)
        feat = FEATURES.get(name)
        if feat is None:
            raise ValueError(f"Unknown feature: {name}")

        for dep in feat.requires:
            _dfs(dep)

        in_stack.discard(name)
        visited.add(name)
        order.append(name)

    _dfs(feature_name)
    return order


def detect_conflicts(feature_name: str, enabled: Set[str]) -> List[str]:
    """
    Check if adding `feature_name` conflicts with any already-enabled features.
    Returns list of conflicting feature names.
    """
    feat = FEATURES.get(feature_name)
    if feat is None:
        return []

    conflicts = []
    for conflict_name in feat.conflicts:
        if conflict_name in enabled:
            conflicts.append(conflict_name)
    return conflicts


def detect_reverse_dependencies(feature_name: str, enabled: Set[str]) -> List[str]:
    """
    Find features in `enabled` that depend on `feature_name`.
    These would need to be removed first.
    """
    dependents = []
    for other_name in enabled:
        if other_name == feature_name:
            continue
        other_feat = FEATURES.get(other_name)
        if other_feat and feature_name in other_feat.requires:
            dependents.append(other_name)
    return dependents


# ── State detection ───────────────────────────────────────────────────────────

def scan_enabled_features(project_name: Optional[str] = None) -> Set[str]:
    """
    Scan the current directory and determine which features are enabled.
    Returns a set of feature names.
    """
    enabled: Set[str] = set()

    for feat_name, feat in FEATURES.items():
        if _is_feature_enabled(feat, project_name):
            enabled.add(feat_name)

    return enabled


def _is_feature_enabled(feat: Feature, project_name: Optional[str] = None) -> bool:
    """Check if a single feature is currently enabled."""
    # Check by packages in requirements.txt
    if feat.detection_packages:
        req_path = Path("requirements.txt")
        if req_path.exists():
            req_content = req_path.read_text(encoding="utf-8").lower()
            for pkg in feat.detection_packages:
                if pkg in req_content:
                    return True

    # Check by files
    if feat.detection_files:
        for file_pattern in feat.detection_files:
            file_path = _resolve_path(file_pattern, project_name)
            if file_path.exists():
                return True

    # Check by settings keys
    if feat.detection_settings and project_name:
        settings_path = Path(project_name) / "settings.py"
        if settings_path.exists():
            settings_content = settings_path.read_text(encoding="utf-8")
            for key in feat.detection_settings:
                if key in settings_content:
                    return True

    return False


def _resolve_path(pattern: str, project_name: Optional[str] = None) -> Path:
    """Resolve a file pattern like '{project}/celery.py' to an actual path."""
    if project_name and "{project}" in pattern:
        return Path(pattern.replace("{project}", project_name))
    return Path(pattern)
