from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, current_user
from datalake_catalog.app import app
from datalake_catalog.model import Catalog
from pony.orm.core import ObjectNotFound

import json
from jsonschema import Draft7Validator
from pkg_resources import resource_stream

with resource_stream("datalake_catalog", "schemas/entry.json") as f:
    schema = json.load(f)
Draft7Validator.check_schema(schema)
validator = Draft7Validator(schema)


def check_role_author():
    if current_user["role"] not in ("admin", "author"):
        abort(403)


@app.get("/catalog")
def get_entries():
    if "full" in request.args:
        return jsonify({e.key: e.spec for e in Catalog.select()}), 200
    return jsonify([e.key for e in Catalog.select()]), 200


@app.get("/catalog/schema")
def get_schema():
    return jsonify(schema), 200


@app.get("/catalog/entry/<entry_id>")
def get_entry(entry_id):
    e = Catalog.get(key=entry_id)
    if e is None:
        abort(404)
    return jsonify(e.spec), 200


def upsert_entry(key, spec):
    validator.validate(spec)
    try:
        e = Catalog[key]
        e.spec = spec
        app.logger.info(f"User '{current_user['user']}' changed the entry '{key}'")
    except ObjectNotFound:
        e = Catalog(key=key, spec=spec)
        app.logger.info(f"User '{current_user['user']}' created the entry '{key}'")


@app.put("/catalog/entry/<entry_id>")
@jwt_required()
def put_entry(entry_id):
    check_role_author()
    upsert_entry(entry_id, request.get_json())
    return jsonify(message="OK"), 200


@app.post("/catalog/import")
@jwt_required()
def post_import():
    check_role_author()
    if "truncate" in request.args:
        Catalog.select().delete(bulk=True)
        app.logger.info(f"User '{current_user['user']}' truncated the entries")
    for key, value in request.get_json().items():
        upsert_entry(key, value)
    return jsonify(message="OK"), 200
