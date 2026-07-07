import pandas as pd
import requests
from src.config import DATABASE_URL
from sqlalchemy import create_engine

FILE_ID = "1hL1_dc4RFOpLiux15pTEU0cGxEqwDIq7"
url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

response = requests.get(url)
response.raise_for_status()

raw = response.json()

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

