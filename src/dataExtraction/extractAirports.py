import json
import pandas as pd
from src.utils.paths import RAW_DATA
from src.config import DATABASE_URL
from sqlalchemy import create_engine

file_path = RAW_DATA / "airports.json"

with open(file_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

df_airports = pd.DataFrame(raw["data"])


df_airports_clean = pd.DataFrame({
    "airport_id":    df_airports["airport_id"],
    "airport_name":  df_airports["airport_name"],
    "iata_code":     df_airports["iata_code"],
    "city_iata_code": df_airports["city_iata_code"],
    "country_iso2":  df_airports["country_iso2"],
    "country_name":  df_airports["country_name"],
    "gmt":           pd.to_numeric(df_airports["gmt"], errors="coerce"),
    "timezone":      df_airports["timezone"],
    "latitude":      pd.to_numeric(df_airports["latitude"], errors="coerce"),
    "longitude":     pd.to_numeric(df_airports["longitude"], errors="coerce")
})

# Tronquer country_iso2 à 2 caractères max et filtrer les iata_code invalides
df_airports_clean["country_iso2"] = df_airports_clean["country_iso2"].str[:2]
df_airports_clean = df_airports_clean[
    df_airports_clean["iata_code"].str.match(r'^[A-Z0-9]{3}$', na=False)
]
df_airports_clean = df_airports_clean.drop_duplicates(subset=["iata_code"])

print(f"Après nettoyage : {len(df_airports_clean)} airports")

engine = create_engine(DATABASE_URL)

df_airports_clean.to_sql(
    "airports",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print("Import airports terminé")

