import typer

# Create commands
from djboost.commands.create.project import create_project_command
from djboost.commands.create.app import create_app_command
from djboost.commands.create.accounts import create_accounts_command

# Add commands
from djboost.commands.add.celery import add_celery_command
from djboost.commands.add.celery_beat import add_celery_beat_command
from djboost.commands.add.docker import add_docker_command
from djboost.commands.add.api_docs import add_api_docs_command
from djboost.commands.add.cicd import add_cicd_command

# Remove commands
from djboost.commands.remove.celery import remove_celery_command
from djboost.commands.remove.celery_beat import remove_celery_beat_command
from djboost.commands.remove.docker import remove_docker_command
from djboost.commands.remove.api_docs import remove_api_docs_command
from djboost.commands.remove.cicd import remove_cicd_command

# Management commands
from djboost.commands.management.doctor import doctor_command
from djboost.commands.management.validate import validate_command
from djboost.commands.management.info import info_command

app = typer.Typer(help="djboost — Django project generator CLI")
create = typer.Typer(help="Create a new project or app")
add = typer.Typer(help="Add integrations to your project")
remove = typer.Typer(help="Remove integrations from your project")

app.add_typer(create, name="create")
app.add_typer(add, name="add")
app.add_typer(remove, name="remove")

create.command("project")(create_project_command)
create.command("app")(create_app_command)
create.command("accounts")(create_accounts_command)

add.command("celery")(add_celery_command)
add.command("celery-beat")(add_celery_beat_command)
add.command("docker")(add_docker_command)
add.command("api-docs")(add_api_docs_command)
add.command("cicd")(add_cicd_command)

remove.command("celery")(remove_celery_command)
remove.command("celery-beat")(remove_celery_beat_command)
remove.command("docker")(remove_docker_command)
remove.command("api-docs")(remove_api_docs_command)
remove.command("cicd")(remove_cicd_command)

app.command("doctor")(doctor_command)
app.command("validate")(validate_command)
app.command("info")(info_command)


def version_callback(value: bool):
    if value:
        typer.echo("djboost version 0.4.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit."
    )
):
    pass
