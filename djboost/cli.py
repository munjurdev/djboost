import typer
from djboost.commands.create_project import create_project_command
from djboost.commands.create_app import create_app_command
from djboost.commands.add_cicd import add_cicd_command
from djboost.commands.remove_cicd import remove_cicd_command

app = typer.Typer(help="djboost — Django project generator CLI")
create = typer.Typer(help="Create a new project or app")
add = typer.Typer(help="Add integrations to your project")
remove = typer.Typer(help="Remove integrations from your project")

app.add_typer(create, name="create")
app.add_typer(add, name="add")
app.add_typer(remove, name="remove")

create.command("project")(create_project_command)
create.command("app")(create_app_command)
add.command("cicd")(add_cicd_command)
remove.command("cicd")(remove_cicd_command)


def version_callback(value: bool):
    if value:
        typer.echo("djboost version 0.1.3")
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
