import click
from base64 import b64decode
from flask_jwt_extended import create_access_token
from pony.flask import Pony
from datalake_catalog.app import app
from datalake_catalog.model import db
import datalake_catalog.security
import datalake_catalog.api


app.config["SECRET_KEY"] = b64decode("o8wm6b3hRIM01liXlbqep44DumtXB0pkONAJB3HQGHU=")

db.bind(
    {
        "provider": "sqlite",
        "filename": "/Users/dschmitt/projects/equancy/technologies/datalake-catalog/catalog.sqlite",
        "create_db": True,
    }
)
db.generate_mapping(create_tables=True)


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
                additional_claims={"role": "editor"},
                expires_delta=False,
            )
        )
