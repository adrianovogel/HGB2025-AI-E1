import time
import random
from datetime import datetime
import psycopg2

DB_NAME = "mydb"
DB_USER = "postgres"
DB_PASSWORD = "postgrespw"
DB_HOST = "127.0.0.1"
DB_PORT = 5433  # change to 5433 if your docker port is mapped to 5433

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    card_id VARCHAR(32) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    country VARCHAR(2) NOT NULL,
    merchant VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

def main():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)

    cards = [f"card_{i}" for i in range(1, 200)]
    countries = ["AT", "DE", "FR", "IT", "ES", "RO", "US", "GB"]
    merchants = ["AMZ", "BILLA", "SPAR", "UBER", "APPLE", "ZALANDO", "IKEA"]

    with conn.cursor() as cur:
        while True:
            card_id = random.choice(cards)
            amount = round(random.uniform(1, 2500), 2)
            country = random.choice(countries)
            merchant = random.choice(merchants)
            ts = datetime.utcnow()

            cur.execute(
                "INSERT INTO transactions (card_id, amount, country, merchant, created_at) VALUES (%s,%s,%s,%s,%s)",
                (card_id, amount, country, merchant, ts),
            )
            print(f"{ts} inserted tx: {card_id} {amount} {country} {merchant}")
            time.sleep(0.01)  # increase/decrease rate

if __name__ == "__main__":
    main()
