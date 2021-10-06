from base64 import b64decode
import click
from flask import Flask, abort, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
    create_access_token,
    current_user,
)
from pony.flask import Pony
from datalake_catalog.model import db, Catalog


app = Flask(__name__)
app.config.update(
    {
        "DEBUG": False,
        "SECRET_KEY": b64decode("o8wm6b3hRIM01liXlbqep44DumtXB0pkONAJB3HQGHU="),
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_ALGORITHM": "HS256",
        "JWT_DECODE_ALGORITHMS": "HS256",
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
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

jwt = JWTManager(app)


@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_payload):
    return {"user": jwt_payload["sub"], "role": jwt_payload["role"]}


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify(message="Not Authorized"), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify(message="Not Authorized"), 401


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify(message="Not Authorized"), 401


@app.errorhandler(404)
def error_404(error):
    return jsonify(message="Not found"), 404


@app.errorhandler(400)
def error_400(error):
    return jsonify(message="Bad request"), 400


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
    print(f"User '{current_user['user']}' changed the entry '{entry_id}'")
    return jsonify(message="OK"), 200


@click.group()
def cli():
    pass


@cli.command()
def start():
    app.run()


@cli.command()
def create_api_key():
    with app.app_context():
        click.echo(
            create_access_token(
                identity="Paul",
                additional_claims={"role": "editor"},
                expires_delta=False,
            )
        )
