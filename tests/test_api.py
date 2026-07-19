import os

# IMPORTANT :
# Les variables doivent être définies AVANT l'import de src.api.main,
# car DATABASE_URL et le moteur SQLAlchemy sont créés à l'import.
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test"
os.environ["API_TOKEN"] = "test-token"

import pytest
from fastapi.testclient import TestClient

from src.api.main import app, verify_token


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def client():
    """
    Client FastAPI sans contournement de l'authentification.
    Permet notamment de tester les erreurs 401/403.
    """
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client():
    """
    Client FastAPI avec authentification simulée.
    Évite d'avoir à fournir un vrai token pour chaque test.
    """

    def override_verify_token():
        return "test-token"

    app.dependency_overrides[verify_token] = override_verify_token

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────
# ROUTE HOME
# ─────────────────────────────────────────────

def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "API Airlines"
    }


def test_home_content_type(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


# ─────────────────────────────────────────────
# ROUTES INEXISTANTES
# ─────────────────────────────────────────────

def test_unknown_route(client):
    response = client.get("/route-inexistante")

    assert response.status_code == 404


def test_unknown_route_response(client):
    response = client.get("/route-inexistante")

    assert response.json() == {
        "detail": "Not Found"
    }


# ─────────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────────

def test_airlines_without_token(client):
    response = client.get("/airlines")

    # Selon la version FastAPI / Starlette,
    # HTTPBearer peut retourner 401 ou 403.
    assert response.status_code in [401, 403]


def test_airports_without_token(client):
    response = client.get("/airports")

    assert response.status_code in [401, 403]


def test_airlines_with_invalid_token(client):
    response = client.get(
        "/airlines",
        headers={
            "Authorization": "Bearer mauvais-token"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Token invalide"
    }


def test_airports_with_invalid_token(client):
    response = client.get(
        "/airports",
        headers={
            "Authorization": "Bearer mauvais-token"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Token invalide"
    }


# ─────────────────────────────────────────────
# VALIDATION /AIRLINES
# ─────────────────────────────────────────────

def test_airlines_limit_zero(authenticated_client):
    response = authenticated_client.get(
        "/airlines?limit=0"
    )

    assert response.status_code == 422


def test_airlines_limit_negative(authenticated_client):
    response = authenticated_client.get(
        "/airlines?limit=-1"
    )

    assert response.status_code == 422


def test_airlines_limit_too_high(authenticated_client):
    response = authenticated_client.get(
        "/airlines?limit=1001"
    )

    assert response.status_code == 422


def test_airlines_limit_invalid_type(authenticated_client):
    response = authenticated_client.get(
        "/airlines?limit=abc"
    )

    assert response.status_code == 422


# ─────────────────────────────────────────────
# VALIDATION /AIRPORTS
# ─────────────────────────────────────────────

def test_airports_limit_zero(authenticated_client):
    response = authenticated_client.get(
        "/airports?limit=0"
    )

    assert response.status_code == 422


def test_airports_limit_negative(authenticated_client):
    response = authenticated_client.get(
        "/airports?limit=-10"
    )

    assert response.status_code == 422


def test_airports_limit_too_high(authenticated_client):
    response = authenticated_client.get(
        "/airports?limit=1001"
    )

    assert response.status_code == 422


def test_airports_limit_invalid_type(authenticated_client):
    response = authenticated_client.get(
        "/airports?limit=bonjour"
    )

    assert response.status_code == 422


# ─────────────────────────────────────────────
# /PREDICT - AUTHENTIFICATION
# ─────────────────────────────────────────────

def test_predict_without_token(client):
    response = client.post(
        "/predict",
        json={}
    )

    assert response.status_code in [401, 403]


def test_predict_with_invalid_token(client):
    response = client.post(
        "/predict",
        headers={
            "Authorization": "Bearer mauvais-token"
        },
        json={}
    )

    assert response.status_code == 401


# ─────────────────────────────────────────────
# /PREDICT - VALIDATION DU PAYLOAD
# ─────────────────────────────────────────────

def test_predict_empty_payload(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={}
    )

    assert response.status_code == 422


def test_predict_missing_required_fields(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA"
        }
    )

    assert response.status_code == 422


def test_predict_invalid_origin(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "J",
            "destination": "LAX",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 1430,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": 2475
        }
    )

    assert response.status_code == 422


def test_predict_invalid_destination(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LA",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 1430,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": 2475
        }
    )

    assert response.status_code == 422


def test_predict_invalid_date(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LAX",
            "flight_date": "date-invalide",
            "scheduled_departure_time": 1430,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": 2475
        }
    )

    assert response.status_code == 422


def test_predict_negative_distance(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LAX",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 1430,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": -100
        }
    )

    assert response.status_code == 422


def test_predict_zero_distance(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LAX",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 1430,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": 0
        }
    )

    assert response.status_code == 422


def test_predict_negative_elapsed_time(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LAX",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 1430,
            "departure_delay": 12,
            "scheduled_elapsed_time": -50,
            "distance": 2475
        }
    )

    assert response.status_code == 422


def test_predict_departure_time_too_high(authenticated_client):
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LAX",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 2500,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": 2475
        }
    )

    assert response.status_code == 422


def test_predict_invalid_hhmm(authenticated_client):
    """
    2360 passe éventuellement la validation numérique <= 2359 ?
    Non, 2360 > 2359.

    On utilise donc 1460 :
    - inférieur à 2359 ;
    - mais les minutes 60 sont invalides.
    """
    response = authenticated_client.post(
        "/predict",
        json={
            "airline_code": "AA",
            "origin": "JFK",
            "destination": "LAX",
            "flight_date": "2024-07-15",
            "scheduled_departure_time": 1460,
            "departure_delay": 12,
            "scheduled_elapsed_time": 360,
            "distance": 2475
        }
    )

    assert response.status_code == 422