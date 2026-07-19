import os

os.environ["DB_USER"] = "user"
os.environ["DB_PASSWORD"] = "password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "airline_db"
os.environ["API_TOKEN"] = "test-token"

from fastapi.testclient import TestClient

from src.api.main import app, verify_token


def override_verify_token():
    return "test-token"


app.dependency_overrides[verify_token] = override_verify_token

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API Airlines"}


def test_unknown_route():
    response = client.get("/route-inexistante")

    assert response.status_code == 404
