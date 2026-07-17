from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import FastAPI, Query, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

from src.config import DATABASE_URL, API_TOKEN


# ─────────────────────────────────────────────
# CONFIGURATION DU MODÈLE
# ─────────────────────────────────────────────

MODEL_DIR = Path("data/models")

MODEL_PATH = MODEL_DIR / "delay_predictor.pkl"
CARRIER_ENCODER_PATH = MODEL_DIR / "encoder_carrier.pkl"
ORIGIN_ENCODER_PATH = MODEL_DIR / "encoder_origin.pkl"
DEST_ENCODER_PATH = MODEL_DIR / "encoder_dest.pkl"

# Conteneur chargé au démarrage de l'application.
ml_objects: dict[str, object] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Charge le modèle et les encodeurs une seule fois
    au démarrage de l'API.
    """
    required_files = [
        MODEL_PATH,
        CARRIER_ENCODER_PATH,
        ORIGIN_ENCODER_PATH,
        DEST_ENCODER_PATH,
    ]

    missing_files = [
        str(file_path)
        for file_path in required_files
        if not file_path.exists()
    ]

    if missing_files:
        raise RuntimeError(
            "Fichiers ML introuvables : " + ", ".join(missing_files)
        )

    ml_objects["model"] = joblib.load(MODEL_PATH)
    ml_objects["carrier_encoder"] = joblib.load(CARRIER_ENCODER_PATH)
    ml_objects["origin_encoder"] = joblib.load(ORIGIN_ENCODER_PATH)
    ml_objects["dest_encoder"] = joblib.load(DEST_ENCODER_PATH)

    print("Modèle et encodeurs chargés.")

    yield

    ml_objects.clear()
    print("Ressources ML libérées.")


app = FastAPI(
    title="Airlines & Airports API",
    lifespan=lifespan,
)

engine = create_engine(DATABASE_URL)

security = HTTPBearer()


# ─────────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────────

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Schéma d'authentification invalide",
        )

    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )

    return credentials.credentials


# ─────────────────────────────────────────────
# SCHÉMAS ML
# ─────────────────────────────────────────────

class FlightPredictionInput(BaseModel):
    """
    Informations nécessaires à la prédiction d'un vol.
    """

    airline_code: str = Field(
        ...,
        min_length=1,
        examples=["AA"],
        description="Code de la compagnie présent dans AIRLINE_CODE",
    )

    origin: str = Field(
        ...,
        min_length=3,
        max_length=3,
        examples=["JFK"],
        description="Code IATA de l'aéroport de départ",
    )

    destination: str = Field(
        ...,
        min_length=3,
        max_length=3,
        examples=["LAX"],
        description="Code IATA de l'aéroport d'arrivée",
    )

    flight_date: date = Field(
        ...,
        examples=["2024-07-15"],
        description="Date du vol au format YYYY-MM-DD",
    )

    scheduled_departure_time: int = Field(
        ...,
        ge=0,
        le=2359,
        examples=[1430],
        description="Heure prévue au format HHMM",
    )

    departure_delay: float = Field(
        default=0,
        examples=[12],
        description="Retard au départ en minutes",
    )

    scheduled_elapsed_time: float = Field(
        ...,
        gt=0,
        examples=[360],
        description="Durée prévue du vol en minutes",
    )

    distance: float = Field(
        ...,
        gt=0,
        examples=[2475],
        description="Distance du vol",
    )


class FlightPredictionOutput(BaseModel):
    prediction: int
    label: str
    delay_probability: float
    on_time_probability: float


# ─────────────────────────────────────────────
# ROUTES GÉNÉRALES
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "API Airlines"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": "model" in ml_objects,
    }


# ─────────────────────────────────────────────
# ENDPOINT DE PRÉDICTION
# ─────────────────────────────────────────────

@app.get("/prediction/options")
def get_prediction_options(
    token: str = Depends(verify_token),
):
    carrier_encoder = ml_objects.get("carrier_encoder")
    origin_encoder = ml_objects.get("origin_encoder")
    dest_encoder = ml_objects.get("dest_encoder")

    if any(
        encoder is None
        for encoder in [
            carrier_encoder,
            origin_encoder,
            dest_encoder,
        ]
    ):
        raise HTTPException(
            status_code=503,
            detail="Les encodeurs ne sont pas disponibles",
        )

    return {
        "airlines": carrier_encoder.categories_[0].tolist(),
        "origins": origin_encoder.categories_[0].tolist(),
        "destinations": dest_encoder.categories_[0].tolist(),
    }

@app.post(
    "/predict",
    response_model=FlightPredictionOutput,
)
def predict_delay(
    flight: FlightPredictionInput,
    token: Annotated[str, Depends(verify_token)],
):
    model = ml_objects.get("model")
    carrier_encoder = ml_objects.get("carrier_encoder")
    origin_encoder = ml_objects.get("origin_encoder")
    dest_encoder = ml_objects.get("dest_encoder")

    if any(
        item is None
        for item in [
            model,
            carrier_encoder,
            origin_encoder,
            dest_encoder,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle ML n'est pas disponible",
        )

    airline_code = flight.airline_code.strip().upper()
    origin = flight.origin.strip().upper()
    destination = flight.destination.strip().upper()

    # Vérification du format HHMM.
    departure_hour = flight.scheduled_departure_time // 100
    departure_minute = flight.scheduled_departure_time % 100

    if departure_hour > 23 or departure_minute > 59:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "scheduled_departure_time doit respecter le format HHMM "
                "avec une heure entre 00 et 23 et des minutes entre 00 et 59"
            ),
        )

    try:
        airline_encoded = int(
            carrier_encoder.transform(
                [[airline_code]]
            )[0][0]
        )

        origin_encoded = int(
            origin_encoder.transform(
                [[origin]]
            )[0][0]
        )

        destination_encoded = int(
            dest_encoder.transform(
                [[destination]]
            )[0][0]
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "La compagnie ou l'un des aéroports n'était pas présent "
                f"dans les données d'entraînement : {error}"
            ),
        ) from error

    # L'ordre des colonnes doit être exactement le même
    # que pendant l'entraînement.
    model_input = pd.DataFrame(
        [
            {
                "AIRLINE_CODE_ENC": airline_encoded,
                "ORIGIN_ENC": origin_encoded,
                "DEST_ENC": destination_encoded,
                "day_of_week": flight.flight_date.weekday(),
                "month": flight.flight_date.month,
                "dep_hour": departure_hour,
                "DEP_DELAY": flight.departure_delay,
                "CRS_ELAPSED_TIME": flight.scheduled_elapsed_time,
                "DISTANCE": flight.distance,
            }
        ]
    )

    try:
        prediction = int(model.predict(model_input)[0])
        probabilities = model.predict_proba(model_input)[0]

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur pendant la prédiction : {error}",
        ) from error

    # On récupère les probabilités à partir de l'ordre model.classes_.
    probability_by_class = {
        int(class_name): float(probability)
        for class_name, probability in zip(
            model.classes_,
            probabilities,
            strict=True,
        )
    }

    delay_probability = probability_by_class.get(1, 0.0)
    on_time_probability = probability_by_class.get(0, 0.0)

    return {
        "prediction": prediction,
        "label": "En retard" if prediction == 1 else "À l'heure",
        "delay_probability": round(delay_probability, 4),
        "on_time_probability": round(on_time_probability, 4),
    }


# ─────────────────────────────────────────────
# ROUTES AIRLINES
# ─────────────────────────────────────────────

@app.get("/airlines")
def get_airlines(
    country: str | None = Query(None),
    iata_code: str | None = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    token: str = Depends(verify_token),
):
    query = """
        SELECT *
        FROM airlines
        WHERE 1=1
    """

    params = {
        "limit": limit,
        "offset": offset,
    }

    if country:
        query += " AND country_iso2 = UPPER(:country)"
        params["country"] = country

    if iata_code:
        query += " AND iata_code = UPPER(:iata_code)"
        params["iata_code"] = iata_code

    query += """
        ORDER BY airline_name
        LIMIT :limit
        OFFSET :offset
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query),
            params,
        ).mappings().all()

    return list(rows)


@app.get("/airlines/{airline_id}")
def get_airline_by_id(
    airline_id: int,
    token: str = Depends(verify_token),
):
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT *
                FROM airlines
                WHERE airline_id = :airline_id
                """
            ),
            {"airline_id": airline_id},
        ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Compagnie aérienne introuvable",
        )

    return dict(row)


# ─────────────────────────────────────────────
# ROUTES AIRPORTS
# ─────────────────────────────────────────────

@app.get("/airports")
def get_airports(
    country: str | None = Query(None),
    city_iata_code: str | None = Query(None),
    iata_code: str | None = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    token: str = Depends(verify_token),
):
    query = """
        SELECT *
        FROM airports
        WHERE 1=1
    """

    params = {
        "limit": limit,
        "offset": offset,
    }

    if country:
        query += " AND country_iso2 = UPPER(:country)"
        params["country"] = country

    if city_iata_code:
        query += " AND city_iata_code = UPPER(:city_iata_code)"
        params["city_iata_code"] = city_iata_code

    if iata_code:
        query += " AND iata_code = UPPER(:iata_code)"
        params["iata_code"] = iata_code

    query += " ORDER BY airport_name LIMIT :limit OFFSET :offset"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    return list(rows)


@app.get("/airports/{airport_id}")
def get_airport_by_id(
    airport_id: int,
    token: str = Depends(verify_token),
):
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT *
                FROM airports
                WHERE airport_id = :airport_id
                """
            ),
            {"airport_id": airport_id},
        ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Aéroport introuvable",
        )

    return dict(row)
