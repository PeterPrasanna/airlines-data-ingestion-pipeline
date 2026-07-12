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
    "airline_id":    df_airlines["airline_id"],
    "airline_name": df_airlines["airline_name"],
    "iata_code":    df_airlines["iata_code"],
    "country_iso2":    df_airlines["country_iso2"],
    "country_name": df_airlines["country_name"],
    "date_founded":   pd.to_numeric(df_airlines["date_founded"], errors="coerce"),
    "fleet_size":   pd.to_numeric(df_airlines["fleet_size"], errors="coerce"),
    "fleet_average_age":         df_airlines["fleet_average_age"],
    "status":       df_airlines["status"]
})


print(len(df_airlines_clean))
#df_airlines_clean = df_airlines_clean.head(10)

# Supprimer les iata_code dupliqués ou invalides (ex: "DO*")
df_airlines_clean = df_airlines_clean[df_airlines_clean["iata_code"].str.match(r'^[A-Z0-9]{2,3}$', na=False)]
df_airlines_clean = df_airlines_clean.drop_duplicates(subset=["iata_code"])

print(f"Après nettoyage doublons : {len(df_airlines_clean)} airlines")

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