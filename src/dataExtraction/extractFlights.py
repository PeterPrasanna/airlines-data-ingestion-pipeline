import csv
from config import get_db_connection

def load_flights(filepath="data/raw/flights_sample_3M.csv"):
    conn = get_db_connection()
    cur = conn.cursor()

    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
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
                row["CRS_DEP_TIME"] or None,
                row["DEP_TIME"] or None,
                row["ARR_TIME"] or None,
                row["CRS_ARR_TIME"] or None,
                row["DELAY_DUE_CARRIER"] or None,
                row["DELAY_DUE_WEATHER"] or None,
                row["DELAY_DUE_NAS"] or None,
                row["DELAY_DUE_SECURITY"] or None,
                row["DELAY_DUE_LATE_AIRCRAFT"] or None
            ))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Flights chargés")

if __name__ == "__main__":
    load_flights()