import os
import sqlite3
import logging
from d4 import DonorFactory

# Ensure required directories exist
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "donors.sqlite3")
logging.basicConfig(level=logging.INFO)


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        donor_id TEXT PRIMARY KEY,
        unique_id TEXT UNIQUE,
        name TEXT,
        birthdate DATE,
        age INTEGER,
        sex TEXT,
        ethnicity TEXT,
        blood_type TEXT,
        first_donation_date DATE,
        last_donation_date DATE,
        total_donations INTEGER
    )
    """)
    conn.commit()
    conn.close()


def populate_database(num_donors: int = 3000):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _ in range(num_donors):
        donor = DonorFactory()
        cursor.execute(
            """
            INSERT INTO donors (donor_id, unique_id, name, birthdate, age, sex, ethnicity, blood_type, first_donation_date, last_donation_date, total_donations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                donor["donor_id"],
                donor["unique_id"],
                donor["name"],
                donor["birthdate"],
                donor["age"],
                donor["sex"],
                donor["ethnicity"],
                donor["blood_type"],
                donor["first_donation_date"],
                donor["last_donation_date"],
                donor["total_donations"],
            ),
        )

    conn.commit()
    conn.close()
    logging.info(f"Generated {num_donors} donors and saved to {DB_PATH}")
    print(f"Generated {num_donors} donors and saved database to {DB_PATH}")


if __name__ == "__main__":
    create_database()
    populate_database()
