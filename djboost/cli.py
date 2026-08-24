import typer

from djboost.commands.add.api_docs import add_api_docs_command

# Add commands
from djboost.commands.add.celery import add_celery_command
from djboost.commands.add.celery_beat import add_celery_beat_command
from djboost.commands.add.channels import add_channels_command
from djboost.commands.add.cicd import add_cicd_command
from djboost.commands.add.docker import add_docker_command
from djboost.commands.add.graphql import add_graphql_command
from djboost.commands.add.kubernetes import add_kubernetes_command
from djboost.commands.add.logging import add_logging_command
from djboost.commands.add.monitoring import add_monitoring_command
from djboost.commands.add.postgres import add_postgres_command
from djboost.commands.add.redis_cache import add_redis_cache_command
from djboost.commands.add.scheduler import add_scheduler_command
from djboost.commands.add.security import add_security_command
from djboost.commands.add.sentry import add_sentry_command
from djboost.commands.add.storage import add_storage_command
from djboost.commands.create.accounts import create_accounts_command
from djboost.commands.create.app import create_app_command

# Create commands
from djboost.commands.create.project import create_project_command

# Management commands
from djboost.commands.management.doctor import doctor_command
from djboost.commands.management.features import features_command
from djboost.commands.management.info import info_command
from djboost.commands.management.validate import validate_command
from djboost.commands.remove.api_docs import remove_api_docs_command

# Remove commands
from djboost.commands.remove.celery import remove_celery_command
from djboost.commands.remove.celery_beat import remove_celery_beat_command
from djboost.commands.remove.channels import remove_channels_command
from djboost.commands.remove.cicd import remove_cicd_command
from djboost.commands.remove.docker import remove_docker_command
from djboost.commands.remove.graphql import remove_graphql_command
from djboost.commands.remove.kubernetes import remove_kubernetes_command
from djboost.commands.remove.logging import remove_logging_command
from djboost.commands.remove.monitoring import remove_monitoring_command
from djboost.commands.remove.postgres import remove_postgres_command
from djboost.commands.remove.redis_cache import remove_redis_cache_command
from djboost.commands.remove.scheduler import remove_scheduler_command
from djboost.commands.remove.security import remove_security_command
from djboost.commands.remove.sentry import remove_sentry_command
from djboost.commands.remove.storage import remove_storage_command

app = typer.Typer(help="djboost — Django project generator CLI")
add = typer.Typer(help="Add integrations to your project")
remove = typer.Typer(help="Remove integrations from your project")

app.add_typer(add, name="add")
app.add_typer(remove, name="remove")

# ── Create commands (top-level) ───────────────────────────────────────────────
app.command("startproject")(create_project_command)
app.command("startapp")(create_app_command)
app.command("startauth")(create_accounts_command)

# ── Add commands ──────────────────────────────────────────────────────────────
add.command("celery")(add_celery_command)
add.command("celery-beat")(add_celery_beat_command)
add.command("scheduler")(add_scheduler_command)
add.command("docker")(add_docker_command)
add.command("kubernetes")(add_kubernetes_command)
add.command("postgres")(add_postgres_command)
add.command("redis-cache")(add_redis_cache_command)
add.command("api-docs")(add_api_docs_command)
add.command("cicd")(add_cicd_command)
add.command("storage")(add_storage_command)
add.command("graphql")(add_graphql_command)
add.command("channels")(add_channels_command)
add.command("security")(add_security_command)
add.command("logging")(add_logging_command)
add.command("sentry")(add_sentry_command)
add.command("monitoring")(add_monitoring_command)

# ── Remove commands ───────────────────────────────────────────────────────────
remove.command("celery")(remove_celery_command)
remove.command("celery-beat")(remove_celery_beat_command)
remove.command("scheduler")(remove_scheduler_command)
remove.command("docker")(remove_docker_command)
remove.command("kubernetes")(remove_kubernetes_command)
remove.command("postgres")(remove_postgres_command)
remove.command("redis-cache")(remove_redis_cache_command)
remove.command("api-docs")(remove_api_docs_command)
remove.command("cicd")(remove_cicd_command)
remove.command("storage")(remove_storage_command)
remove.command("graphql")(remove_graphql_command)
remove.command("channels")(remove_channels_command)
remove.command("security")(remove_security_command)
remove.command("logging")(remove_logging_command)
remove.command("sentry")(remove_sentry_command)
remove.command("monitoring")(remove_monitoring_command)

# ── Management commands ───────────────────────────────────────────────────────
app.command("doctor")(doctor_command)
app.command("validate")(validate_command)
app.command("info")(info_command)
app.command("features")(features_command)


def version_callback(value: bool):
    if value:
        typer.echo("djboost version 0.6.3")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    )
):
    pass
