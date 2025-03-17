import os
import uuid
import sqlite3
import logging
from faker import Faker
import factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
EMPLOYEE_DB_PATH = os.path.join(DATA_DIR, "employees.sqlite3")

fake = Faker()


class EmployeeFactory(factory.Factory):
    class Meta:
        model = dict

    employee_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.LazyFunction(lambda: fake.name())
    hire_date = factory.LazyFunction(
        lambda: fake.date_between(start_date="-10y", end_date="today")
    )


def create_employee_db():
    """Create the employees database if it doesn't exist."""
    logger.info(f"Creating employees database at {EMPLOYEE_DB_PATH}")

    conn = sqlite3.connect(EMPLOYEE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        name TEXT,
        hire_date DATE
    )
    """)

    conn.commit()
    conn.close()

    logger.info("Employees database created successfully")


def generate_employees(num_employees=50):
    """Generate a specified number of employees and add them to the database."""
    logger.info(f"Generating {num_employees} employees")

    create_employee_db()

    conn = sqlite3.connect(EMPLOYEE_DB_PATH)
    cursor = conn.cursor()

    for _ in range(num_employees):
        employee = EmployeeFactory()

        try:
            cursor.execute(
                "INSERT INTO employees (employee_id, name, hire_date) VALUES (?, ?, ?)",
                (employee["employee_id"], employee["name"], employee["hire_date"]),
            )
        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate employee ID generated, skipping")
            continue

    conn.commit()
    conn.close()

    logger.info(f"Successfully generated {num_employees} employees")


def get_employee_count():
    """Get the count of employees in the database."""
    conn = sqlite3.connect(EMPLOYEE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]

    conn.close()

    return count


if __name__ == "__main__":
    generate_employees()
    logger.info(f"Total employees in database: {get_employee_count()}")
