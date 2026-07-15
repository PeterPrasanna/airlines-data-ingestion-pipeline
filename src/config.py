import psycopg2
import os


DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "airline_db"
DB_USER = "uAirlines"
DB_PASSWORD = "pAirlines"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def get_db_connection(): return psycopg2.connect( host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD )

API_TOKEN = os.getenv("API_TOKEN", "airlines")