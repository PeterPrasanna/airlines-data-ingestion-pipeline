from fastapi import FastAPI, Query, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from src.config import DATABASE_URL, API_TOKEN

# Toutes les routes seront protégées par le token
app = FastAPI(title="Airlines & Airports API")

engine = create_engine(DATABASE_URL)

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Vérifie le token Bearer envoyé dans l'en-tête Authorization.
    Exemple attendu :
    Authorization: Bearer mon_token_secret
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Schéma d'authentification invalide"
        )

    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

    return credentials.credentials


@app.get("/")
def home():
    return {"message": "API Airlines"}


@app.get("/airlines")
def get_airlines(
    country: str | None = Query(None),
    iata_code: str | None = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    token: str = Depends(verify_token)
):
    query = """
        SELECT *
        FROM airlines
        WHERE 1=1
    """
    params = {"limit": limit}

    if country:
        query += " AND country_iso2 = UPPER(:country)"
        params["country"] = country

    if iata_code:
        query += " AND iata_code = UPPER(:iata_code)"
        params["iata_code"] = iata_code

    query += " ORDER BY airline_name LIMIT :limit"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    return list(rows)


@app.get("/airlines/{airline_id}")
def get_airline_by_id(
    airline_id: int,
    token: str = Depends(verify_token)
):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM airlines WHERE airline_id = :airline_id"),
            {"airline_id": airline_id}
        ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Compagnie aérienne introuvable")

    return dict(row)


@app.get("/airports")
def get_airports(
    country: str | None = Query(None),
    city_iata_code: str | None = Query(None),
    iata_code: str | None = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    token: str = Depends(verify_token)
):
    query = """
        SELECT *
        FROM airports
        WHERE 1=1
    """
    params = {"limit": limit}

    if country:
        query += " AND country_iso2 = UPPER(:country)"
        params["country"] = country

    if city_iata_code:
        query += " AND city_iata_code = UPPER(:city_iata_code)"
        params["city_iata_code"] = city_iata_code

    if iata_code:
        query += " AND iata_code = UPPER(:iata_code)"
        params["iata_code"] = iata_code

    query += " ORDER BY airport_name LIMIT :limit"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    return list(rows)


@app.get("/airports/{airport_id}")
def get_airport_by_id(
    airport_id: int,
    token: str = Depends(verify_token)
):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM airports WHERE airport_id = :airport_id"),
            {"airport_id": airport_id}
        ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Aéroport introuvable")

    return dict(row)