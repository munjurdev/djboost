import typer
from djboost.generator import create_project


def create_project_command(name: str = typer.Argument("core", help="The name of the Django project")):
    create_project(name)