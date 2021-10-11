from flask import jsonify
from flask_jwt_extended import JWTManager
from datalake_catalog.app import app

jwt = JWTManager(app)


@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_payload):
    return {
        "user": jwt_payload["sub"],
        "role": jwt_payload["role"] if "role" in jwt_payload else "",
    }


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    app.logger.warning(f"Received an expired token")
    return jsonify(message="Unauthorized"), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    app.logger.warning(f"Received an invalid token. {reason}")
    return jsonify(message="Unauthorized"), 401


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify(message="Unauthorized"), 401
