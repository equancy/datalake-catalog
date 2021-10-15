from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, current_user
from jsonschema.exceptions import ValidationError
from datalake_catalog.app import app
from datalake_catalog.model import (
    Catalog,
    upsert_catalog,
    Storage,
    insert_storage,
    Configuration,
)
from datalake_catalog.schemas import SchemaValidator

catalog_validator = SchemaValidator("catalog")
storage_validator = SchemaValidator("storage")
config_validator = SchemaValidator("configuration")


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify(message=f"at {error.json_path} : {error.message}"), 400


def check_role_author():
    if current_user["role"] not in ("admin", "author"):
        abort(403)


def check_role_admin():
    if current_user["role"] not in ("admin"):
        abort(403)


@app.get("/health")
def get_health():
    return jsonify(message="OK"), 200


@app.get("/catalog")
def get_catalog():
    if "full" in request.args:
        return jsonify({e.key: e.spec for e in Catalog.select()}), 200
    return jsonify([e.key for e in Catalog.select()]), 200


@app.get("/catalog/schema")
def get_catalog_schema():
    return jsonify(catalog_validator.schema), 200


@app.get("/catalog/entry/<entry_id>")
def get_catalog_entry(entry_id):
    e = Catalog.get(key=entry_id)
    if e is None:
        abort(404)
    return jsonify(e.spec), 200


def validate_spec(spec):
    catalog_validator.validate(spec)


@app.put("/catalog/entry/<entry_id>")
@jwt_required()
def put_catalog_entry(entry_id):
    check_role_author()
    validate_spec(request.get_json())
    upsert_catalog(entry_id, request.get_json())
    app.logger.info(f"User '{current_user['user']}' changed the entry '{entry_id}'")
    return jsonify(message="OK"), 200


@app.post("/catalog/import")
@jwt_required()
def post_catalog_import():
    check_role_author()
    error_messages = {}
    for key, value in request.get_json().items():
        try:
            validate_spec(value)
        except ValidationError as error:
            error_messages[key] = f"at {error.json_path}: {error.message}"
    if len(error_messages.keys()) > 0:
        return (
            jsonify(message="Catalog validation failed", failures=error_messages),
            400,
        )

    if "truncate" in request.args:
        Catalog.select().delete(bulk=True)
        app.logger.info(f"User '{current_user['user']}' truncated the entries")
    for key, value in request.get_json().items():
        upsert_catalog(key, value)
        app.logger.info(f"User '{current_user['user']}' changed the entry '{key}'")
    return jsonify(message="OK"), 200


@app.get("/storage")
def get_storages():
    return (
        jsonify(
            {s.key: {"bucket": s.bucket, "prefix": s.prefix} for s in Storage.select()}
        ),
        200,
    )


@app.put("/storage")
@jwt_required()
def put_storage():
    check_role_admin()
    storage_validator.validate(request.get_json())
    Storage.select().delete(bulk=True)

    for key, value in request.get_json().items():
        insert_storage(
            key, value["bucket"], value["prefix"] if "prefix" in value else None
        )
    app.logger.info(f"User '{current_user['user']}' updated the Storage configuration")
    return jsonify(message="OK"), 200


@app.get("/configuration")
def get_configuration():
    return jsonify({c.key: c.value for c in Configuration.select()}), 200


@app.put("/configuration")
@jwt_required()
def put_configuration():
    check_role_admin()
    config_validator.validate(request.get_json())
    for key, value in request.get_json().items():
        c = Configuration[key]
        c.value = value
    app.logger.info(f"User '{current_user['user']}' updated the global configuration")
    return jsonify(message="OK"), 200
