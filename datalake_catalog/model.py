import json
from pony import orm
from pony.orm.core import ObjectNotFound
from pony.flask import Pony
from datalake_catalog.app import app
from urllib.parse import urlparse
from pkg_resources import resource_stream

db = orm.Database()
Pony(app)


def connect(db_string):  # pragma: no cover
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
    elif r.scheme == "local":
        db.bind(provider="sqlite", filename=":memory:")
    else:
        raise ValueError(f"Unknown provider '{r.scheme}' in database connection string")
    _init_db()


def _init_db():
    db.generate_mapping(create_tables=True)

    with resource_stream("datalake_catalog", f"config/default.json") as f:
        default_config = json.load(f)
    
    with orm.db_session:
        for key, value in default_config.items():
            if Configuration.get(key=key) is None:
                Configuration(key=key, value=value)


class Catalog(db.Entity):
    key = orm.PrimaryKey(str)
    spec = orm.Required(orm.Json)

    domain = orm.Required(str)
    provider = orm.Required(str)
    feed = orm.Required(str)


class Storage(db.Entity):
    key = orm.PrimaryKey(str)
    bucket = orm.Required(str)
    prefix = orm.Optional(str)


class Configuration(db.Entity):
    key = orm.PrimaryKey(str)
    value = orm.Required(orm.Json)


def upsert_catalog(key, spec):
    domain = spec["domain"]
    provider = spec["provider"]
    feed = spec["feed"]
    try:
        e = Catalog[key]
        e.spec = spec
        e.domain = domain
        e.provider = provider
        e.feed = feed
    except ObjectNotFound:
        e = Catalog(key=key, spec=spec, domain=domain, provider=provider, feed=feed)


def insert_storage(key, bucket, prefix=None):
    if prefix is not None:
        s = Storage(key=key, bucket=bucket, prefix=prefix)
    else:
        s = Storage(key=key, bucket=bucket)
