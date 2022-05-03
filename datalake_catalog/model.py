import json
from string import Formatter
import re
from pony import orm
from pony.orm.core import ObjectNotFound
from pony.flask import Pony
from datalake_catalog.app import app
from urllib.parse import urlparse
from pkg_resources import resource_stream

db = orm.Database()
Pony(app)
provider_scheme = {"aws": "s3", "gcp": "gs", "azure": "adls", "local": "file"}


def connect(db_string):
    r = urlparse(db_string)
    path = r.path[1:]  # strip the first /
    if r.scheme == "sqlite":
        db.bind(provider="sqlite", filename=path, create_db=True)
    elif r.scheme == "mysql":
        port = r.port if r.port is not None else 3306
        db.bind(provider="mysql", host=r.hostname, port=port, user=r.username, passwd=r.password, db=path)
    elif r.scheme == "postgresql":
        port = r.port if r.port is not None else 5432
        db.bind(provider="postgres", user=r.username, password=r.password, host=r.hostname, database=path, port=port)
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
    path_pattern = orm.Required(str)

    @property
    def path_regex(self):
        formatter = Formatter().parse(self.path_pattern)
        fields = []
        result = ""
        for (literal_text, field_name, format_spec, conversion) in formatter:
            result += re.escape(literal_text)
            if field_name is not None:
                if field_name in fields:  # backreference for existing name
                    result += f"(?P={field_name})"
                else:
                    fields.append(field_name)  # new name reference
                    result += f"(?P<{field_name}>.+)"
        return re.compile(f"{result}$")  # ensure only suffixes are matched


class Storage(db.Entity):
    key = orm.PrimaryKey(str)
    bucket = orm.Required(str)
    prefix = orm.Optional(str)

    def get_real_path(self, path):
        if self.prefix is not None and len(self.prefix) > 0:
            return f"{self.prefix}/{path}"
        return f"{path}"

    def build_uri(self, path):
        provider = Configuration["provider"].value
        real_path = self.get_real_path(path)
        scheme = provider_scheme[provider]
        return f"{scheme}://{self.bucket}/{real_path}"


class Configuration(db.Entity):
    key = orm.PrimaryKey(str)
    value = orm.Required(orm.Json)


def upsert_catalog(key, spec):
    domain = spec["domain"]
    provider = spec["provider"]
    feed = spec["feed"]

    # Preprocess the path pattern
    path_pattern = spec["storage"]["path"]["pattern"]
    path_format = Formatter().parse(path_pattern)
    path_pattern = ""
    for (literal_text, field_name, format_spec, conversion) in path_format:
        path_pattern += literal_text
        if field_name is not None:
            if field_name == "domain":
                path_pattern += domain
            elif field_name == "provider":
                path_pattern += provider
            elif field_name == "feed":
                path_pattern += feed
            else:
                path_pattern += "{" + field_name + "}"

    try:
        e = Catalog[key]
        e.spec = spec
        e.domain = domain
        e.provider = provider
        e.feed = feed
        e.path_pattern
    except ObjectNotFound:
        e = Catalog(
            key=key,
            spec=spec,
            domain=domain,
            provider=provider,
            feed=feed,
            path_pattern=path_pattern,
        )


def insert_storage(key, bucket, prefix=None):
    if prefix is not None:
        s = Storage(key=key, bucket=bucket, prefix=prefix)
    else:
        s = Storage(key=key, bucket=bucket)
