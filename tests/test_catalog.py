from tests.fixtures import *


@pytest.fixture
def valid_entry():
    with open("tests/files/entry.json", "r") as f:
        return json.load(f)


def test_schema(client):
    rv = client.get("/catalog/schema")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert (
        rv.get_json()["$schema"] == "http://json-schema.org/draft-07/schema#"
    ), "Response payload should be a schema"
    assert (
        rv.get_json()["$schema"] == "http://json-schema.org/draft-07/schema#"
    ), "Response payload should be the catalog schema"


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


def test_catalog_storage(client):
    endpoint = "/catalog/storage/test-imported"
    # Storage prefix can be partial
    rv = client.get(endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json()["is_partial"], "Storage prefix should be partial"
    assert (
        rv.get_json()["prefix"] == "unit-test/equancy/mock/"
    ), "Prefix should be predictible"

    # Storage prefix can be completed
    rv = client.get(endpoint, query_string={"date": "YYYYMMDD"})
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert not rv.get_json()["is_partial"], "Storage prefix should not be partial"
    assert (
        rv.get_json()["prefix"] == "unit-test/equancy/mock/YYYYMMDD_mock.csv"
    ), "Prefix should be predictible"

    # Entry must exist
    rv = client.get("/catalog/storage/not-found")
    assert rv.status.startswith("404"), "HTTP Status is wrong"
