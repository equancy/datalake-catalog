from base64 import b64decode


class Default:
    DEBUG = False
    ENV = "production"

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = "HS256"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    DB_STRING = "sqlite:///catalog.sqlite"

class UnitTest:
    DEBUG = False
    ENV = "testing"

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = "HS256"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = 60

    DB_STRING = "local://"
