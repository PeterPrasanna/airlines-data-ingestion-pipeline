import csv
import psycopg2
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def format_time(value):
    """Convertit 954 → '09:54', 1430 → '14:30', '' → None"""
    if not value or str(value).strip() == '' or str(value).strip() == 'nan':
        return None
    try:
        val = str(value).split('.')[0].zfill(4)  # 954 → '0954'
        return f"{val[:2]}:{val[2:]}"             # '0954' → '09:54'
    except:
        return None


def load_flights(filepath="data/raw/flights_sample_3m.csv"):
    conn = get_db_connection()
    cur = conn.cursor()

    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        count = 0

        for row in reader:
            try:
                # Table flights
                cur.execute("""
                    INSERT INTO flights (
                        fl_number, fl_date, airline_code,
                        origin, dest, distance,
                        cancelled, cancellation_code, diverted
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (fl_number, fl_date) DO NOTHING
                """, (
                    row["FL_NUMBER"],
                    row["FL_DATE"],
                    row["AIRLINE_CODE"],
                    row["ORIGIN"],
                    row["DEST"],
                    row["DISTANCE"] or None,
                    row["CANCELLED"] == "1",
                    row["CANCELLATION_CODE"] or None,
                    row["DIVERTED"] == "1"
                ))

                # Table flight_informations
                cur.execute("""
                    INSERT INTO flight_informations (
                        fl_number, fl_date,
                        crs_dep_time, dep_time, arr_time, crs_arr_time,
                        delay_due_carrier, delay_due_weather, delay_due_nas,
                        delay_due_security, delay_due_late_aircraft
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (fl_number, fl_date) DO NOTHING
                """, (
                    row["FL_NUMBER"],
                    row["FL_DATE"],
                    format_time(row["CRS_DEP_TIME"]),
                    format_time(row["DEP_TIME"]),
                    format_time(row["ARR_TIME"]),
                    format_time(row["CRS_ARR_TIME"]),
                    row["DELAY_DUE_CARRIER"] or None,
                    row["DELAY_DUE_WEATHER"] or None,
                    row["DELAY_DUE_NAS"] or None,
                    row["DELAY_DUE_SECURITY"] or None,
                    row["DELAY_DUE_LATE_AIRCRAFT"] or None
                ))

                count += 1

                # Commit tous les 10 000 vols pour ne pas tout perdre en cas d'erreur
                if count % 10000 == 0:
                    conn.commit()
                    print(f"  → {count:,} vols insérés...")

            except Exception as e:
                conn.rollback()
                print(f"Erreur sur la ligne {count} : {e}")
                continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"Flights chargés ! Total : {count:,} vols insérés")


if __name__ == "__main__":
    load_flights()