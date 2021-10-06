from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, current_user
from datalake_catalog.app import app
from datalake_catalog.model import Catalog
from pony.orm.core import ObjectNotFound


@app.get("/catalog/entry")
def get_entries():
    l = Catalog.select()
    return jsonify([c.key for c in l]), 200


@app.get("/catalog/entry/<entry_id>")
def get_entry(entry_id):
    e = Catalog.get(key=entry_id)
    if e is None:
        abort(404)
    return jsonify(e.spec), 200


@app.put("/catalog/entry/<entry_id>")
@jwt_required()
def put_entry(entry_id):
    role = current_user["role"]
    if role not in ("admin", "editor"):
        abort(403)

    try:
        catalog_entry = Catalog[entry_id]
        catalog_entry.spec = request.get_json()
        app.logger.info(f"User '{current_user['user']}' changed the entry '{entry_id}'")
        return jsonify(message="OK"), 200
    except ObjectNotFound:
        catalog_entry = Catalog(key=entry_id, spec=request.get_json())
        app.logger.info(f"User '{current_user['user']}' created the entry '{entry_id}'")
        return jsonify(message="OK"), 201
