import os
import sys
import sqlite3
import pytest



# Add the parent directory (containing src/) to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from main import DONOR_DB_PATH

def test_database_exists():
    """Ensure the database file exists."""
    assert os.path.exists(DONOR_DB_PATH), (
        "Database file does not exist. Try running donor_generator.py"
    )


def test_donors_table_has_data():
    """Check that the donors table contains at least one record."""
    conn = sqlite3.connect(DONOR_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM donors")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "No donors found in the database"


def test_donors_table_structure():
    """Ensure all expected columns exist in the donors table."""
    expected_columns = {
        "donor_id",
        "unique_id",
        "name",
        "birthdate",
        "age",
        "sex",
        "ethnicity",
        "blood_type",
        "first_donation_date",
        "last_donation_date",
        "total_donations",
    }
    conn = sqlite3.connect(DONOR_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(donors)")
    actual_columns = {row[1] for row in cursor.fetchall()}
    conn.close()
    assert expected_columns.issubset(actual_columns), (
        "Missing expected columns in donors table"
    )


def test_no_donor_under_17():
    """Ensure no donor is younger than 17."""
    conn = sqlite3.connect(DONOR_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM donors WHERE age < 17")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0, "Some donors are under 17 years old!"
