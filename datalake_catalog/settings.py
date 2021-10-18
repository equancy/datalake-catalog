from os import urandom


class Default:
    DEBUG = False
    ENV = "production"

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = "HS256"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = 60


class UnitTest(Default):
    TESTING = True
    SECRET_KEY = urandom(32)
