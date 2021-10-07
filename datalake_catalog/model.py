from pony import orm
from pony.flask import Pony
from datalake_catalog.app import app
from urllib.parse import urlparse

db = orm.Database()
Pony(app)


def connect(db_string):
    r = urlparse(db_string)
    if r.scheme == "sqlite":
        path = r.path[1:]  # strip the first /
        db.bind(provider="sqlite", filename=path, create_db=True)
    elif r.scheme == "mysql":
        host = f"{r.hostname}:{r.port}" if r.port is not None else r.hostname
        db.bind(
            provider="mysql", host=host, user=r.username, passwd=r.password, db=path[1:]
        )
    elif r.scheme == "postgresql":
        host = f"{r.hostname}:{r.port}" if r.port is not None else r.hostname
        db.bind(
            provider="postgres",
            user=r.username,
            password=r.password,
            host=host,
            database=path[1:],
        )
    elif r.scheme == "oracle":
        db.bind(provider="oracle", user=r.username, password=r.password, dsn=r.hostname)
    else:
        raise ValueError(f"Unknown provider '{r.scheme}' in database connection string")
    db.generate_mapping(create_tables=True)


class Catalog(db.Entity):
    key = orm.PrimaryKey(str)
    spec = orm.Required(orm.Json)
