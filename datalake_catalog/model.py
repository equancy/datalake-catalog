from pony import orm


db = orm.Database()


class Catalog(db.Entity):
    key = orm.PrimaryKey(str)
    spec = orm.Required(orm.Json)
