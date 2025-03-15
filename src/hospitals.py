import os
import sqlite3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure required directories exist
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
HOSPITAL_DB_PATH = os.path.join(DATA_DIR, "hospitals.sqlite3")


def create_hospitals_db(db_filename="hospitals.sqlite3"):
    """Creates an SQLite3 database with the hospitals table and populates it with data."""

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Create the hospitals table
    cursor.execute("""
        CREATE TABLE hospitals (
            NPI INTEGER PRIMARY KEY,
            address TEXT,
            tel TEXT,
            POC TEXT
        )
    """)

    # Insert hospital data
    hospitals_data = [
        (
            1538535463,
            "2 Bernardine Dr, Newport News, VA 23602",
            "+17578866000",
            "Emma Harrison",
        ),
        (
            1750399192,
            "3636 High St, Portsmouth, VA 23707",
            "+1 757 398 2200 ext 220",
            "Lucas Bennett",
        ),
        (
            1366547747,
            "500 J Clyde Morris Blvd, Newport News, VA 23601",
            "+17575942000",
            "Olivia Parker",
        ),
        (
            1528162534,
            "7547 Medical Dr, Gloucester, VA 23061, United States",
            "+18046938800",
            "Ethan Wright",
        ),
        (
            1104086685,
            "3000 Coliseum Dr, Hampton, VA 23666",
            "+17577361000",
            "Sophia Coleman",
        ),
        (
            1811957681,
            "830 Kempsville Rd, Norfolk, VA 23502",
            "+17572616000",
            "Noah Turner",
        ),
        (
            1437119310,
            "600 Gresham Dr, Norfolk, VA 23507",
            "+17573883000",
            "Isabella Reed",
        ),
        (1376540138, "2800 Godwin Blvd, Suffolk", "+1 757 934 4000", "Mason Campbell"),
        (
            1528028396,
            "2025 Glenn Mitchell Dr, Virginia Beach, VA 23456, United States",
            "+17575071000",
            "Amelia Foster",
        ),
        (
            1629038336,
            "1060 1st Colonial Rd, Virginia Beach, VA 23451",
            "+17573958000",
            "Liam Griffin",
        ),
        (
            1710613807,
            "2021 Concert Dr, Virginia Beach, VA 23456",
            "1 757 668 2711",
            "Riley Morgan",
        ),
    ]

    cursor.executemany(
        "INSERT INTO hospitals (NPI, address, tel, POC) VALUES (?, ?, ?, ?)",
        hospitals_data,
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_hospitals_db(HOSPITAL_DB_PATH)
    print("hospitals.sqlite3 created successfully.")
