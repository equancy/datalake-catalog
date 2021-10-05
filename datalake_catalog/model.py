from pony import orm

db = orm.Database()


class Catalog(db.Entity):
    key = orm.PrimaryKey(str)
    location = orm.Required(str)
