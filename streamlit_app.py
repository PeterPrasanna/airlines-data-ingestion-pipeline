import os

import requests
import streamlit as st


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

API_URL = os.getenv("API_URL", "http://api:8000")
API_TOKEN = os.getenv("API_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


# ─────────────────────────────────────────────
# CONFIGURATION STREAMLIT
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="LIORA AIRLINES",
    page_icon="✈️",
    layout="centered",
)


# ─────────────────────────────────────────────
# FONCTIONS API
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_airlines():
    """
    Récupère toutes les compagnies aériennes
    depuis l'API avec pagination.
    """

    all_airlines = []
    limit = 1000
    offset = 0

    while True:
        response = requests.get(
            f"{API_URL}/airlines",
            headers=HEADERS,
            params={
                "limit": limit,
                "offset": offset,
            },
            timeout=30,
        )

        response.raise_for_status()

        airlines = response.json()

        all_airlines.extend(
            airlines
        )

        if len(airlines) < limit:
            break

        offset += limit

    return all_airlines


@st.cache_data(ttl=300)
def get_airports():
    """
    Récupère tous les aéroports
    depuis l'API avec pagination.
    """

    all_airports = []
    limit = 1000
    offset = 0

    while True:
        response = requests.get(
            f"{API_URL}/airports",
            headers=HEADERS,
            params={
                "limit": limit,
                "offset": offset,
            },
            timeout=30,
        )

        response.raise_for_status()

        airports = response.json()

        all_airports.extend(
            airports
        )

        if len(airports) < limit:
            break

        offset += limit

    return all_airports


def predict_delay(payload):
    """
    Envoie les informations du vol à l'API
    et récupère la prédiction.
    """

    response = requests.post(
        f"{API_URL}/predict",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ─────────────────────────────────────────────
# EN-TÊTE
# ─────────────────────────────────────────────

st.title(
    "✈️ LIORA AIRLINES"
)

st.write(
    "Prédiction des retards de vols"
)

st.write(
    "Équipe : Julie Françoise, "
    "Prasanna Peter Alocias, "
    "Théo Voyer"
)

st.divider()


# ─────────────────────────────────────────────
# VÉRIFICATION DE LA CONFIGURATION
# ─────────────────────────────────────────────

if not API_TOKEN:

    st.error(
        "La variable d'environnement "
        "API_TOKEN n'est pas définie."
    )

    st.stop()


# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────

try:

    airlines = get_airlines()

    airports = get_airports()


except requests.HTTPError as error:

    try:

        detail = (
            error.response
            .json()
            .get(
                "detail",
                "Erreur inconnue",
            )
        )

    except Exception:

        detail = str(
            error
        )

    st.error(
        f"Erreur API : {detail}"
    )

    st.stop()


except requests.RequestException as error:

    st.error(
        "Impossible de contacter l'API."
    )

    st.code(
        str(error)
    )

    st.stop()


# ─────────────────────────────────────────────
# PRÉPARATION DES COMPAGNIES
# ─────────────────────────────────────────────

airline_options = {}


for airline in airlines:

    iata_code = airline.get(
        "iata_code"
    )

    airline_name = airline.get(
        "airline_name"
    )

    if iata_code:

        code = (
            str(iata_code)
            .strip()
            .upper()
        )

        airline_options[
            code
        ] = (
            airline_name
            or code
        )


carrier_codes = sorted(
    airline_options.keys()
)


# ─────────────────────────────────────────────
# PRÉPARATION DES AÉROPORTS
# ─────────────────────────────────────────────

airport_options = {}


for airport in airports:

    iata_code = airport.get(
        "iata_code"
    )

    airport_name = airport.get(
        "airport_name"
    )

    if iata_code:

        code = (
            str(iata_code)
            .strip()
            .upper()
        )

        airport_options[
            code
        ] = (
            airport_name
            or code
        )


airport_codes = sorted(
    airport_options.keys()
)


# ─────────────────────────────────────────────
# VÉRIFICATION DES LISTES
# ─────────────────────────────────────────────

if not carrier_codes:

    st.error(
        "Aucune compagnie aérienne disponible."
    )

    st.stop()


if not airport_codes:

    st.error(
        "Aucun aéroport disponible."
    )

    st.stop()


# ─────────────────────────────────────────────
# FORMULAIRE
# ─────────────────────────────────────────────

st.subheader(
    "Informations du vol"
)


carrier = st.selectbox(
    "Compagnie",
    options=carrier_codes,
    format_func=lambda code: (
        f"{code} - "
        f"{airline_options[code]}"
    ),
)


origin = st.selectbox(
    "Aéroport de départ",
    options=airport_codes,
    format_func=lambda code: (
        f"{code} - "
        f"{airport_options[code]}"
    ),
)


destination_options = [
    code
    for code in airport_codes
    if code != origin
]


destination = st.selectbox(
    "Aéroport d'arrivée",
    options=destination_options,
    format_func=lambda code: (
        f"{code} - "
        f"{airport_options[code]}"
    ),
)


flight_date = st.date_input(
    "Date du vol"
)


departure_hour = st.slider(
    "Heure de départ",
    min_value=0,
    max_value=23,
    value=8,
)


departure_delay = st.number_input(
    "Retard au départ (minutes)",
    value=0.0,
    step=1.0,
)


scheduled_elapsed_time = st.number_input(
    "Durée prévue du vol (minutes)",
    min_value=1.0,
    value=180.0,
    step=5.0,
)


distance = st.number_input(
    "Distance (miles)",
    min_value=1.0,
    value=800.0,
    step=10.0,
)


# ─────────────────────────────────────────────
# PRÉDICTION
# ─────────────────────────────────────────────

if st.button(
    "Lancer la prédiction",
    type="primary",
    use_container_width=True,
):

    scheduled_departure_time = (
        departure_hour
        * 100
    )


    payload = {

        "airline_code":
            carrier,

        "origin":
            origin,

        "destination":
            destination,

        "flight_date":
            str(
                flight_date
            ),

        "scheduled_departure_time":
            scheduled_departure_time,

        "departure_delay":
            departure_delay,

        "scheduled_elapsed_time":
            scheduled_elapsed_time,

        "distance":
            distance,
    }


    try:

        with st.spinner(
            "Prédiction en cours..."
        ):

            result = predict_delay(
                payload
            )


        st.divider()

        st.subheader(
            "Résultat"
        )


        prediction = result[
            "prediction"
        ]


        delay_probability = (
            result[
                "delay_probability"
            ]
            * 100
        )


        on_time_probability = (
            result[
                "on_time_probability"
            ]
            * 100
        )


        if prediction == 1:

            st.error(
                "⚠️ Le vol risque "
                "d'être en retard."
            )

        else:

            st.success(
                "✅ Le vol devrait "
                "être à l'heure."
            )


        col1, col2 = st.columns(
            2
        )


        with col1:

            st.metric(
                label=(
                    "Probabilité de retard"
                ),
                value=(
                    f"{delay_probability:.1f} %"
                ),
            )


        with col2:

            st.metric(
                label=(
                    "Probabilité d'être "
                    "à l'heure"
                ),
                value=(
                    f"{on_time_probability:.1f} %"
                ),
            )


    except requests.HTTPError as error:

        try:

            detail = (
                error.response
                .json()
                .get(
                    "detail",
                    "Erreur inconnue",
                )
            )

        except Exception:

            detail = str(
                error
            )


        st.error(
            f"Erreur API : {detail}"
        )


    except requests.RequestException as error:

        st.error(
            "Impossible de contacter "
            "l'API."
        )

        st.code(
            str(error)
        )