from pony import orm
from pony.flask import Pony
from datalake_catalog.app import app


db = orm.Database()
Pony(app)


class Catalog(db.Entity):
    key = orm.PrimaryKey(str)
    spec = orm.Required(orm.Json)
