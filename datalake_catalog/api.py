from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, current_user
from datalake_catalog.app import app
from datalake_catalog.model import Catalog


@app.get("/catalog")
def get_entries():
    l = Catalog.select()
    return jsonify([c.key for c in l]), 200


@app.get("/catalog/<entry_id>")
def get_entry(entry_id):
    e = Catalog.get(key=entry_id)
    if e is None:
        abort(404)
    return jsonify({"key": entry_id, "location": e.location}), 200


@app.put("/catalog/<entry_id>")
@jwt_required()
def put_entry(entry_id):
    r = current_user["role"]
    if r not in ("admin", "editor"):
        return jsonify(message="Forbidden"), 403
    d = request.get_json()
    e = Catalog[entry_id]
    if e is not None:
        e.location = d["location"]
    else:
        e = Catalog(key=entry_id, location=d["location"])
    app.logger.info(f"User '{current_user['user']}' changed the entry '{entry_id}'")
    return jsonify(message="OK"), 200
