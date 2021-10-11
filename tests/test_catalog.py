from os import urandom
from time import sleep
from base64 import b64decode, b64encode
import json
import pytest
from flask_jwt_extended import create_access_token
from datalake_catalog.app import app
from datalake_catalog.model import connect
import datalake_catalog.security
import datalake_catalog.api
from datetime import timedelta

connect("local://")
app.config.from_object("datalake_catalog.settings.UnitTest")
app.config["SECRET_KEY"] = urandom(32)


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
            expires_delta=timedelta(microseconds=1),
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


@pytest.fixture
def valid_entry():
    with open("tests/test-entry.json", "r") as f:
        return json.load(f)


def test_health(client):
    rv = client.get("/health")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json()["message"] == "OK", "Response payload is wrong"


def test_api_token(client, hacker_token, expired_token):
    endpoint = "/catalog/entry/test"

    # Wrong signature shall not pass
    rv = client.put(
        endpoint,
        headers={
            "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        },
    )
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # Hacked algorithm shall not pass
    rv = client.put(endpoint, headers=hacker_token)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # Expired token shall not pass
    sleep(1)
    rv = client.put(endpoint, headers=expired_token)
    assert rv.status.startswith("401"), "HTTP Status is wrong"


def test_create(client, guest_token, author_token, admin_token, valid_entry):
    endpoint = "/catalog/entry/test"

    # entry does not exist at first
    rv = client.get(endpoint)
    assert rv.status.startswith("404"), "HTTP Status is wrong"

    # authorization is required
    rv = client.put(endpoint)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # permission is required
    rv = client.put(endpoint, headers=guest_token)
    assert rv.status.startswith("403"), "HTTP Status is wrong"

    # an author may manage
    rv = client.put(endpoint, json=valid_entry, headers=author_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # an admin may also manage
    rv = client.put(endpoint, json=valid_entry, headers=admin_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # once creaed, entry is available
    rv = client.get(endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == valid_entry, "Entry is not the same"
