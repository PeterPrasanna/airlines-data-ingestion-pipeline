import itertools
import requests

API_URL = "http://localhost:8000/predict"

HEADERS = {
    "Authorization": "airlines",
    "Content-Type": "application/json",
}

airlines = ["AA", "UA", "DL", "WN", "B6"]
routes = [
    ("JFK", "LAX", 2475, 390),
    ("ORD", "SFO", 1846, 280),
    ("ATL", "LAX", 1946, 300),
    ("LAX", "JFK", 2475, 330),
    ("MIA", "JFK", 1090, 190),
]

dates = [
    "2024-06-28",
    "2024-07-05",
    "2024-07-12",
    "2024-07-19",
    "2024-07-26",
]

times = [
    600,
    1200,
    1600,
    1800,
    2000,
    2200,
    2350,
]

best_result = None

for airline, route, flight_date, departure_time in itertools.product(
    airlines,
    routes,
    dates,
    times,
):
    origin, destination, distance, elapsed_time = route

    payload = {
        "airline_code": airline,
        "origin": origin,
        "destination": destination,
        "flight_date": flight_date,
        "scheduled_departure_time": departure_time,
        "departure_delay": 0,
        "scheduled_elapsed_time": elapsed_time,
        "distance": distance,
    }

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=10,
    )

    if response.status_code != 200:
        continue

    result = response.json()
    probability = result["delay_probability"]

    if (
        best_result is None
        or probability > best_result["probability"]
    ):
        best_result = {
            "payload": payload,
            "result": result,
            "probability": probability,
        }

if best_result:
    print("Meilleure probabilité de retard trouvée :")
    print(best_result["payload"])
    print(best_result["result"])
else:
    print("Aucune requête valide.")