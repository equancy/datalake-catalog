from base64 import b64decode, b64encode
import json
import pytest
from datetime import timedelta
from flask_jwt_extended import create_access_token
from datalake_catalog.app import app
from datalake_catalog.model import connect
import datalake_catalog.security
import datalake_catalog.api

app.config.from_object("datalake_catalog.settings.UnitTest")
connect(app.config["DB_STRING"])


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def guest_token():
    with app.app_context():
        token = create_access_token(identity="Test Guest")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def author_token():
    with app.app_context():
        token = create_access_token(
            identity="Test Author", additional_claims={"role": "author"}
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token():
    with app.app_context():
        token = create_access_token(
            identity="Test Admin", additional_claims={"role": "admin"}
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token():
    with app.app_context():
        token = create_access_token(
            identity="Test Expired",
            expires_delta=timedelta(seconds=-1),
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hacker_token():
    # somehow take hands on a valid jwt
    with app.app_context():
        token = create_access_token(
            identity="Test Hacked",
        )
    st = token.split(".")

    # remove the algorithm
    h = b64decode(st[0]).replace(b"HS256", b"none")

    # forge an admin token
    p = json.loads(b64decode(st[1]))
    p["role"] = "admin"
    p = json.dumps(p).encode("utf-8")

    # rebuild jwt
    token = b64encode(h).decode("utf-8") + "." + b64encode(p).decode("utf-8") + "."
    return {"Authorization": f"Bearer {token}"}
