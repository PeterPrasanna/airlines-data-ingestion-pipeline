import pandas as pd
import requests
from src.config import DATABASE_URL
from sqlalchemy import create_engine, text

FILE_ID = "1PxxstMGuqK_qZnHD5qaw7OghADE4YEYl"
url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

response = requests.get(url)
response.raise_for_status()

raw = response.json()

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
    "fleet_average_age": pd.to_numeric(df_airlines["fleet_average_age"], errors="coerce"),
    "status":       df_airlines["status"]
})

df_airlines_clean = df_airlines_clean.dropna(
    subset=["airline_id", "iata_code", "country_name", "date_founded","fleet_average_age"]
)

df_airlines_clean = df_airlines_clean.drop_duplicates(subset=["iata_code"])

print(len(df_airlines_clean))
#df_airlines_clean = df_airlines_clean.head(10)

# Supprimer les iata_code dupliqués ou invalides (ex: "DO*")
df_airlines_clean = df_airlines_clean[df_airlines_clean["iata_code"].str.match(r'^[A-Z0-9]{2,3}$', na=False)]
df_airlines_clean = df_airlines_clean.drop_duplicates(subset=["iata_code"])

print(f"Après nettoyage doublons : {len(df_airlines_clean)} airlines")

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    for _, row in df_airlines_clean.iterrows():
        conn.execute(text("""
            INSERT INTO airlines (
                airline_id,
                airline_name,
                iata_code,
                country_iso2,
                country_name,
                date_founded,
                fleet_size,
                fleet_average_age,
                status
            )
            VALUES (
                :airline_id,
                :airline_name,
                :iata_code,
                :country_iso2,
                :country_name,
                :date_founded,
                :fleet_size,
                :fleet_average_age,
                :status
            )
            ON CONFLICT (airline_id) DO NOTHING
        """), row.to_dict())

print("Import airlines terminé")