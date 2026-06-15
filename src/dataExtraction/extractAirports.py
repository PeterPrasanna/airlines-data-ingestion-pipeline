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
    "iata_code": df_airports["iata_code"],
    "name": df_airports["airport_name"],
    "country": df_airports["country_name"],
    "latitude": pd.to_numeric(df_airports["latitude"], errors="coerce"),
    "longitude": pd.to_numeric(df_airports["longitude"], errors="coerce")
})

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

