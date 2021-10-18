from tests.fixtures import *


@pytest.fixture
def valid_storage():
    with open("tests/files/storage.json", "r") as f:
        return json.load(f)


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


def test_storage_path(client):
    # Works only for existing stores
    rv = client.get("/storage/not-found/wherever")
    assert rv.status.startswith("404"), "HTTP Status is wrong"

    # Store path can be factored
    rv = client.get("/storage/stronghold/path/to/file.csv")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert (
        rv.get_json()["path"] == "path/to/file.csv"
    ), "Store without prefix should return the path"
    assert (
        rv.get_json()["uri"] == "gs://datalake-stronghold/path/to/file.csv"
    ), "URI should be predictible"

    # Store path includes the prefix
    rv = client.get("/storage/input/path/to/file.csv")
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert (
        rv.get_json()["path"] == "input/path/to/file.csv"
    ), "Store without prefix should return the path"
    assert (
        rv.get_json()["uri"] == "gs://datalake-landing/input/path/to/file.csv"
    ), "URI should be predictible"
