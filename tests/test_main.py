import os
import sys
import sqlite3
import pytest

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
