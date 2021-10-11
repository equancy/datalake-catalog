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


@pytest.fixture
def valid_storage():
    with open("tests/test-storage.json", "r") as f:
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


def test_schema(client):
    rv = client.get("/catalog/schema")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert (
        rv.get_json()["$schema"] == "http://json-schema.org/draft-07/schema#"
    ), "Response payload is wrong"


def test_catalog_management(client, guest_token, author_token, valid_entry):
    import_endpoint = "/catalog/import"
    create_endpoint = "/catalog/entry/test-created"
    payload = {"test-imported": valid_entry}

    # Catalog is empty at first
    rv = client.get("/catalog")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == [], "Catalog should be empty"

    # ---------------------------
    # Batch import

    # authorization is required
    rv = client.post(import_endpoint)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # permission is required
    rv = client.post(import_endpoint, headers=guest_token)
    assert rv.status.startswith("403"), "HTTP Status is wrong"

    # an author may import
    rv = client.post(import_endpoint, json=payload, headers=author_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # catalog schema is validated
    rv = client.post(import_endpoint, json={"catalog": "bad"}, headers=author_token)
    assert rv.status.startswith("400"), "HTTP Status is wrong"

    # once imported, catalog is available
    rv = client.get("/catalog", query_string={"full": "yes"})
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == payload, "Catalog should be predictible"

    # import is idempotent
    rv = client.post(import_endpoint, json=payload, headers=author_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    rv = client.get("/catalog", query_string={"full": "yes"})
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == payload, "Catalog import should be idempotent"

    # ---------------------------
    # Single entry creation

    # entry does not exist at first
    rv = client.get(create_endpoint)
    assert rv.status.startswith("404"), "HTTP Status is wrong"

    # authorization is required
    rv = client.put(create_endpoint)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # permission is required
    rv = client.put(create_endpoint, headers=guest_token)
    assert rv.status.startswith("403"), "HTTP Status is wrong"

    # an author may manage
    rv = client.put(create_endpoint, json=valid_entry, headers=author_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # entry is validated before creation
    rv = client.put(create_endpoint, json={"catalog": "bad"}, headers=author_token)
    assert rv.status.startswith("400"), "HTTP Status is wrong"

    # once created, entry is available
    rv = client.get(create_endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == valid_entry, "Entry is not the same"

    # creation is merged with import
    rv = client.get("/catalog")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert not set(rv.get_json()) ^ {
        "test-created",
        "test-imported",
    }, "Catalog should be predictible"

    # ---------------------------
    # Import can be authoritative

    # import can truncate
    rv = client.post(
        import_endpoint,
        query_string={"truncate": "yes"},
        json=payload,
        headers=author_token,
    )
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # once truncated and imported, catalog is predictible
    rv = client.get("/catalog?full")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == payload, "Catalog should be predictible"


def test_storage(client, author_token, admin_token, valid_storage):
    endpoint = "/storage"
    # Storage is empty at first
    rv = client.get(endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == {}, "Storage should be empty"

    # authorization is required
    rv = client.put(endpoint)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # permission is required
    rv = client.put(endpoint, headers=author_token)
    assert rv.status.startswith("403"), "HTTP Status is wrong"

    # an admin may import
    rv = client.put(endpoint, json=valid_storage, headers=admin_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # once imported, storage is available
    rv = client.get("/storage")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json().keys() == valid_storage.keys(), "Storage should be predictible"
