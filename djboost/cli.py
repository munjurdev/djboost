import typer
from djboost.commands.create_project import create_project_command
from djboost.commands.create_app import create_app_command
from djboost.commands.create_accounts import create_accounts_command
from djboost.commands.add_cicd import add_cicd_command
from djboost.commands.remove_cicd import remove_cicd_command
from djboost.commands.add_celery import add_celery_command
from djboost.commands.add_celery_beat import add_celery_beat_command
from djboost.commands.add_docker import add_docker_command
from djboost.commands.add_api_docs import add_api_docs_command
from djboost.commands.remove_celery import remove_celery_command

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
add.command("cicd")(add_cicd_command)
add.command("celery")(add_celery_command)
add.command("celery-beat")(add_celery_beat_command)
add.command("docker")(add_docker_command)
add.command("api-docs")(add_api_docs_command)
remove.command("cicd")(remove_cicd_command)
remove.command("celery")(remove_celery_command)


def version_callback(value: bool):
    if value:
        typer.echo("djboost version 0.3.0")
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
