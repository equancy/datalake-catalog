import click
from datetime import timedelta
from flask_jwt_extended import create_access_token
from pony.flask import Pony
from datalake_catalog.app import app
from datalake_catalog.model import connect
import datalake_catalog.security
import datalake_catalog.api


app.config.from_object("datalake_catalog.settings.Default")
if not app.config.from_envvar("CATALOG_SETTINGS", silent=True):
    app.config.from_object("datalake_catalog.settings.Develop")

connect(app.config["DB_STRING"])


@click.group()
def cli():
    pass


@cli.command()
@click.argument("name")
@click.option("-e", "--expires", type=int, help="number of days before token expires")
@click.option(
    "-r",
    "--role",
    type=click.Choice(["author", "admin"]),
    help="the role associated with the name",
)
def create_api_key(name, expires, role):
    claims = {}
    if role is not None:
        claims["role"] = role
    if expires is None:
        expiry = False
    else:
        expiry = timedelta(days=expires)
    with app.app_context():
        click.echo(
            create_access_token(
                identity=name,
                additional_claims=claims,
                expires_delta=expiry,
            )
        )
