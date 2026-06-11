DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "airline_db"
DB_USER = "uAirlines"
DB_PASSWORD = "pAirlines"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)