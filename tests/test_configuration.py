from tests.fixtures import *

DEFAULT_CONFIGURATION = {
    "provider": "local",
    "csv_format": {
        "delimiter": ",",
        "quote_char": '"',
        "escape_char": "\\",
        "double_quote": True,
        "line_break": "\n",
    },
}


@pytest.fixture
def valid_configuration():
    with open("tests/files/configuration.json", "r") as f:
        return json.load(f)


def test_global(client, author_token, admin_token, valid_configuration):
    endpoint = "/configuration"
    # Configuration is default at first
    rv = client.get(endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == DEFAULT_CONFIGURATION, "Configuration should be default"

    # authorization is required
    rv = client.put(endpoint)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # permission is required
    rv = client.put(endpoint, headers=author_token)
    assert rv.status.startswith("403"), "HTTP Status is wrong"

    # an admin may import
    rv = client.put(endpoint, json=valid_configuration, headers=admin_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"

    # once imported, Configuration is available
    rv = client.get(endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == valid_configuration, "Configuration should be predictible"

    # Configuration schema is validated
    rv = client.put(endpoint, json={"configuration": "bad"}, headers=admin_token)
    assert rv.status.startswith("400"), "HTTP Status is wrong"


def test_atomic(client, author_token, admin_token):
    endpoint = "/configuration/provider"
    # Single configuration entry can be fetched
    rv = client.get(endpoint)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert rv.get_json() == "local", "Configuration should be default"
    rv = client.get("configuration/not-present")
    assert rv.status.startswith("404"), "HTTP Status is wrong"

    # Single configuration can be updated
    # but authorization is required
    rv = client.put(endpoint)
    assert rv.status.startswith("401"), "HTTP Status is wrong"

    # and permission is required
    rv = client.put(endpoint, headers=author_token)
    assert rv.status.startswith("403"), "HTTP Status is wrong"

    # then admin may import
    # yet input schema is validated
    rv = client.put(endpoint, json={"configuration": "bad"}, headers=admin_token)
    assert rv.status.startswith("400"), "HTTP Status is wrong"
    rv = client.put(endpoint, json="gcp", headers=admin_token)
    assert rv.status.startswith("200"), "HTTP Status is wrong"
    assert client.get(endpoint).get_json() == "gcp", "Configuration should have been updated"

    # only valid configuration may be updated
    rv = client.put("configuration/not-present", headers=admin_token)
    assert rv.status.startswith("404"), "HTTP Status is wrong"
