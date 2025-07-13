from fastapi.testclient import TestClient

from flasx.main import app
import pytest

client = TestClient(app)


def test_hello() -> None:
    """Test the hello endpoint."""
    response = client.get("/v1/hello")
    assert response.status_code == 200
    assert response.json() == "Hello, World!"


def test_add_operation() -> None:
    """Test the add operation endpoint."""
    response = client.post("/v1/hello/add-operation?a=5&b=10")
    assert response.status_code == 200
    assert response.json() == 15

    response = client.post("/v1/hello/add-operation?a=2.5&b=3.5")
    assert response.status_code == 200
    assert response.json() == 6.0

    response = client.post("/v1/hello/add-operation?a=1&b=2")
    assert response.status_code == 200
    assert response.json() == 3.0


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (-100000000, 100000, -99900000),
        (-50000000, 150000, -49850000),
        (0, 200000, 200000),
        (50000000, 175000, 50175000),
        (100000000, 200000, 100200000),
    ],
)
def test_add_operation_large_range(a, b, expected):
    print(a, b, expected)
    response = client.post(f"/v1/hello/add-operation?a={a}&b={b}")
    assert response.status_code == 200
    assert response.json() == float(expected)
