import click

from flask_jwt_extended import create_access_token
from pony.flask import Pony
from datalake_catalog.app import app
from datalake_catalog.model import connect
import datalake_catalog.security
import datalake_catalog.api


app.config.from_object("datalake_catalog.settings.Default")
app.config.from_envvar("CATALOG_SETTINGS")

connect(app.config["DB_STRING"])


@click.group()
def cli():
    pass


@cli.command()
def start():
    app.run()


@cli.command()
def create_api_key():
    with app.app_context():
        click.echo(
            create_access_token(
                identity="Paul",
                additional_claims={"role": "author"},
                expires_delta=False,
            )
        )
