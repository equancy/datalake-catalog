from pony import orm
from pony.orm.core import ObjectNotFound
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
    elif r.scheme == "local":
        db.bind(provider="sqlite", filename=":memory:")
    else:
        raise ValueError(f"Unknown provider '{r.scheme}' in database connection string")
    db.generate_mapping(create_tables=True)


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


def upsert_storage(key, bucket, prefix=None):
    try:
        s = Storage[key]
        s.bucket = bucket
        if prefix is not None:
            s.prefix = prefix
    except ObjectNotFound:
        if prefix is not None:
            s = Storage(key=key, bucket=bucket, prefix=prefix)
        else:
            s = Storage(key=key, bucket=bucket)
