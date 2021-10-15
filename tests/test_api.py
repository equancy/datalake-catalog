from tests.fixtures import *


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
    # sleep(1)
    rv = client.put(endpoint, headers=expired_token)
    assert rv.status.startswith("401"), "HTTP Status is wrong"
