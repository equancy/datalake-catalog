import click
from flask import Flask, abort, request, jsonify
from pony.flask import Pony
from datalake_catalog.model import db, Catalog


app = Flask(__name__)
app.config.update(
    {
        "DEBUG": False,
        "SECRET_KEY": "WHZRAjy3FU8RFzKr42oEeNRk5jroFMcpsxeVLLGriHxVSD6fPV9n26rwM4ox9rwq",
        "PONY": {
            "provider": "sqlite",
            "filename": "/Users/dschmitt/projects/equancy/technologies/datalake-catalog/catalog.sqlite",
            "create_db": True,
        },
    }
)
Pony(app)
db.bind(**app.config["PONY"])
db.generate_mapping(create_tables=True)


@app.errorhandler(404)
def error_404(error):
    return {"message": "Not found"}, 404


@app.errorhandler(400)
def error_400(error):
    return {"message": "Bad request"}, 400


@app.get("/catalog")
def get_entries():
    l = Catalog.select()
    return jsonify([c.key for c in l])


@app.get("/catalog/<entry_id>")
def get_entry(entry_id):
    e = Catalog.get(key=entry_id)
    if e is None:
        abort(404)
    return {"key": entry_id, "location": e.location}


@app.put("/catalog/<entry_id>")
def put_entry(entry_id):
    d = request.get_json()
    e = Catalog(key=d["key"], location=d["location"])
    return {"message": "OK"}


@click.command()
def cli():
    app.run()
