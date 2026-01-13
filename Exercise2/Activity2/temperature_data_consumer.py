import time
from datetime import datetime, timedelta
import psycopg2

DB_NAME = "office_db"
DB_USER = "postgres"
DB_PASSWORD = "postgrespw"
DB_HOST = "127.0.0.1"
DB_PORT = 5433

QUERY = """
SELECT AVG(temperature)
FROM temperature_readings
WHERE recorded_at >= %s;
"""

def fetch_avg_last_10_minutes(conn):
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    with conn.cursor() as cur:
        cur.execute(QUERY, (ten_minutes_ago,))
        (avg_temp,) = cur.fetchone()
        return avg_temp

def main():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    try:
        while True:
            avg_temp = fetch_avg_last_10_minutes(conn)
            if avg_temp is not None:
                print(f"{datetime.now()} - Average temperature last 10 minutes: {avg_temp:.2f} °C")
            else:
                print(f"{datetime.now()} - No data in last 10 minutes.")
            time.sleep(600)
    except KeyboardInterrupt:
        print("Stopped consuming data.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
