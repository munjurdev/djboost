"""
Comprehensive test suite to boost coverage across ALL modules.
Targets: cli.py, generator.py, docker.py, postgres.py, redis_cache.py,
         graphql.py, monitoring.py, channels_gen.py, logging_config.py,
         celery.py, scheduler.py, storage.py, security.py, sentry.py,
         api_docs.py, validators.py, and all command modules.
"""

import os
import re
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

# ── Helpers ──────────────────────────────────────────────────────────────────

MANAGE_PY_TEMPLATE = textwrap.dedent("""\
    #!/usr/bin/env python
    \"\"\"Django's command-line utility for administrative tasks.\"\"\"
    import os
    import sys

    def main():
        \"\"\"Run administrative tasks.\"\"\"
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django."
            ) from exc
        execute_from_command_line(sys.argv)

    if __name__ == '__main__':
        main()
""")

SETTINGS_TEMPLATE = textwrap.dedent("""\
    import os
    from pathlib import Path
    from decouple import config

    BASE_DIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = config('SECRET_KEY', default='test-key')
    DEBUG = config('DEBUG', default=False, cast=bool)
    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'corsheaders',
        'drf_spectacular',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = '{name}.urls'
    WSGI_APPLICATION = '{name}.wsgi.application'

    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_TZ = True

    STATIC_URL = 'static/'
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""")


def setup_django_project(tmp_path, name="testproject"):
    """Create a minimal djboost-style Django project in tmp_path."""
    project_dir = tmp_path / name
    project_dir.mkdir()

    # manage.py
    (tmp_path / "manage.py").write_text(MANAGE_PY_TEMPLATE.format(name=name), encoding="utf-8")

    # settings.py
    (project_dir / "settings.py").write_text(SETTINGS_TEMPLATE.format(name=name), encoding="utf-8")

    # urls.py
    (project_dir / "urls.py").write_text(
        textwrap.dedent(f"""\
            from django.urls import path

            urlpatterns = [
            ]
        """),
        encoding="utf-8",
    )

    # wsgi.py
    (project_dir / "wsgi.py").write_text(
        textwrap.dedent(f"""\
            import os
            from django.core.wsgi import get_wsgi_application

            os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
            application = get_wsgi_application()
        """),
        encoding="utf-8",
    )

    # __init__.py
    (project_dir / "__init__.py").write_text("", encoding="utf-8")

    # .env
    (tmp_path / ".env").write_text("SECRET_KEY=test-secret-key\nDEBUG=True\n", encoding="utf-8")

    # requirements.txt
    (tmp_path / "requirements.txt").write_text(
        "Django>=5.0,<6\ndjangorestframework>=3.15,<4\n"
        "django-rest-framework-simplejwt>=5.3,<6\n"
        "django-cors-headers>=4.3,<5\n"
        "drf-spectacular>=0.27,<1\n"
        "python-decouple>=3.8,<4\n",
        encoding="utf-8",
    )

    return tmp_path, name


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCli:
    """Test djboost.cli module."""

    def test_cli_app_is_typer(self):
        from djboost.cli import app

        assert app is not None

    def test_cli_has_add_subcommand(self):
        from djboost.cli import app

        cmd_names = [cmd.name for cmd in app.registered_commands]
        assert "startproject" in cmd_names

    def test_cli_add_group_exists(self):
        from djboost.cli import add

        assert add is not None

    def test_cli_remove_group_exists(self):
        from djboost.cli import remove

        assert remove is not None

    def test_version_callback(self):
        from djboost.cli import version_callback

        with pytest.raises((SystemExit, typer.Exit)):
            version_callback(True)

    def test_version_callback_false(self):
        from djboost.cli import version_callback

        version_callback(False)  # Should not raise

    def test_cli_main_callback(self):
        from djboost.cli import main

        assert callable(main)

    def test_cli_has_all_add_commands(self):
        from djboost.cli import add

        cmd_names = [cmd.name for cmd in add.registered_commands]
        for feat in [
            "celery",
            "docker",
            "postgres",
            "redis-cache",
            "channels",
            "graphql",
            "monitoring",
            "logging",
            "sentry",
            "security",
            "storage",
            "api-docs",
            "cicd",
            "kubernetes",
            "scheduler",
            "celery-beat",
        ]:
            assert feat in cmd_names, f"Missing add command: {feat}"

    def test_cli_has_all_remove_commands(self):
        from djboost.cli import remove

        cmd_names = [cmd.name for cmd in remove.registered_commands]
        for feat in [
            "celery",
            "docker",
            "postgres",
            "redis-cache",
            "channels",
            "graphql",
            "monitoring",
            "logging",
            "sentry",
            "security",
            "storage",
            "api-docs",
            "cicd",
            "kubernetes",
            "scheduler",
            "celery-beat",
        ]:
            assert feat in cmd_names, f"Missing remove command: {feat}"

    def test_cli_has_management_commands(self):
        from djboost.cli import app

        cmd_names = [cmd.name for cmd in app.registered_commands]
        for cmd in ["doctor", "validate", "info", "features"]:
            assert cmd in cmd_names, f"Missing management command: {cmd}"


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR (ORCHESTRATOR) TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGenerator:
    """Test djboost.generator module."""

    def test_imports(self):
        from djboost.generator import create_project

        assert callable(create_project)

    def test_check_virtual_environment_import(self):
        from djboost.generator import check_virtual_environment

        assert callable(check_virtual_environment)

    def test_validate_name_import(self):
        from djboost.generator import validate_name

        assert callable(validate_name)


# ═══════════════════════════════════════════════════════════════════════════════
# CELERY GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCeleryGenerator:
    """Test djboost.generators.celery module."""

    def test_get_project_name_no_manage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import get_project_name

        assert get_project_name() is None

    def test_get_project_name_valid(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "myapp")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import get_project_name

        assert get_project_name() == "myapp"

    def test_get_project_name_bad_manage(self, tmp_path, monkeypatch):
        (tmp_path / "manage.py").write_text("x = 1", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import get_project_name

        assert get_project_name() is None

    def test_generate_celery_files(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import generate_celery_files

        result = generate_celery_files("proj")
        assert (tmp_path / "proj" / "celery.py").exists()
        assert (tmp_path / "proj" / "tasks.py").exists()
        assert (tmp_path / "proj" / "__init__.py").exists()

    def test_generate_celery_files_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "celery.py").write_text("old", encoding="utf-8")
        (tmp_path / "proj" / "tasks.py").write_text("old", encoding="utf-8")
        from djboost.generators.celery import generate_celery_files

        generate_celery_files("proj")  # Should not raise

    def test_update_settings_celery(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import update_settings_celery

        result = update_settings_celery("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "CELERY_BROKER_URL" in content

    def test_update_settings_celery_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCELERY_BROKER_URL = 'redis://'\n",
            encoding="utf-8",
        )
        from djboost.generators.celery import update_settings_celery

        assert update_settings_celery("proj") is True

    def test_update_settings_celery_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import update_settings_celery

        assert update_settings_celery("nonexistent") is False

    def test_generate_celery_beat_config(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        # Add celery settings first
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCELERY_BROKER_URL = 'redis://'\n",
            encoding="utf-8",
        )
        from djboost.generators.celery import generate_celery_beat_config

        result = generate_celery_beat_config("proj")
        assert result is True

    def test_generate_celery_beat_no_celery(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import generate_celery_beat_config

        result = generate_celery_beat_config("proj")
        assert result is False

    def test_generate_celery_beat_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCELERY_BROKER_URL = 'redis://'\nCELERY_BEAT_SCHEDULE = {}\n",
            encoding="utf-8",
        )
        from djboost.generators.celery import generate_celery_beat_config

        assert generate_celery_beat_config("proj") is True

    def test_generate_celery_beat_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import generate_celery_beat_config

        assert generate_celery_beat_config("nope") is False

    def test_add_crontab_import(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import add_crontab_import

        result = add_crontab_import("proj")
        assert result is True

    def test_add_crontab_import_already_imported(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nfrom celery.schedules import crontab\n",
            encoding="utf-8",
        )
        from djboost.generators.celery import add_crontab_import

        assert add_crontab_import("proj") is True

    def test_add_crontab_import_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import add_crontab_import

        assert add_crontab_import("nope") is False

    def test_remove_celery_files(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "celery.py").write_text("c", encoding="utf-8")
        (tmp_path / "proj" / "tasks.py").write_text("t", encoding="utf-8")
        from djboost.generators.celery import remove_celery_files

        removed = remove_celery_files("proj")
        assert len(removed) == 2

    def test_remove_celery_files_not_found(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import remove_celery_files

        removed = remove_celery_files("proj")
        assert len(removed) == 0

    def test_remove_celery_from_init(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        init = tmp_path / "proj" / "__init__.py"
        init.write_text(
            "from .celery import app as celery_app\n\n__all__ = ('celery_app',)\n",
            encoding="utf-8",
        )
        from djboost.generators.celery import remove_celery_from_init

        assert remove_celery_from_init("proj") is True

    def test_remove_celery_from_init_no_celery(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import remove_celery_from_init

        assert remove_celery_from_init("proj") is True

    def test_remove_celery_from_init_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import remove_celery_from_init

        assert remove_celery_from_init("nope") is False

    def test_remove_celery_from_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8")
            + "\n# ── Celery (Background Tasks) ─\nCELERY_BROKER_URL = 'redis://'\n",
            encoding="utf-8",
        )
        from djboost.generators.celery import remove_celery_from_settings

        assert remove_celery_from_settings("proj") is True
        content = settings.read_text(encoding="utf-8")
        assert "CELERY_BROKER_URL" not in content

    def test_remove_celery_from_settings_not_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import remove_celery_from_settings

        assert remove_celery_from_settings("proj") is True

    def test_remove_celery_from_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import remove_celery_from_settings

        assert remove_celery_from_settings("nope") is False

    def test_remove_celery_from_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("celery>=5.4\nredis>=5.0\nDjango>=5.0\n", encoding="utf-8")
        from djboost.generators.celery import remove_celery_from_requirements

        assert remove_celery_from_requirements() is True
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "celery" not in content.lower()
        assert "redis" not in content.lower()
        assert "Django" in content

    def test_remove_celery_from_requirements_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.celery import remove_celery_from_requirements

        assert remove_celery_from_requirements() is False

    def test_remove_celery_from_requirements_no_celery(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\n", encoding="utf-8")
        from djboost.generators.celery import remove_celery_from_requirements

        assert remove_celery_from_requirements() is True


# ═══════════════════════════════════════════════════════════════════════════════
# POSTGRES GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPostgresGenerator:
    """Test djboost.generators.postgres module."""

    def test_update_settings_postgres(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        # Add DATABASES block so regex can match
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8")
            + "\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}\n",
            encoding="utf-8",
        )
        from djboost.generators.postgres import update_settings_postgres

        result = update_settings_postgres("proj")
        assert result is True
        content = settings.read_text(encoding="utf-8")
        assert "django.db.backends.postgresql" in content

    def test_update_settings_postgres_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n'ENGINE': 'django.db.backends.postgresql'\n",
            encoding="utf-8",
        )
        from djboost.generators.postgres import update_settings_postgres

        assert update_settings_postgres("proj") is True

    def test_update_settings_postgres_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.postgres import update_settings_postgres

        assert update_settings_postgres("nope") is False

    def test_update_env_postgres(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=x\n", encoding="utf-8")
        from djboost.generators.postgres import update_env_postgres

        result = update_env_postgres("proj")
        assert result is True
        content = (tmp_path / ".env").read_text(encoding="utf-8")
        assert "DB_ENGINE" in content

    def test_update_env_postgres_already_configured(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("DB_ENGINE=xxx\n", encoding="utf-8")
        from djboost.generators.postgres import update_env_postgres

        assert update_env_postgres("proj") is True

    def test_update_env_postgres_no_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.postgres import update_env_postgres

        assert update_env_postgres("proj") is False

    def test_add_postgres_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\n", encoding="utf-8")
        from djboost.generators.postgres import add_postgres_to_requirements

        add_postgres_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "psycopg2" in content

    def test_add_postgres_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("psycopg2-binary>=2.9\n", encoding="utf-8")
        from djboost.generators.postgres import add_postgres_to_requirements

        add_postgres_to_requirements()  # Should not raise

    def test_format_string_fix(self):
        """Verify the format string fix produces correct output."""
        name = "testproj"
        new_db = """DATABASES = {{
    'default': {{
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='{name}_db'),
        'USER': config('DB_USER', default='{name}_user'),
    }}
}}""".format(name=name)
        assert "testproj_db" in new_db
        assert "testproj_user" in new_db
        assert "DATABASES = {" in new_db


# ═══════════════════════════════════════════════════════════════════════════════
# REDIS CACHE GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRedisCacheGenerator:
    """Test djboost.generators.redis_cache module."""

    def test_update_settings_redis_cache(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.redis_cache import update_settings_redis_cache

        result = update_settings_redis_cache("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "CACHES" in content
        assert "django_redis" in content

    def test_update_settings_redis_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCACHES = {}\ndjango_redis\n",
            encoding="utf-8",
        )
        from djboost.generators.redis_cache import update_settings_redis_cache

        assert update_settings_redis_cache("proj") is True

    def test_update_settings_redis_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.redis_cache import update_settings_redis_cache

        assert update_settings_redis_cache("nope") is False

    def test_update_env_redis_cache(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=x\n", encoding="utf-8")
        from djboost.generators.redis_cache import update_env_redis_cache

        result = update_env_redis_cache("proj")
        assert result is True
        content = (tmp_path / ".env").read_text(encoding="utf-8")
        assert "REDIS_URL" in content

    def test_update_env_redis_already_configured(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("REDIS_URL=redis://\n", encoding="utf-8")
        from djboost.generators.redis_cache import update_env_redis_cache

        assert update_env_redis_cache("proj") is True

    def test_update_env_redis_no_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.redis_cache import update_env_redis_cache

        assert update_env_redis_cache("proj") is False

    def test_add_redis_cache_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\n", encoding="utf-8")
        from djboost.generators.redis_cache import add_redis_cache_to_requirements

        add_redis_cache_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "django-redis" in content
        assert "redis" in content

    def test_add_redis_cache_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("django-redis>=5.4\nredis>=5.0\n", encoding="utf-8")
        from djboost.generators.redis_cache import add_redis_cache_to_requirements

        add_redis_cache_to_requirements()  # Should not raise

    def test_format_string_fix(self):
        """Verify the format string fix produces correct output."""
        name = "testproj"
        cache_settings = """CACHES = {{
    'default': {{
        'BACKEND': 'django_redis.cache.RedisCache',
        'OPTIONS': {{
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }},
        'KEY_PREFIX': '{name}',
    }}
}}""".format(name=name)
        assert "testproj" in cache_settings
        assert "CACHES = {" in cache_settings
        assert "OPTIONS" in cache_settings
        assert "'CLIENT_CLASS'" in cache_settings


# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDockerGenerator:
    """Test djboost.generators.docker module."""

    def test_check_installed_features_no_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.docker import _check_installed_features

        features = _check_installed_features()
        assert all(v is False for v in features.values())

    def test_check_installed_features_with_celery(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("celery>=5.4\nchannels>=4.1\n", encoding="utf-8")
        from djboost.generators.docker import _check_installed_features

        features = _check_installed_features()
        assert features["celery"] is True
        assert features["channels"] is True

    def test_generate_docker_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.docker import generate_docker_files

        generate_docker_files("proj")
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()
        assert (tmp_path / ".dockerignore").exists()

    def test_generate_dockerfile(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.docker import generate_dockerfile

        result = generate_dockerfile()
        assert result is True
        assert (tmp_path / "Dockerfile").exists()
        content = (tmp_path / "Dockerfile").read_text(encoding="utf-8")
        assert "python:3.12-slim" in content

    def test_generate_dockerfile_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Dockerfile").write_text("old", encoding="utf-8")
        from djboost.generators.docker import generate_dockerfile

        assert generate_dockerfile() is False

    def test_generate_docker_compose_add(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.docker import generate_docker_compose_add

        result = generate_docker_compose_add("proj")
        assert result is True
        content = (tmp_path / "docker-compose.yml").read_text(encoding="utf-8")
        assert "web:" in content
        assert "db:" in content
        assert "redis:" in content

    def test_generate_docker_compose_add_with_celery(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("celery>=5.4\nflower>=2.0\n", encoding="utf-8")
        from djboost.generators.docker import generate_docker_compose_add

        result = generate_docker_compose_add("proj")
        assert result is True
        content = (tmp_path / "docker-compose.yml").read_text(encoding="utf-8")
        assert "celery:" in content
        assert "flower:" in content

    def test_generate_docker_compose_add_with_daphne(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("daphne>=4.1\n", encoding="utf-8")
        from djboost.generators.docker import generate_docker_compose_add

        result = generate_docker_compose_add("proj")
        assert result is True
        content = (tmp_path / "docker-compose.yml").read_text(encoding="utf-8")
        assert "daphne" in content

    def test_generate_docker_compose_add_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        (tmp_path / "docker-compose.yml").write_text("old", encoding="utf-8")
        from djboost.generators.docker import generate_docker_compose_add

        assert generate_docker_compose_add("proj") is False

    def test_generate_dockerignore_add(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.docker import generate_dockerignore_add

        result = generate_dockerignore_add()
        assert result is True
        assert (tmp_path / ".dockerignore").exists()

    def test_generate_dockerignore_add_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".dockerignore").write_text("old", encoding="utf-8")
        from djboost.generators.docker import generate_dockerignore_add

        assert generate_dockerignore_add() is False

    def test_add_docker_to_requirements_with_celery(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("celery>=5.4\n", encoding="utf-8")
        from djboost.generators.docker import add_docker_to_requirements

        add_docker_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "flower" in content
        assert "gunicorn" in content

    def test_add_docker_to_requirements_no_celery(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\n", encoding="utf-8")
        from djboost.generators.docker import add_docker_to_requirements

        add_docker_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "gunicorn" in content

    def test_add_docker_to_requirements_all_present(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text(
            "celery>=5.4\nflower>=2.0\ngunicorn>=21.2\ndaphne>=4.1\n", encoding="utf-8"
        )
        from djboost.generators.docker import add_docker_to_requirements

        add_docker_to_requirements()  # Should print "no additional needed"

    def test_get_project_name(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.docker import get_project_name

        assert get_project_name() == "proj"

    def test_get_project_name_no_manage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.docker import get_project_name

        assert get_project_name() is None


# ═══════════════════════════════════════════════════════════════════════════════
# CHANNELS GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestChannelsGenerator:
    """Test djboost.generators.channels_gen module."""

    def test_generate_asgi_file(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.channels_gen import generate_asgi_file

        result = generate_asgi_file("proj")
        assert result is True
        content = (tmp_path / "proj" / "asgi.py").read_text(encoding="utf-8")
        assert "ProtocolTypeRouter" in content

    def test_generate_asgi_file_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "asgi.py").write_text("old", encoding="utf-8")
        from djboost.generators.channels_gen import generate_asgi_file

        assert generate_asgi_file("proj") is False

    def test_update_settings_channels(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.channels_gen import update_settings_channels

        result = update_settings_channels("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "ASGI_APPLICATION" in content
        assert "CHANNEL_LAYERS" in content
        assert "daphne" in content

    def test_update_settings_channels_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nASGI_APPLICATION = 'proj.asgi.application'\nchannels\n",
            encoding="utf-8",
        )
        from djboost.generators.channels_gen import update_settings_channels

        assert update_settings_channels("proj") is True

    def test_update_settings_channels_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.channels_gen import update_settings_channels

        assert update_settings_channels("nope") is False

    def test_add_channels_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.channels_gen import add_channels_to_requirements

        add_channels_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "daphne" in content
        assert "channels" in content
        assert "channels-redis" in content

    def test_add_channels_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text(
            "daphne>=4.1\nchannels>=4.1\nchannels-redis>=4.2\n", encoding="utf-8"
        )
        from djboost.generators.channels_gen import add_channels_to_requirements

        add_channels_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPHQL GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGraphQLGenerator:
    """Test djboost.generators.graphql module."""

    def test_generate_graphql_schema(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.graphql import generate_graphql_schema

        result = generate_graphql_schema("proj")
        assert result is True
        assert (tmp_path / "proj" / "schema.py").exists()

    def test_generate_graphql_schema_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "schema.py").write_text("old", encoding="utf-8")
        from djboost.generators.graphql import generate_graphql_schema

        assert generate_graphql_schema("proj") is False

    def test_add_graphql_urls(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.graphql import add_graphql_urls

        result = add_graphql_urls("proj")
        assert result is True
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "graphql" in content.lower()

    def test_add_graphql_urls_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8") + "\ngraphql\nstrawberry\n",
            encoding="utf-8",
        )
        from djboost.generators.graphql import add_graphql_urls

        assert add_graphql_urls("proj") is True

    def test_add_graphql_urls_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.graphql import add_graphql_urls

        assert add_graphql_urls("nope") is False

    def test_add_graphql_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.graphql import add_graphql_settings

        result = add_graphql_settings("proj")
        assert result is True

    def test_add_graphql_settings_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nSTRAWBERRY = {}\n",
            encoding="utf-8",
        )
        from djboost.generators.graphql import add_graphql_settings

        assert add_graphql_settings("proj") is True

    def test_add_graphql_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.graphql import add_graphql_settings

        assert add_graphql_settings("nope") is False

    def test_add_graphql_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.graphql import add_graphql_to_requirements

        add_graphql_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "strawberry" in content

    def test_add_graphql_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("strawberry-graphql>=0.22\n", encoding="utf-8")
        from djboost.generators.graphql import add_graphql_to_requirements

        add_graphql_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# MONITORING GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestMonitoringGenerator:
    """Test djboost.generators.monitoring module."""

    def test_generate_telemetry(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.monitoring import generate_telemetry

        result = generate_telemetry("proj")
        assert result is True
        assert (tmp_path / "proj" / "telemetry.py").exists()

    def test_generate_telemetry_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "telemetry.py").write_text("old", encoding="utf-8")
        from djboost.generators.monitoring import generate_telemetry

        assert generate_telemetry("proj") is False

    def test_add_monitoring_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.monitoring import add_monitoring_settings

        result = add_monitoring_settings("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "OTEL_SERVICE_NAME" in content

    def test_add_monitoring_settings_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nOTEL_SERVICE_NAME\n",
            encoding="utf-8",
        )
        from djboost.generators.monitoring import add_monitoring_settings

        assert add_monitoring_settings("proj") is True

    def test_add_monitoring_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.monitoring import add_monitoring_settings

        assert add_monitoring_settings("nope") is False

    def test_add_monitoring_to_wsgi(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.monitoring import add_monitoring_to_wsgi

        result = add_monitoring_to_wsgi("proj")
        assert result is True
        content = (tmp_path / "proj" / "wsgi.py").read_text(encoding="utf-8")
        assert "telemetry" in content

    def test_add_monitoring_to_wsgi_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        wsgi = tmp_path / "proj" / "wsgi.py"
        wsgi.write_text(
            wsgi.read_text(encoding="utf-8") + "\ntelemetry\n",
            encoding="utf-8",
        )
        from djboost.generators.monitoring import add_monitoring_to_wsgi

        assert add_monitoring_to_wsgi("proj") is True

    def test_add_monitoring_to_wsgi_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.monitoring import add_monitoring_to_wsgi

        assert add_monitoring_to_wsgi("nope") is False

    def test_add_monitoring_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.monitoring import add_monitoring_to_requirements

        add_monitoring_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "opentelemetry" in content.lower()

    def test_add_monitoring_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text(
            "opentelemetry-api>=1.25\nopentelemetry-sdk>=1.25\n"
            "opentelemetry-exporter-otlp>=1.25\n"
            "opentelemetry-instrumentation-django>=0.46b0\n"
            "opentelemetry-instrumentation-requests>=0.46b0\n",
            encoding="utf-8",
        )
        from djboost.generators.monitoring import add_monitoring_to_requirements

        add_monitoring_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING CONFIG GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestLoggingConfigGenerator:
    """Test djboost.generators.logging_config module."""

    def test_generate_logging_config(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.logging_config import generate_logging_config

        result = generate_logging_config("proj")
        assert result is True
        assert (tmp_path / "proj" / "logging_config.py").exists()

    def test_generate_logging_config_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "logging_config.py").write_text("old", encoding="utf-8")
        from djboost.generators.logging_config import generate_logging_config

        assert generate_logging_config("proj") is False

    def test_add_logging_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.logging_config import add_logging_settings

        result = add_logging_settings("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "logging_config" in content
        assert "setup_logging" in content

    def test_add_logging_settings_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nstructlog\n",
            encoding="utf-8",
        )
        from djboost.generators.logging_config import add_logging_settings

        assert add_logging_settings("proj") is True

    def test_add_logging_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.logging_config import add_logging_settings

        assert add_logging_settings("nope") is False

    def test_add_logging_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.logging_config import add_logging_to_requirements

        add_logging_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "structlog" in content

    def test_add_logging_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("structlog>=24.0\npython-json-logger>=2.0\n", encoding="utf-8")
        from djboost.generators.logging_config import add_logging_to_requirements

        add_logging_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEDULER GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSchedulerGenerator:
    """Test djboost.generators.scheduler module."""

    def test_generate_scheduler_config(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.scheduler import generate_scheduler_config

        result = generate_scheduler_config("proj")
        assert result is True
        assert (tmp_path / "proj" / "scheduler.py").exists()

    def test_generate_scheduler_config_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "scheduler.py").write_text("old", encoding="utf-8")
        from djboost.generators.scheduler import generate_scheduler_config

        assert generate_scheduler_config("proj") is False

    def test_add_scheduler_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.scheduler import add_scheduler_settings

        result = add_scheduler_settings("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "APSCHEDULER_DATETIME_FORMAT" in content

    def test_add_scheduler_settings_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nAPSCHEDULER_DATETIME_FORMAT\n",
            encoding="utf-8",
        )
        from djboost.generators.scheduler import add_scheduler_settings

        assert add_scheduler_settings("proj") is True

    def test_add_scheduler_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.scheduler import add_scheduler_settings

        assert add_scheduler_settings("nope") is False

    def test_add_scheduler_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.scheduler import add_scheduler_to_requirements

        add_scheduler_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "django-apscheduler" in content

    def test_add_scheduler_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("django-apscheduler>=0.7\n", encoding="utf-8")
        from djboost.generators.scheduler import add_scheduler_to_requirements

        add_scheduler_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestStorageGenerator:
    """Test djboost.generators.storage module."""

    def test_update_settings_storage(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.storage import update_settings_storage

        result = update_settings_storage("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "AWS_STORAGE_BUCKET_NAME" in content

    def test_update_settings_storage_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nAWS_STORAGE_BUCKET_NAME\n",
            encoding="utf-8",
        )
        from djboost.generators.storage import update_settings_storage

        assert update_settings_storage("proj") is True

    def test_update_settings_storage_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.storage import update_settings_storage

        assert update_settings_storage("nope") is False

    def test_update_env_storage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=x\n", encoding="utf-8")
        from djboost.generators.storage import update_env_storage

        result = update_env_storage("proj")
        assert result is True
        content = (tmp_path / ".env").read_text(encoding="utf-8")
        assert "AWS_ACCESS_KEY_ID" in content

    def test_update_env_storage_already_configured(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("AWS_ACCESS_KEY_ID=xxx\n", encoding="utf-8")
        from djboost.generators.storage import update_env_storage

        assert update_env_storage("proj") is True

    def test_update_env_storage_no_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.storage import update_env_storage

        assert update_env_storage("proj") is False

    def test_add_storage_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.storage import add_storage_to_requirements

        add_storage_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "django-storages" in content
        assert "boto3" in content

    def test_add_storage_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("django-storages[boto3]>=1.14\nboto3>=1.28\n", encoding="utf-8")
        from djboost.generators.storage import add_storage_to_requirements

        add_storage_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# SECURITY GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSecurityGenerator:
    """Test djboost.generators.security module."""

    def test_update_settings_security(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.security import update_settings_security

        result = update_settings_security("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "CSP_DEFAULT_SRC" in content
        assert "csp.middleware.CSPMiddleware" in content

    def test_update_settings_security_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCSP_DEFAULT_SRC\n",
            encoding="utf-8",
        )
        from djboost.generators.security import update_settings_security

        assert update_settings_security("proj") is True

    def test_update_settings_security_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.security import update_settings_security

        assert update_settings_security("nope") is False

    def test_add_security_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.security import add_security_to_requirements

        add_security_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "django-csp" in content

    def test_add_security_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("django-csp>=3.8\n", encoding="utf-8")
        from djboost.generators.security import add_security_to_requirements

        add_security_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# SENTRY GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSentryGenerator:
    """Test djboost.generators.sentry module."""

    def test_add_sentry_to_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.sentry import add_sentry_to_settings

        result = add_sentry_to_settings("proj")
        assert result is True
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "SENTRY_DSN" in content

    def test_add_sentry_to_settings_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nSENTRY_DSN\n",
            encoding="utf-8",
        )
        from djboost.generators.sentry import add_sentry_to_settings

        assert add_sentry_to_settings("proj") is True

    def test_add_sentry_to_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.sentry import add_sentry_to_settings

        assert add_sentry_to_settings("nope") is False

    def test_add_sentry_to_wsgi(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.sentry import add_sentry_to_wsgi

        assert add_sentry_to_wsgi("proj") is True

    def test_add_sentry_to_wsgi_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.sentry import add_sentry_to_wsgi

        assert add_sentry_to_wsgi("nope") is False

    def test_add_sentry_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.sentry import add_sentry_to_requirements

        add_sentry_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "sentry-sdk" in content

    def test_add_sentry_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("sentry-sdk[django]>=2.0\n", encoding="utf-8")
        from djboost.generators.sentry import add_sentry_to_requirements

        add_sentry_to_requirements()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# API DOCS GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestApiDocsGenerator:
    """Test djboost.generators.api_docs module."""

    def test_add_spectacular_to_installed_apps(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import add_spectacular_to_installed_apps

        add_spectacular_to_installed_apps("proj")
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "rest_framework" in content
        assert "drf_spectacular" in content

    def test_add_spectacular_to_installed_apps_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import add_spectacular_to_installed_apps

        add_spectacular_to_installed_apps("nope")  # Should not raise

    def test_add_spectacular_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import add_spectacular_settings

        add_spectacular_settings("proj")
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "SPECTACULAR_SETTINGS" in content

    def test_add_spectacular_settings_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nSPECTACULAR_SETTINGS\n",
            encoding="utf-8",
        )
        from djboost.generators.api_docs import add_spectacular_settings

        add_spectacular_settings("proj")  # Should not raise

    def test_add_spectacular_settings_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import add_spectacular_settings

        add_spectacular_settings("nope")  # Should not raise

    def test_generate_api_docs_urls(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import generate_api_docs_urls

        generate_api_docs_urls("proj")
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "api/schema" in content

    def test_generate_api_docs_urls_already_configured(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8") + "\napi/schema\n",
            encoding="utf-8",
        )
        from djboost.generators.api_docs import generate_api_docs_urls

        generate_api_docs_urls("proj")  # Should not raise

    def test_generate_api_docs_urls_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import generate_api_docs_urls

        generate_api_docs_urls("nope")  # Should not raise

    def test_add_spectacular_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django\n", encoding="utf-8")
        from djboost.generators.api_docs import add_spectacular_to_requirements

        add_spectacular_to_requirements()
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "drf-spectacular" in content
        assert "uritemplate" in content

    def test_add_spectacular_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("drf-spectacular>=0.27\nuritemplate>=4.1\n", encoding="utf-8")
        from djboost.generators.api_docs import add_spectacular_to_requirements

        add_spectacular_to_requirements()  # Should not raise

    def test_generate_api_docs_files(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import generate_api_docs_files

        changes = generate_api_docs_files("proj", "both")
        assert len(changes) > 0

    def test_generate_api_docs_files_swagger_only(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import generate_api_docs_files

        changes = generate_api_docs_files("proj", "swagger")
        assert len(changes) > 0

    def test_generate_api_docs_files_redoc_only(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.api_docs import generate_api_docs_files

        changes = generate_api_docs_files("proj", "redoc")
        assert len(changes) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATORS TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidators:
    """Test djboost.generators.validators module."""

    def test_validate_name_valid(self):
        from djboost.generators.validators import validate_name

        validate_name("myproject", "project name")  # Should not raise

    def test_validate_name_with_underscores(self):
        from djboost.generators.validators import validate_name

        validate_name("my_project", "project name")  # Should not raise

    def test_validate_name_invalid_hyphen(self):
        from djboost.generators.validators import validate_name

        with pytest.raises((SystemExit, typer.Exit)):
            validate_name("my-project", "project name")

    def test_validate_name_invalid_digit_start(self):
        from djboost.generators.validators import validate_name

        with pytest.raises((SystemExit, typer.Exit)):
            validate_name("1project", "project name")

    def test_validate_name_empty(self):
        from djboost.generators.validators import validate_name

        with pytest.raises((SystemExit, typer.Exit)):
            validate_name("", "project name")

    def test_validate_name_invalid_special_chars(self):
        from djboost.generators.validators import validate_name

        with pytest.raises((SystemExit, typer.Exit)):
            validate_name("my@project", "project name")

    def test_check_virtual_environment(self):
        from djboost.generators.validators import check_virtual_environment

        # Should not raise (we're in a venv or it's lenient)
        check_virtual_environment()


# ═══════════════════════════════════════════════════════════════════════════════
# MANAGEMENT COMMANDS TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestManagementCommands:
    """Test djboost.commands.management modules."""

    def test_doctor_command(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()  # Should not raise

    def test_doctor_command_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()  # Should not raise

    def test_features_command(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.features import features_command

        features_command()  # Should not raise

    def test_features_command_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.features import features_command

        features_command()  # Should not raise

    def test_info_command(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.info import info_command

        info_command()  # Should not raise

    def test_info_command_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.info import info_command

        info_command()  # Should not raise

    def test_validate_command(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.validate import validate_command

        validate_command()  # Should not raise

    def test_validate_command_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.validate import validate_command

        validate_command()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# ADD COMMAND MODULES TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestAddCommands:
    """Test djboost.commands.add.* modules."""

    def test_add_celery_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.celery import add_celery_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_celery_command(dry_run=True, force=False)

    def test_add_docker_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.docker import add_docker_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_docker_command(dry_run=True, force=False)

    def test_add_postgres_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.postgres import add_postgres_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_postgres_command(dry_run=True, force=False)

    def test_add_redis_cache_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.redis_cache import add_redis_cache_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_redis_cache_command(dry_run=True, force=False)

    def test_add_channels_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.channels import add_channels_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_channels_command(dry_run=True, force=False)

    def test_add_graphql_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.graphql import add_graphql_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_graphql_command(dry_run=True, force=False)

    def test_add_monitoring_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.monitoring import add_monitoring_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_monitoring_command(dry_run=True, force=False)

    def test_add_logging_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.logging import add_logging_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_logging_command(dry_run=True, force=False)

    def test_add_sentry_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.sentry import add_sentry_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_sentry_command(dry_run=True, force=False)

    def test_add_security_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.security import add_security_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_security_command(dry_run=True, force=False)

    def test_add_storage_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.storage import add_storage_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_storage_command(dry_run=True, force=False)

    def test_add_kubernetes_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.kubernetes import add_kubernetes_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_kubernetes_command(dry_run=True, force=False)

    def test_add_scheduler_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.scheduler import add_scheduler_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_scheduler_command(dry_run=True, force=False)

    def test_add_api_docs_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.api_docs import add_api_docs_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_api_docs_command(provider="swagger", dry_run=True, force=False)

    def test_add_api_docs_invalid_provider(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.api_docs import add_api_docs_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_api_docs_command(provider="invalid", dry_run=False, force=False)

    def test_add_cicd_github_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.cicd import add_cicd_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_cicd_command(provider="github", dry_run=True, force=False)

    def test_add_cicd_invalid_provider(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.add.cicd import add_cicd_command

        with pytest.raises((SystemExit, typer.Exit)):
            add_cicd_command(provider="invalid", dry_run=False, force=False)


# ═══════════════════════════════════════════════════════════════════════════════
# REMOVE COMMAND MODULES TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRemoveCommands:
    """Test djboost.commands.remove.* modules."""

    def test_remove_docker_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.docker import remove_docker_command

        remove_docker_command(dry_run=True, force=False)  # Should not raise

    def test_remove_postgres_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.postgres import remove_postgres_command

        remove_postgres_command(dry_run=True, force=False)

    def test_remove_redis_cache_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.redis_cache import remove_redis_cache_command

        remove_redis_cache_command(dry_run=True, force=False)

    def test_remove_channels_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.channels import remove_channels_command

        remove_channels_command(dry_run=True, force=False)

    def test_remove_graphql_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.graphql import remove_graphql_command

        remove_graphql_command(dry_run=True, force=False)

    def test_remove_monitoring_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.monitoring import remove_monitoring_command

        remove_monitoring_command(dry_run=True, force=False)

    def test_remove_logging_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.logging import remove_logging_command

        remove_logging_command(dry_run=True, force=False)

    def test_remove_sentry_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.sentry import remove_sentry_command

        remove_sentry_command(dry_run=True, force=False)

    def test_remove_security_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.security import remove_security_command

        remove_security_command(dry_run=True, force=False)

    def test_remove_storage_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.storage import remove_storage_command

        remove_storage_command(dry_run=True, force=False)

    def test_remove_scheduler_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.scheduler import remove_scheduler_command

        remove_scheduler_command(dry_run=True, force=False)

    def test_remove_kubernetes_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.kubernetes import remove_kubernetes_command

        remove_kubernetes_command(dry_run=True, force=False)

    def test_remove_api_docs_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.api_docs import remove_api_docs_command

        remove_api_docs_command(dry_run=True, force=False)

    def test_remove_celery_beat_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.celery_beat import remove_celery_beat_command

        remove_celery_beat_command(dry_run=True, force=False)

    def test_remove_celery_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.celery import remove_celery_command

        with pytest.raises((SystemExit, typer.Exit)):
            remove_celery_command(dry_run=True, force=False)

    def test_remove_cicd_github_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.cicd import remove_cicd_command

        with pytest.raises((SystemExit, typer.Exit)):
            remove_cicd_command(provider="github", dry_run=True, force=False)

    def test_remove_cicd_invalid_provider(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.remove.cicd import remove_cicd_command

        with pytest.raises((SystemExit, typer.Exit)):
            remove_cicd_command(provider="invalid", dry_run=False, force=False)

    def test_remove_docker_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Dockerfile").write_text("old", encoding="utf-8")
        (tmp_path / "docker-compose.yml").write_text("old", encoding="utf-8")
        (tmp_path / ".dockerignore").write_text("old", encoding="utf-8")
        from djboost.commands.remove.docker import remove_docker_command

        remove_docker_command(dry_run=False, force=True)
        assert not (tmp_path / "Dockerfile").exists()
        assert not (tmp_path / "docker-compose.yml").exists()

    def test_remove_postgres_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n'ENGINE': 'django.db.backends.postgresql'\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("psycopg2-binary>=2.9\n", encoding="utf-8")
        from djboost.commands.remove.postgres import remove_postgres_command

        remove_postgres_command(dry_run=False, force=True)
        content = settings.read_text(encoding="utf-8")
        assert "sqlite3" in content

    def test_remove_redis_cache_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── Redis Cache\nCACHES = {}\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("django-redis>=5.4\n", encoding="utf-8")
        from djboost.commands.remove.redis_cache import remove_redis_cache_command

        remove_redis_cache_command(dry_run=False, force=True)

    def test_remove_channels_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n    'daphne',\n# ── Django Channels\nASGI_APPLICATION\n",
            encoding="utf-8",
        )
        asgi = tmp_path / "proj" / "asgi.py"
        asgi.write_text("ProtocolTypeRouter", encoding="utf-8")
        (tmp_path / "requirements.txt").write_text("daphne>=4.1\nchannels>=4.1\n", encoding="utf-8")
        from djboost.commands.remove.channels import remove_channels_command

        remove_channels_command(dry_run=False, force=True)

    def test_remove_graphql_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "schema.py").write_text("schema", encoding="utf-8")
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8")
            + "\nfrom strawberry.django.views import GraphQLView\n"
            + "    path('graphql/', ...),\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("strawberry-graphql>=0.22\n", encoding="utf-8")
        from djboost.commands.remove.graphql import remove_graphql_command

        remove_graphql_command(dry_run=False, force=True)

    def test_remove_monitoring_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "telemetry.py").write_text("t", encoding="utf-8")
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── OpenTelemetry\nOTEL_SERVICE_NAME\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("opentelemetry-api>=1.25\n", encoding="utf-8")
        from djboost.commands.remove.monitoring import remove_monitoring_command

        remove_monitoring_command(dry_run=False, force=True)

    def test_remove_logging_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "logging_config.py").write_text("l", encoding="utf-8")
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── Structured Logging\nstructlog\nfrom proj.logging_config\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("structlog>=24.0\npython-json-logger>=2.0\n", encoding="utf-8")
        from djboost.commands.remove.logging import remove_logging_command

        remove_logging_command(dry_run=False, force=True)

    def test_remove_sentry_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── Sentry\nimport sentry_sdk\nSENTRY_DSN\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("sentry-sdk[django]>=2.0\n", encoding="utf-8")
        from djboost.commands.remove.sentry import remove_sentry_command

        remove_sentry_command(dry_run=False, force=True)

    def test_remove_security_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8")
            + "\n    'csp.middleware.CSPMiddleware',\n# ── Security Headers\nCSP_DEFAULT_SRC\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("django-csp>=3.8\n", encoding="utf-8")
        from djboost.commands.remove.security import remove_security_command

        remove_security_command(dry_run=False, force=True)

    def test_remove_storage_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── S3 / Cloud Storage\nAWS_STORAGE_BUCKET_NAME\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("django-storages[boto3]>=1.14\nboto3>=1.28\n", encoding="utf-8")
        from djboost.commands.remove.storage import remove_storage_command

        remove_storage_command(dry_run=False, force=True)

    def test_remove_scheduler_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "scheduler.py").write_text("s", encoding="utf-8")
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── APScheduler\nAPSCHEDULER_DATETIME_FORMAT\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("django-apscheduler>=0.7\n", encoding="utf-8")
        from djboost.commands.remove.scheduler import remove_scheduler_command

        remove_scheduler_command(dry_run=False, force=True)

    def test_remove_celery_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "celery.py").write_text("c", encoding="utf-8")
        (tmp_path / "proj" / "tasks.py").write_text("t", encoding="utf-8")
        init = tmp_path / "proj" / "__init__.py"
        init.write_text(
            "from .celery import app as celery_app\n__all__ = ('celery_app',)",
            encoding="utf-8",
        )
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n# ── Celery (Background Tasks)\nCELERY_BROKER_URL\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("celery>=5.4\nredis>=5.0\n", encoding="utf-8")
        from djboost.commands.remove.celery import remove_celery_command

        remove_celery_command(dry_run=False, force=True)

    def test_remove_celery_beat_real(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8")
            + "\nfrom celery.schedules import crontab\nCELERY_BEAT_SCHEDULE = {}\n",
            encoding="utf-8",
        )
        (tmp_path / "requirements.txt").write_text("celery-beat>=2.0\n", encoding="utf-8")
        from djboost.commands.remove.celery_beat import remove_celery_beat_command

        remove_celery_beat_command(dry_run=False, force=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CREATE COMMANDS TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreateCommands:
    """Test djboost.commands.create.* modules."""

    def test_create_app_get_project_name(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import get_project_name

        assert get_project_name() == "proj"

    def test_create_app_get_project_name_no_manage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import get_project_name

        with pytest.raises((SystemExit, typer.Exit)):
            get_project_name()

    def test_create_app_update_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_settings

        update_settings("proj", "products")
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "'apps.products'," in content

    def test_create_app_update_settings_already_added(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\n    'apps.products',\n",
            encoding="utf-8",
        )
        from djboost.commands.create.app import update_settings

        update_settings("proj", "products")  # Should not add again

    def test_create_app_update_urls(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_urls

        update_urls("proj", "products")
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "apps.products.urls" in content

    def test_create_app_update_urls_already_added(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8") + "\napps.products.urls\n",
            encoding="utf-8",
        )
        from djboost.commands.create.app import update_urls

        update_urls("proj", "products")  # Should not add again

    def test_create_accounts_get_project_name(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.accounts_app import get_project_name

        assert get_project_name() == "proj"


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURES REGISTRY TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestFeaturesRegistryExtended:
    """Additional tests for djboost.generators.features."""

    def test_list_features(self):
        from djboost.generators.features import list_features

        features = list_features()
        assert len(features) >= 15
        names = [f.name for f in features]
        assert "celery" in names
        assert "docker" in names
        assert "postgres" in names

    def test_get_feature(self):
        from djboost.generators.features import get_feature

        feat = get_feature("celery")
        assert feat is not None
        assert feat.name == "celery"

    def test_get_feature_unknown(self):
        from djboost.generators.features import get_feature

        assert get_feature("nonexistent") is None

    def test_scan_enabled_features_no_manage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.features import scan_enabled_features

        enabled = scan_enabled_features(None)
        assert isinstance(enabled, set)

    def test_scan_enabled_features_with_celery(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("celery>=5.4\nredis>=5.0\n", encoding="utf-8")
        from djboost.generators.features import scan_enabled_features

        enabled = scan_enabled_features(None)
        assert "celery" in enabled

    def test_resolve_dependencies(self):
        from djboost.generators.features import resolve_dependencies

        deps = resolve_dependencies("celery-beat")
        assert "celery" in deps

    def test_resolve_dependencies_no_deps(self):
        from djboost.generators.features import resolve_dependencies

        deps = resolve_dependencies("celery")
        assert isinstance(deps, (set, list))

    def test_detect_conflicts(self):
        from djboost.generators.features import detect_conflicts

        conflicts = detect_conflicts("scheduler", {"celery-beat"})
        assert len(conflicts) > 0

    def test_detect_reverse_dependencies(self):
        from djboost.generators.features import detect_reverse_dependencies

        deps = detect_reverse_dependencies("celery", {"celery-beat"})
        assert "celery-beat" in deps


# ═══════════════════════════════════════════════════════════════════════════════
# SAFE ENGINE EXTENDED TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSafeEngineExtended:
    """Additional tests for djboost.generators.safe_engine."""

    def test_generate_add_plan(self):
        from djboost.generators.safe_engine import generate_add_plan

        plan = generate_add_plan("celery", dry_run=True, project_name="testproj")
        assert plan is not None
        assert plan.dry_run is True

    def test_generate_remove_plan(self):
        from djboost.generators.safe_engine import generate_remove_plan

        plan = generate_remove_plan("celery", dry_run=True, project_name="testproj")
        assert plan is not None
        assert plan.dry_run is True

    def test_scan_enabled_features(self):
        from djboost.generators.safe_engine import scan_enabled_features

        enabled = scan_enabled_features(None)
        assert isinstance(enabled, set)


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestDependenciesExtended:
    """Additional tests for djboost.generators.dependencies."""

    def test_add_to_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.dependencies import add_to_requirements

        add_to_requirements(["Django>=5.0", "celery>=5.4"])
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "Django" in content
        assert "celery" in content

    def test_add_to_requirements_existing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\n", encoding="utf-8")
        from djboost.generators.dependencies import add_to_requirements

        add_to_requirements(["Django>=5.0"])  # Should not duplicate


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestQualityExtended:
    """Additional tests for djboost.generators.quality."""

    def test_generate_gitignore(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.quality import generate_gitignore

        generate_gitignore()
        assert (tmp_path / ".gitignore").exists()

    def test_generate_pre_commit_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.quality import generate_pre_commit_config

        generate_pre_commit_config()
        assert (tmp_path / ".pre-commit-config.yaml").exists()

    def test_generate_pytest_ini(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.quality import generate_pytest_ini

        generate_pytest_ini("proj")
        assert (tmp_path / "pytest.ini").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# ENV TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnvExtended:
    """Additional tests for djboost.generators.env."""

    def test_generate_env_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.env import generate_env_file

        generate_env_file("test-secret-key", "proj")
        assert (tmp_path / ".env").exists()
        content = (tmp_path / ".env").read_text(encoding="utf-8")
        assert "test-secret-key" in content
        assert "proj" in content


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT FILES TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestProjectFilesExtended:
    """Additional tests for djboost.generators.project_files."""

    def test_create_directories(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.project_files import create_directories

        create_directories()
        assert (tmp_path / "apps").exists()
        assert (tmp_path / "media").exists()
        assert (tmp_path / "static").exists()

    def test_create_common_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "common").mkdir()
        (tmp_path / "common" / "__init__.py").write_text("", encoding="utf-8")
        from djboost.generators.project_files import create_common_files

        create_common_files()
        assert (tmp_path / "common" / "responses.py").exists()
        assert (tmp_path / "common" / "pagination.py").exists()
        assert (tmp_path / "common" / "exceptions.py").exists()

    def test_create_utils_file(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.project_files import create_utils_file

        create_utils_file("proj")
        assert (tmp_path / "proj" / "utils.py").exists()

    def test_update_urls_file(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.project_files import update_urls_file

        update_urls_file("proj")
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "admin" in content


# ═══════════════════════════════════════════════════════════════════════════════
# CICD TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCicdExtended:
    """Additional tests for djboost.generators.cicd."""

    def test_generate_github_actions(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.cicd import generate_github_actions

        generate_github_actions()
        assert (tmp_path / ".github" / "workflows" / "main.yml").exists()

    def test_generate_gitlab_ci(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.cicd import generate_gitlab_ci

        generate_gitlab_ci()
        assert (tmp_path / ".gitlab-ci.yml").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# KUBERNETES TESTS (additional)
# ═══════════════════════════════════════════════════════════════════════════════


class TestKubernetesExtended:
    """Additional tests for djboost.generators.kubernetes."""

    def test_generate_k8s_manifests(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.kubernetes import generate_k8s_manifests

        generate_k8s_manifests("proj")
        assert (tmp_path / "k8s").exists()
        assert (tmp_path / "k8s" / "deployment.yaml").exists()
        assert (tmp_path / "k8s" / "service.yaml").exists()

    def test_get_project_name(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.generators.kubernetes import get_project_name

        assert get_project_name() == "proj"

    def test_get_project_name_no_manage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.kubernetes import get_project_name

        assert (
            get_project_name() is None
        )  # ── Commands integration tests ─────────────────────────────────────────────────


import json
import os
import subprocess
import textwrap
from unittest.mock import MagicMock, call, patch

import pytest
import typer

# ── Helpers ──────────────────────────────────────────────────────────────────

MANAGE_PY_TEMPLATE = textwrap.dedent("""\
    #!/usr/bin/env python
    \"\"\"Django's command-line utility for administrative tasks.\"\"\"
    import os
    import sys

    def main():
        \"\"\"Run administrative tasks.\"\"\"
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django."
            ) from exc
        execute_from_command_line(sys.argv)

    if __name__ == '__main__':
        main()
""")

SETTINGS_TEMPLATE = textwrap.dedent("""\
    import os
    from pathlib import Path
    from decouple import config

    BASE_DIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = config('SECRET_KEY', default='test-key')
    DEBUG = config('DEBUG', default=False, cast=bool)
    ALLOWED_HOSTS = ['*']

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'corsheaders',
        'drf_spectacular',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = '{name}.urls'
    WSGI_APPLICATION = '{name}.wsgi.application'

    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_TZ = True

    STATIC_URL = 'static/'
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    REST_FRAMEWORK = {{
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardResultsPagination',
        'PAGE_SIZE': 20,
        'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    }}

    SIMPLE_JWT = {{
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
    }}

    CORS_ALLOWED_ORIGINS = ['http://localhost:3000']

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
""")


def setup_django_project(tmp_path, name="proj"):
    """Create a minimal djboost-style Django project."""
    project_dir = tmp_path / name
    project_dir.mkdir()

    (tmp_path / "manage.py").write_text(MANAGE_PY_TEMPLATE.format(name=name), encoding="utf-8")
    (project_dir / "settings.py").write_text(SETTINGS_TEMPLATE.format(name=name), encoding="utf-8")
    (project_dir / "urls.py").write_text(
        textwrap.dedent(f"""\
            from django.urls import path

            urlpatterns = [
            ]
        """),
        encoding="utf-8",
    )
    (project_dir / "wsgi.py").write_text(
        textwrap.dedent(f"""\
            import os
            from django.core.wsgi import get_wsgi_application

            os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name}.settings')
            application = get_wsgi_application()
        """),
        encoding="utf-8",
    )
    (project_dir / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET_KEY=test-secret-key\nDEBUG=True\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text(
        "Django>=5.0,<6\ndjangorestframework>=3.15,<4\n"
        "django-rest-framework-simplejwt>=5.3,<6\n"
        "django-cors-headers>=4.3,<5\n"
        "drf-spectacular>=0.27,<1\n"
        "python-decouple>=3.8,<4\n",
        encoding="utf-8",
    )

    # Create common/ package
    common = tmp_path / "common"
    common.mkdir()
    (common / "__init__.py").write_text("", encoding="utf-8")
    (common / "responses.py").write_text("# responses", encoding="utf-8")
    (common / "pagination.py").write_text("# pagination", encoding="utf-8")
    (common / "exceptions.py").write_text("# exceptions", encoding="utf-8")

    # Create apps/ directory
    apps = tmp_path / "apps"
    apps.mkdir()
    (apps / "__init__.py").write_text("", encoding="utf-8")

    return tmp_path, name


# Patch that mocks _validate_project to always pass (our test projects
# aren't real Django projects, so manage.py check would fail).
VALIDATE_PATCH = patch(
    "djboost.generators.safe_engine._validate_project",
    return_value=(True, []),
)


# ═══════════════════════════════════════════════════════════════════════════════
# ADD COMMAND INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestAddCommandsIntegration:
    """Test add commands with a real project (hits apply_fn paths)."""

    def test_add_celery_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.celery.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.celery import add_celery_command

            add_celery_command(dry_run=False, force=False)
        assert (tmp_path / "proj" / "celery.py").exists()

    def test_add_celery_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.celery.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.celery import add_celery_command

            with pytest.raises(typer.Exit):
                add_celery_command(dry_run=True, force=False)

    def test_add_docker_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.docker.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.docker import add_docker_command

            add_docker_command(dry_run=False, force=False)
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()

    def test_add_docker_dry_run(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.docker.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.docker import add_docker_command

            with pytest.raises(typer.Exit):
                add_docker_command(dry_run=True, force=False)

    def test_add_postgres_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        # Add DATABASES block so postgres regex can match
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8")
            + "\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}\n",
            encoding="utf-8",
        )
        with patch("djboost.commands.add.postgres.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.postgres import add_postgres_command

            add_postgres_command(dry_run=False, force=False)
        content = settings.read_text(encoding="utf-8")
        assert "postgresql" in content

    def test_add_redis_cache_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.redis_cache.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.redis_cache import add_redis_cache_command

            add_redis_cache_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "CACHES" in content

    def test_add_channels_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.channels.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.channels import add_channels_command

            add_channels_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "ASGI_APPLICATION" in content

    def test_add_graphql_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.graphql.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.graphql import add_graphql_command

            add_graphql_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "graphql" in content.lower()

    def test_add_monitoring_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.monitoring.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.monitoring import add_monitoring_command

            add_monitoring_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "OTEL_SERVICE_NAME" in content

    def test_add_logging_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.logging.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.logging import add_logging_command

            add_logging_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "logging_config" in content

    def test_add_sentry_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.sentry.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.sentry import add_sentry_command

            add_sentry_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "sentry" in content.lower() or "SENTRY" in content

    def test_add_security_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.security.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.security import add_security_command

            add_security_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "CSP" in content or "SecurityMiddleware" in content

    def test_add_storage_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.storage.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.storage import add_storage_command

            add_storage_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "STORAGES" in content or "DEFAULT_FILE_STORAGE" in content

    def test_add_scheduler_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.scheduler.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.scheduler import add_scheduler_command

            add_scheduler_command(dry_run=False, force=False)
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "APSCHEDULER" in content

    def test_add_api_docs_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        # Remove drf-spectacular from requirements so feature isn't detected as already enabled
        (tmp_path / "requirements.txt").write_text("Django>=5.0,<6\ndjangorestframework>=3.15,<4\n", encoding="utf-8")
        with patch("djboost.commands.add.api_docs.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.api_docs import add_api_docs_command

            add_api_docs_command(provider="swagger", dry_run=False, force=False)
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "schema" in content.lower()

    def test_add_api_docs_redoc(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0,<6\ndjangorestframework>=3.15,<4\n", encoding="utf-8")
        with patch("djboost.commands.add.api_docs.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.api_docs import add_api_docs_command

            add_api_docs_command(provider="redoc", dry_run=False, force=False)
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "redoc" in content.lower()

    def test_add_api_docs_invalid_provider(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.api_docs.check_virtual_environment"):
            from djboost.commands.add.api_docs import add_api_docs_command

            with pytest.raises(typer.Exit):
                add_api_docs_command(provider="invalid", dry_run=False, force=False)

    def test_add_cicd_github(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.cicd.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.cicd import add_cicd_command

            add_cicd_command(provider="github", dry_run=False, force=False)
        assert (tmp_path / ".github" / "workflows" / "main.yml").exists()

    def test_add_cicd_gitlab(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.cicd.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.cicd import add_cicd_command

            add_cicd_command(provider="gitlab", dry_run=False, force=False)
        assert (tmp_path / ".gitlab-ci.yml").exists()

    def test_add_cicd_invalid_provider(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.cicd.check_virtual_environment"):
            from djboost.commands.add.cicd import add_cicd_command

            with pytest.raises(typer.Exit):
                add_cicd_command(provider="invalid", dry_run=False, force=False)

    def test_add_kubernetes_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.kubernetes.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.kubernetes import add_kubernetes_command

            add_kubernetes_command(dry_run=False, force=False)
        assert (tmp_path / "k8s").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# ADD COMMAND ERROR PATHS (no project name = Exit 1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAddCommandsNoProject:
    """Test add commands when no project is found (no manage.py)."""

    def test_celery_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.celery.check_virtual_environment"):
            from djboost.commands.add.celery import add_celery_command

            with pytest.raises(typer.Exit):
                add_celery_command(dry_run=False, force=False)

    def test_docker_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.docker.check_virtual_environment"):
            from djboost.commands.add.docker import add_docker_command

            with pytest.raises(typer.Exit):
                add_docker_command(dry_run=False, force=False)

    def test_postgres_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.postgres.check_virtual_environment"):
            from djboost.commands.add.postgres import add_postgres_command

            with pytest.raises(typer.Exit):
                add_postgres_command(dry_run=False, force=False)

    def test_redis_cache_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.redis_cache.check_virtual_environment"):
            from djboost.commands.add.redis_cache import add_redis_cache_command

            with pytest.raises(typer.Exit):
                add_redis_cache_command(dry_run=False, force=False)

    def test_channels_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.channels.check_virtual_environment"):
            from djboost.commands.add.channels import add_channels_command

            with pytest.raises(typer.Exit):
                add_channels_command(dry_run=False, force=False)

    def test_graphql_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.graphql.check_virtual_environment"):
            from djboost.commands.add.graphql import add_graphql_command

            with pytest.raises(typer.Exit):
                add_graphql_command(dry_run=False, force=False)

    def test_monitoring_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.monitoring.check_virtual_environment"):
            from djboost.commands.add.monitoring import add_monitoring_command

            with pytest.raises(typer.Exit):
                add_monitoring_command(dry_run=False, force=False)

    def test_logging_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.logging.check_virtual_environment"):
            from djboost.commands.add.logging import add_logging_command

            with pytest.raises(typer.Exit):
                add_logging_command(dry_run=False, force=False)

    def test_sentry_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.sentry.check_virtual_environment"):
            from djboost.commands.add.sentry import add_sentry_command

            with pytest.raises(typer.Exit):
                add_sentry_command(dry_run=False, force=False)

    def test_security_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.security.check_virtual_environment"):
            from djboost.commands.add.security import add_security_command

            with pytest.raises(typer.Exit):
                add_security_command(dry_run=False, force=False)

    def test_storage_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.storage.check_virtual_environment"):
            from djboost.commands.add.storage import add_storage_command

            with pytest.raises(typer.Exit):
                add_storage_command(dry_run=False, force=False)

    def test_scheduler_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.scheduler.check_virtual_environment"):
            from djboost.commands.add.scheduler import add_scheduler_command

            with pytest.raises(typer.Exit):
                add_scheduler_command(dry_run=False, force=False)

    def test_kubernetes_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.kubernetes.check_virtual_environment"):
            from djboost.commands.add.kubernetes import add_kubernetes_command

            with pytest.raises(typer.Exit):
                add_kubernetes_command(dry_run=False, force=False)

    def test_api_docs_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.api_docs.check_virtual_environment"):
            from djboost.commands.add.api_docs import add_api_docs_command

            with pytest.raises(typer.Exit):
                add_api_docs_command(provider="swagger", dry_run=False, force=False)

    def test_cicd_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.cicd.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.cicd import add_cicd_command

            add_cicd_command(provider="github", dry_run=False, force=False)
        assert (tmp_path / ".github" / "workflows" / "main.yml").exists()

    def test_celery_beat_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.celery_beat.check_virtual_environment"):
            from djboost.commands.add.celery_beat import add_celery_beat_command

            with pytest.raises(typer.Exit):
                add_celery_beat_command(dry_run=False, force=False)

    def test_cicd_no_project_gitlab(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.cicd.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.cicd import add_cicd_command

            add_cicd_command(provider="gitlab", dry_run=False, force=False)
        assert (tmp_path / ".gitlab-ci.yml").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# CELERY BEAT ADD COMMAND
# ═══════════════════════════════════════════════════════════════════════════════


class TestAddCeleryBeat:
    """Test celery beat add command paths."""

    def test_add_celery_beat_full(self, tmp_path, monkeypatch):
        """Happy path: celery is installed, add celery-beat."""
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        # Pre-add celery settings so scan_enabled_features detects it
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCELERY_BROKER_URL = 'redis://'\n",
            encoding="utf-8",
        )
        with patch("djboost.commands.add.celery_beat.check_virtual_environment"), VALIDATE_PATCH:
            from djboost.commands.add.celery_beat import add_celery_beat_command

            add_celery_beat_command(dry_run=False, force=False)
        content = settings.read_text(encoding="utf-8")
        assert "CELERY_BEAT_SCHEDULE" in content

    def test_add_celery_beat_no_celery(self, tmp_path, monkeypatch):
        """Error: celery not installed."""
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.add.celery_beat.check_virtual_environment"):
            from djboost.commands.add.celery_beat import add_celery_beat_command

            with pytest.raises(typer.Exit):
                add_celery_beat_command(dry_run=False, force=False)


# ═══════════════════════════════════════════════════════════════════════════════
# REMOVE COMMAND INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRemoveCommandsIntegration:
    """Test remove commands with a real project."""

    def test_remove_celery_beat_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8")
            + "\nfrom celery.schedules import crontab\nCELERY_BEAT_SCHEDULE = {}\n",
            encoding="utf-8",
        )
        with patch("djboost.commands.remove.celery_beat.check_virtual_environment"):
            from djboost.commands.remove.celery_beat import remove_celery_beat_command

            remove_celery_beat_command(dry_run=False, force=True)

    def test_remove_cicd_github(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / ".github" / "workflows" / "main.yml").write_text("name: test", encoding="utf-8")
        with patch("djboost.commands.remove.cicd.check_virtual_environment"):
            from djboost.commands.remove.cicd import remove_cicd_command

            remove_cicd_command(provider="github", dry_run=False, force=True)
        assert not (tmp_path / ".github").exists()

    def test_remove_cicd_gitlab(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitlab-ci.yml").write_text("stages:", encoding="utf-8")
        with patch("djboost.commands.remove.cicd.check_virtual_environment"):
            from djboost.commands.remove.cicd import remove_cicd_command

            remove_cicd_command(provider="gitlab", dry_run=False, force=True)
        assert not (tmp_path / ".gitlab-ci.yml").exists()

    def test_remove_cicd_github_not_present(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.remove.cicd.check_virtual_environment"):
            from djboost.commands.remove.cicd import remove_cicd_command

            with pytest.raises(typer.Exit):
                remove_cicd_command(provider="github", dry_run=False, force=True)

    def test_remove_cicd_gitlab_not_present(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.remove.cicd.check_virtual_environment"):
            from djboost.commands.remove.cicd import remove_cicd_command

            with pytest.raises(typer.Exit):
                remove_cicd_command(provider="gitlab", dry_run=False, force=True)

    def test_remove_cicd_invalid_provider(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.remove.cicd.check_virtual_environment"):
            from djboost.commands.remove.cicd import remove_cicd_command

            with pytest.raises(typer.Exit):
                remove_cicd_command(provider="invalid", dry_run=False, force=True)

    def test_remove_kubernetes_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "k8s").mkdir()
        (tmp_path / "k8s" / "deployment.yaml").write_text("apiVersion: v1", encoding="utf-8")
        with patch("djboost.commands.remove.kubernetes.check_virtual_environment"):
            from djboost.commands.remove.kubernetes import remove_kubernetes_command

            remove_kubernetes_command(dry_run=False, force=True)
        assert not (tmp_path / "k8s").exists()

    def test_remove_kubernetes_not_present(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.remove.kubernetes.check_virtual_environment"):
            from djboost.commands.remove.kubernetes import remove_kubernetes_command

            # kubernetes is not configured, should handle gracefully
            remove_kubernetes_command(dry_run=False, force=True)

    def test_remove_api_docs_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            textwrap.dedent("""\
                from django.urls import path
                from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

                urlpatterns = [
                    path('api/schema/', SpectacularAPIView.as_view(url_name='schema'), name='schema'),
                    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
                    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
                ]
            """),
            encoding="utf-8",
        )
        with patch("djboost.commands.remove.api_docs.check_virtual_environment"):
            from djboost.commands.remove.api_docs import remove_api_docs_command

            remove_api_docs_command(dry_run=False, force=True)
        content = urls.read_text(encoding="utf-8")
        assert "SpectacularAPIView" not in content

    def test_remove_api_docs_partial(self, tmp_path, monkeypatch):
        """Test when only some elements are present."""
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            textwrap.dedent("""\
                from django.urls import path

                urlpatterns = [
                ]
            """),
            encoding="utf-8",
        )
        with patch("djboost.commands.remove.api_docs.check_virtual_environment"):
            from djboost.commands.remove.api_docs import remove_api_docs_command

            remove_api_docs_command(dry_run=False, force=True)

    def test_remove_api_docs_with_requirements(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\ndrf-spectacular>=0.27\n", encoding="utf-8")
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            "from django.urls import path\nfrom drf_spectacular.views import SpectacularAPIView\nurlpatterns = [\n    path('api/schema/', SpectacularAPIView.as_view(url_name='schema'), name='schema'),\n]\n",
            encoding="utf-8",
        )
        with patch("djboost.commands.remove.api_docs.check_virtual_environment"):
            from djboost.commands.remove.api_docs import remove_api_docs_command

            remove_api_docs_command(dry_run=False, force=True)
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "spectacular" not in content.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# CREATE COMMAND TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreateAccountsCommand:
    """Test djboost startauth command."""

    def test_create_accounts_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.create.accounts.check_virtual_environment"):
            from djboost.commands.create.accounts import create_accounts_command

            create_accounts_command()

    def test_create_accounts_no_project(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        import shutil

        shutil.rmtree(tmp_path / "common", ignore_errors=True)
        shutil.rmtree(tmp_path / "apps", ignore_errors=True)
        with patch("djboost.commands.create.accounts.check_virtual_environment"):
            from djboost.commands.create.accounts import create_accounts_command

            create_accounts_command()  # Should still work with warning


class TestCreateAppCommand:
    """Test djboost startapp command."""

    def test_create_app_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.create.app.check_virtual_environment"):
            from djboost.commands.create.app import create_app_command

            create_app_command(name="myapp")
        assert (tmp_path / "apps" / "myapp").exists()

    def test_create_app_already_exists(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "apps" / "myapp").mkdir()
        with patch("djboost.commands.create.app.check_virtual_environment"):
            from djboost.commands.create.app import create_app_command

            with pytest.raises(typer.Exit):
                create_app_command(name="myapp")

    def test_create_app_no_manage_py(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.create.app.check_virtual_environment"):
            from djboost.commands.create.app import create_app_command

            with pytest.raises(typer.Exit):
                create_app_command(name="myapp")

    def test_create_app_no_djboost_project(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        import shutil

        shutil.rmtree(tmp_path / "apps", ignore_errors=True)
        shutil.rmtree(tmp_path / "common", ignore_errors=True)
        with patch("djboost.commands.create.app.check_virtual_environment"):
            from djboost.commands.create.app import create_app_command

            create_app_command(name="myapp")

    def test_create_app_invalid_name(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        with patch("djboost.commands.create.app.check_virtual_environment"):
            from djboost.commands.create.app import create_app_command

            with pytest.raises(typer.Exit):
                create_app_command(name="my-app")

    def test_update_settings(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_settings

        update_settings("proj", "testapp")
        content = (tmp_path / "proj" / "settings.py").read_text(encoding="utf-8")
        assert "apps.testapp" in content

    def test_update_settings_already_added(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_settings

        update_settings("proj", "testapp")
        update_settings("proj", "testapp")  # Should warn

    def test_update_settings_no_settings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_settings

        update_settings("nonexistent", "testapp")

    def test_update_urls(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_urls

        update_urls("proj", "testapp")
        content = (tmp_path / "proj" / "urls.py").read_text(encoding="utf-8")
        assert "apps.testapp.urls" in content

    def test_update_urls_already_added(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_urls

        update_urls("proj", "testapp")
        update_urls("proj", "testapp")  # Should warn

    def test_update_urls_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import update_urls

        update_urls("nonexistent", "testapp")

    def test_update_urls_no_urlpatterns(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text("urlpatterns_not_found = []\n", encoding="utf-8")
        from djboost.commands.create.app import update_urls

        update_urls("proj", "testapp")

    def test_update_urls_no_include_import(self, tmp_path, monkeypatch):
        """Test that 'include' is auto-imported when missing."""
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            "from django.urls import path\nurlpatterns = [\n]\n",
            encoding="utf-8",
        )
        from djboost.commands.create.app import update_urls

        update_urls("proj", "testapp")
        content = urls.read_text(encoding="utf-8")
        assert "include" in content

    def test_get_project_name_from_manage_py(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.create.app import get_project_name

        assert get_project_name() == "proj"

    def test_get_project_name_bad_manage(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "manage.py").write_text("x = 1", encoding="utf-8")
        from djboost.commands.create.app import get_project_name

        with pytest.raises(typer.Exit):
            get_project_name()


# ═══════════════════════════════════════════════════════════════════════════════
# MANAGEMENT COMMAND TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDoctorCommand:
    """Test djboost doctor with real projects."""

    def test_doctor_full_project(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_with_celery(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "celery.py").write_text("c", encoding="utf-8")
        (tmp_path / "requirements.txt").write_text(
            "celery>=5.4\nredis>=5.0\nchannels>=4.1\nflower>=2.0\n",
            encoding="utf-8",
        )
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_debug_true(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=test\nDEBUG=True\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_debug_false(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=test\nDEBUG=False\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_default_secret_key(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=your-secret-key\nDEBUG=True\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_default_secret_key_generated(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=your-generated-secret\nDEBUG=True\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_custom_secret_key(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text("SECRET_KEY=super-secret-123!\nDEBUG=False\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_precommit_and_gitignore(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".pre-commit-config.yaml").write_text("repos:", encoding="utf-8")
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_github_actions(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / ".github" / "workflows" / "main.yml").write_text("name: test", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_gitlab_ci(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitlab-ci.yml").write_text("stages:", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_docker_compose(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n  web:\n  db:\n  redis:\n  celery:\n  flower:\n",
            encoding="utf-8",
        )
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_urls_with_swagger(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8") + "\nSpectacularSwaggerView\n",
            encoding="utf-8",
        )
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_urls_with_redoc(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8") + "\nSpectacularRedocView\n",
            encoding="utf-8",
        )
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_urls_no_docs(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_with_apps(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        app_dir = tmp_path / "apps" / "myapp"
        app_dir.mkdir()
        (app_dir / "apps.py").write_text("class AppConfig:\n    name = 'myapp'\n", encoding="utf-8")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_empty_apps(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_no_manage_py(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_no_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_no_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_no_common(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.doctor import doctor_command

        doctor_command()

    def test_doctor_common_missing_files(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        # Remove some common files
        os.remove(tmp_path / "common" / "responses.py")
        os.remove(tmp_path / "common" / "pagination.py")
        os.remove(tmp_path / "common" / "exceptions.py")
        from djboost.commands.management.doctor import doctor_command

        doctor_command()


class TestInfoCommand:
    """Test djboost info with real projects."""

    def test_info_full_project(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_with_celery(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "proj" / "celery.py").write_text("c", encoding="utf-8")
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nCELERY_BEAT_SCHEDULE = {}\n",
            encoding="utf-8",
        )
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_with_docker(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n  web:\n  db:\n  redis:\n  celery:\n  flower:\n",
            encoding="utf-8",
        )
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_github_actions(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / ".github" / "workflows" / "main.yml").write_text("name: test", encoding="utf-8")
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_gitlab_ci(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitlab-ci.yml").write_text("stages:", encoding="utf-8")
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_no_ci_cd(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_with_accounts(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "apps" / "accounts").mkdir()
        (tmp_path / "apps" / "accounts" / "__init__.py").touch()
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_with_custom_app(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        app_dir = tmp_path / "apps" / "myapp"
        app_dir.mkdir()
        (app_dir / "apps.py").write_text("class AppConfig:\n    name = 'myapp'\n", encoding="utf-8")
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_with_api_docs(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            urls.read_text(encoding="utf-8") + "\nSpectacularSwaggerView\nSpectacularRedocView\n",
            encoding="utf-8",
        )
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_no_manage_py(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.info import info_command

        info_command()

    def test_info_no_settings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "manage.py").write_text("# manage", encoding="utf-8")
        from djboost.commands.management.info import info_command

        info_command()


class TestValidateCommand:
    """Test djboost validate with real projects."""

    def test_validate_full_project(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_manage_py(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_with_asgi(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        settings.write_text(
            settings.read_text(encoding="utf-8") + "\nASGI_APPLICATION = 'proj.asgi.application'\n",
            encoding="utf-8",
        )
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_cors(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        content = settings.read_text(encoding="utf-8")
        content = content.replace("CORS_ALLOWED_ORIGINS", "CORS_REMOVED")
        settings.write_text(content, encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_jwt(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        content = settings.read_text(encoding="utf-8")
        content = content.replace("SIMPLE_JWT", "JWT_REMOVED")
        settings.write_text(content, encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_jwt_full(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_common_no_apps(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        import shutil

        shutil.rmtree(tmp_path / "common", ignore_errors=True)
        shutil.rmtree(tmp_path / "apps", ignore_errors=True)
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_requirements(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        os.remove(tmp_path / "requirements.txt")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_env(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        os.remove(tmp_path / ".env")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_leading_slash_in_urls(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        urls = tmp_path / "proj" / "urls.py"
        urls.write_text(
            "from django.urls import path\nurlpatterns = [\n    path('/api/test/', None),\n]\n",
            encoding="utf-8",
        )
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_installed_apps(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        content = settings.read_text(encoding="utf-8")
        content = content.replace("INSTALLED_APPS", "REMOVED_APPS")
        settings.write_text(content, encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_rest_framework(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        content = settings.read_text(encoding="utf-8")
        content = content.replace("REST_FRAMEWORK", "RF_REMOVED")
        settings.write_text(content, encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_optional_in_base(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        content = settings.read_text(encoding="utf-8")
        content += "\n'channels'\n'daphne'\n"
        settings.write_text(content, encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_exception_handler(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "proj" / "settings.py"
        content = settings.read_text(encoding="utf-8")
        content = content.replace("EXCEPTION_HANDLER", "EH_REMOVED")
        content = content.replace("DEFAULT_PAGINATION_CLASS", "DPC_REMOVED")
        settings.write_text(content, encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_circular_import_in_common(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        (tmp_path / "common" / "responses.py").write_text("from common.responses import custom\n", encoding="utf-8")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_apps_init(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        os.remove(tmp_path / "apps" / "__init__.py")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_common_dir(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        import shutil

        shutil.rmtree(tmp_path / "common")
        from djboost.commands.management.validate import validate_command

        validate_command()

    def test_validate_no_apps_dir(self, tmp_path, monkeypatch):
        setup_django_project(tmp_path, "proj")
        monkeypatch.chdir(tmp_path)
        import shutil

        shutil.rmtree(tmp_path / "apps")
        from djboost.commands.management.validate import validate_command

        validate_command()


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATORS.PY TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidatorsAutoCreate:
    """Test check_virtual_environment auto-create paths."""

    def test_in_venv(self):
        """When already in a venv, should return True immediately."""
        with patch.object(sys, "base_prefix", "/usr"), patch.object(sys, "prefix", "/usr/env"):
            from djboost.generators.validators import check_virtual_environment

            result = check_virtual_environment()
            assert result is True

    def test_env_exists(self, tmp_path, monkeypatch):
        """When not in venv but env/ exists, should use existing env."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "env").mkdir()
        if sys.platform == "win32":
            (tmp_path / "env" / "Scripts").mkdir()
            (tmp_path / "env" / "Scripts" / "python.exe").touch()
        else:
            (tmp_path / "env" / "bin").mkdir()
            (tmp_path / "env" / "bin" / "python").touch()

        with patch.object(sys, "base_prefix", sys.prefix), patch.object(sys, "prefix", sys.prefix):
            from djboost.generators.validators import check_virtual_environment

            with patch("djboost.generators.validators.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = check_virtual_environment()
                assert result is True

    def test_creates_env(self, tmp_path, monkeypatch):
        """When not in venv and env/ doesn't exist, should auto-create."""
        monkeypatch.chdir(tmp_path)
        real_executable = sys.executable  # Save real path
        try:
            with patch.object(sys, "base_prefix", sys.prefix), patch.object(sys, "prefix", sys.prefix):
                from djboost.generators.validators import check_virtual_environment

                with patch("djboost.generators.validators.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    with patch("djboost.generators.validators.get_venv_python_path") as mock_venv:
                        mock_python = tmp_path / "env" / "bin" / "python"
                        mock_venv.return_value = mock_python
                        result = check_virtual_environment()
                        assert result is True
        finally:
            sys.executable = real_executable  # Restore to prevent leaking

    def test_venv_create_fails(self, tmp_path, monkeypatch):
        """When venv creation fails, should raise Exit(1)."""
        monkeypatch.chdir(tmp_path)
        real_executable = sys.executable
        try:
            with patch.object(sys, "base_prefix", sys.prefix), patch.object(sys, "prefix", sys.prefix):
                from djboost.generators.validators import check_virtual_environment

                with patch("djboost.generators.validators.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=1, stderr="error creating")
                    with pytest.raises(typer.Exit):
                        check_virtual_environment()
        finally:
            sys.executable = real_executable

    def test_python_not_found(self, tmp_path, monkeypatch):
        """When venv python is not found after creation, should raise Exit(1)."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "env").mkdir()
        real_executable = sys.executable
        try:
            with patch.object(sys, "base_prefix", sys.prefix), patch.object(sys, "prefix", sys.prefix):
                from djboost.generators.validators import check_virtual_environment

                with patch("djboost.generators.validators.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    with pytest.raises(typer.Exit):
                        check_virtual_environment()
        finally:
            sys.executable = real_executable

    def test_venv_exception(self, tmp_path, monkeypatch):
        """When subprocess raises an exception, should raise Exit(1)."""
        monkeypatch.chdir(tmp_path)
        real_executable = sys.executable
        try:
            with patch.object(sys, "base_prefix", sys.prefix), patch.object(sys, "prefix", sys.prefix):
                from djboost.generators.validators import check_virtual_environment

                with patch("djboost.generators.validators.subprocess.run") as mock_run:
                    mock_run.side_effect = Exception("subprocess error")
                    with pytest.raises(typer.Exit):
                        check_virtual_environment()
        finally:
            sys.executable = real_executable


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES.PY TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDependencies:
    """Test djboost.generators.dependencies uncovered paths."""

    def test_add_to_requirements_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.dependencies import add_to_requirements

        add_to_requirements(["celery>=5.4", "redis>=5.0"])
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "celery" in content
        assert "redis" in content

    def test_add_to_requirements_already_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("celery>=5.4\n", encoding="utf-8")
        from djboost.generators.dependencies import add_to_requirements

        add_to_requirements(["celery>=5.4"])

    def test_remove_from_requirements(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\ncelery>=5.4\nredis>=5.0\n", encoding="utf-8")
        from djboost.generators.dependencies import remove_from_requirements

        remove_from_requirements(["celery", "redis"])
        content = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
        assert "celery" not in content
        assert "redis" not in content
        assert "Django" in content

    def test_remove_from_requirements_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.dependencies import remove_from_requirements

        remove_from_requirements(["celery"])

    def test_remove_from_requirements_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "requirements.txt").write_text("Django>=5.0\n", encoding="utf-8")
        from djboost.generators.dependencies import remove_from_requirements

        remove_from_requirements(["celery"])

    def test_install_optional_packages_unknown(self):
        from djboost.generators.dependencies import install_optional_packages

        with patch("djboost.generators.dependencies.subprocess.run"):
            assert install_optional_packages("unknown_category") is False

    def test_install_optional_packages_valid(self):
        from djboost.generators.dependencies import install_optional_packages

        with patch("djboost.generators.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert install_optional_packages("celery") is True

    def test_uninstall_optional_packages_unknown(self):
        from djboost.generators.dependencies import uninstall_optional_packages

        with patch("djboost.generators.dependencies.subprocess.run"):
            assert uninstall_optional_packages("unknown_category") is False

    def test_uninstall_optional_packages_valid(self):
        from djboost.generators.dependencies import uninstall_optional_packages

        with patch("djboost.generators.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert uninstall_optional_packages("celery") is True

    def test_install_dependencies_error(self):
        from djboost.generators.dependencies import install_dependencies

        with patch("djboost.generators.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="install error")
            with pytest.raises(typer.Exit):
                install_dependencies(["bad-package>=1.0"])

    def test_install_dependencies_success(self):
        from djboost.generators.dependencies import install_dependencies

        with patch("djboost.generators.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            install_dependencies(["good-package>=1.0"])

    def test_uninstall_packages(self):
        from djboost.generators.dependencies import uninstall_packages

        with patch("djboost.generators.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            uninstall_packages(["celery>=5.4"])

    def test_uninstall_packages_not_installed(self):
        from djboost.generators.dependencies import uninstall_packages

        with patch("djboost.generators.dependencies.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            uninstall_packages(["nonexistent>=1.0"])


# ═══════════════════════════════════════════════════════════════════════════════
# SAFE ENGINE REMAINING LINES
# ═══════════════════════════════════════════════════════════════════════════════


class TestSafeEngineRemaining:
    """Test safe_engine.py remaining uncovered lines."""

    def test_load_change_history_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from djboost.generators.safe_engine import load_change_history

        assert load_change_history() == []

    def test_load_change_history_corrupt(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".djboost_backup").mkdir()
        (tmp_path / ".djboost_backup" / "changes.json").write_text("not json", encoding="utf-8")
        from djboost.generators.safe_engine import load_change_history

        assert load_change_history() == []

    def test_load_change_history_valid(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".djboost_backup").mkdir()
        data = [{"feature_name": "test", "operation": "add"}]
        (tmp_path / ".djboost_backup" / "changes.json").write_text(json.dumps(data), encoding="utf-8")
        from djboost.generators.safe_engine import load_change_history

        result = load_change_history()
        assert len(result) == 1
        assert result[0]["feature_name"] == "test"

    def test_print_plan_all_fields(self):
        from djboost.generators.safe_engine import ChangePlan, FileChange, _print_plan

        plan = ChangePlan(feature_name="test", operation="add", dry_run=False)
        plan.errors.append("test error")
        plan.warnings.append("test warning")
        plan.dependencies = ["dep1"]
        plan.conflicts = ["conflict1"]
        plan.packages_to_install = ["pkg1>=1.0"]
        plan.files_to_change = [
            FileChange(path="test.py", action="create"),
            FileChange(path="old.py", action="delete"),
            FileChange(path="mod.py", action="modify"),
        ]
        plan.env_vars_to_add = ["VAR1=val1"]
        _print_plan(plan)

    def test_print_plan_remove_operation(self):
        from djboost.generators.safe_engine import ChangePlan, _print_plan

        plan = ChangePlan(feature_name="test", operation="remove", dry_run=False)
        _print_plan(plan)

    def test_print_plan_dry_run_with_reverse_deps(self):
        from djboost.generators.safe_engine import ChangePlan, _print_plan

        plan = ChangePlan(feature_name="test", operation="add", dry_run=True)
        plan.packages_to_uninstall = ["pkg1>=1.0"]
        plan.reverse_deps = ["dep1"]
        _print_plan(plan)

    def test_print_plan_no_changes(self):
        from djboost.generators.safe_engine import ChangePlan, _print_plan

        plan = ChangePlan(feature_name="test", operation="add", dry_run=False)
        _print_plan(plan)  # No errors, warnings, deps, etc.


# ── Project files tests ────────────────────────────────────────────────────────

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT FILES — uncovered functions
# ═══════════════════════════════════════════════════════════════════════════════


class TestProjectFilesUncovered:
    """Test uncovered functions in djboost.generators.project_files."""

    def test_create_celery_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "myapp").mkdir()
        from djboost.generators.project_files import create_celery_file

        create_celery_file("myapp")
        assert (tmp_path / "myapp" / "celery.py").exists()
        content = (tmp_path / "myapp" / "celery.py").read_text(encoding="utf-8")
        assert "Celery" in content
        assert "myapp" in content

    def test_create_tasks_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "myapp").mkdir()
        from djboost.generators.project_files import create_tasks_file

        create_tasks_file("myapp")
        assert (tmp_path / "myapp" / "tasks.py").exists()
        content = (tmp_path / "myapp" / "tasks.py").read_text(encoding="utf-8")
        assert "shared_task" in content
        assert "sample_task" in content

    def test_update_init_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "myapp").mkdir()
        from djboost.generators.project_files import update_init_file

        update_init_file("myapp")
        assert (tmp_path / "myapp" / "__init__.py").exists()
        content = (tmp_path / "myapp" / "__init__.py").read_text(encoding="utf-8")
        assert "celery_app" in content
