import json
import pandas as pd
from src.utils.paths import RAW_DATA
from src.config import DATABASE_URL
from sqlalchemy import create_engine

file_path = RAW_DATA / "airlines.json"

with open(file_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

df_airlines = pd.DataFrame(raw["data"])
df_airlines = df_airlines[df_airlines["status"] == "active"]

df_airlines_clean = pd.DataFrame({
    "iata_code": df_airlines["iata_code"],
    "icao_code": df_airlines["icao_code"],
    "name": df_airlines["airline_name"],
    "country": df_airlines["country_name"],
    "fleet_size": pd.to_numeric(df_airlines["fleet_size"], errors="coerce"),
    "status": df_airlines["status"],
    "type": df_airlines["type"]
})

df_airlines_clean = df_airlines_clean.dropna(subset=["iata_code", "icao_code", "country","type"])

print(len(df_airlines_clean))
#df_airlines_clean = df_airlines_clean.head(10)

engine = create_engine(DATABASE_URL)

df_airlines_clean.to_sql(
    "airlines",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print("Import airlines terminé")