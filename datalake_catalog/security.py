from flask_jwt_extended import JWTManager
from datalake_catalog.app import app

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
