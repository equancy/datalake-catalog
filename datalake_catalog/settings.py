from os import urandom


class Default:
    DEBUG = False
    TESTING = False

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = "HS256"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = 60


class Develop(Default):
    ENV = "development"
    SECRET_KEY = b"\x97\x1f\x0f\xfb\xdaI\xcf&'\xa9\xe8z\xfa\x0f\xbcV\xefx\x16\x14\xe4\xd5\xf20\x92{J\xee\xf1\xae\x9aS"
    DB_STRING = "sqlite://localhost/catalog.sqlite"


class UnitTest(Default):
    TESTING = True
    SECRET_KEY = urandom(32)
    DB_STRING = "local://"
