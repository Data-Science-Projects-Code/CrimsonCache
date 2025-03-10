import os
import sqlite3
import random
import argparse
import logging
from donor_generator import DonorFactory
from donation_history_generator import DonationHistoryGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure required directories exist
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DONOR_DB_PATH = os.path.join(DATA_DIR, "donors.sqlite3")
DONATION_DB_PATH = os.path.join(DATA_DIR, "donations.sqlite3")


def create_donor_database():
    """Create the donors database schema"""
    conn = sqlite3.connect(DONOR_DB_PATH)
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
    logger.info(f"Created donor database schema at {DONOR_DB_PATH}")


def populate_donor_database(num_donors=3000):
    """Generate donors and populate the database"""
    conn = sqlite3.connect(DONOR_DB_PATH)
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
    logger.info(f"Generated {num_donors} donors and saved to {DONOR_DB_PATH}")


def main(num_days=1000, percent_chance=30, min_units=20, max_units=200, seed=42):
    """
    Main function to run the donation history generation

    Args:
        num_days: Number of days of historical data to generate
        percent_chance: Percentage chance of a blood drive on any day
        min_units: Minimum number of units collected per blood drive
        max_units: Maximum number of units collected per blood drive
        seed: Random seed for reproducibility
    """
    # Set random seed
    random.seed(seed)

    # Create donation history generator
    generator = DonationHistoryGenerator(DONOR_DB_PATH, DONATION_DB_PATH, seed)

    try:
        donor_db_exists = os.path.exists(DONOR_DB_PATH)
        donation_db_exists = os.path.exists(DONATION_DB_PATH)

        # Case 1: Donor database exists but donation database doesn't
        if donor_db_exists and not donation_db_exists:
            logger.info("Donor database found but donation database not found.")
            logger.info("Initializing donation database...")
            generator.initialize_donation_database()

            logger.info(f"Generating {num_days} days of historical donation data...")
            generator.generate_historical_data(
                num_days, min_units, max_units, percent_chance
            )

        # Case 2: Both databases exist (daily update)
        elif donor_db_exists and donation_db_exists:
            logger.info("Both donor and donation databases found.")

            # # Validate and fix donation database schema if needed
            # if not generator.validate_and_fix_schema():
            #     logger.error("Failed to validate/fix donation database schema")
            #     return
            #
            logger.info("Generating daily update...")
            # Override num_days to 1 for daily update
            today_db_path = generator.generate_daily_file(
                min_units, max_units, percent_chance
            )

            if today_db_path:
                logger.info(f"Today's donation data saved to: {today_db_path}")
            else:
                logger.info("No blood drive occurred today")

        # Case 3: Neither database exists
        else:
            logger.info("Donor database not found. Creating and populating...")
            create_donor_database()
            populate_donor_database()

            logger.info("Initializing donation database...")
            generator.initialize_donation_database()

            logger.info(f"Generating {num_days} days of historical donation data...")
            generator.generate_historical_data(
                num_days, min_units, max_units, percent_chance
            )

        logger.info("Process completed successfully")
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate blood donation data")
    parser.add_argument(
        "--num_days",
        type=int,
        default=1000,
        help="Number of days of historical data to generate",
    )
    parser.add_argument(
        "--percent_chance",
        type=float,
        default=30,
        help="Percentage chance of a blood drive on any given day",
    )
    parser.add_argument(
        "--min_units",
        type=int,
        default=20,
        help="Minimum number of units collected per blood drive",
    )
    parser.add_argument(
        "--max_units",
        type=int,
        default=200,
        help="Maximum number of units collected per blood drive",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    # Run the main function with parsed arguments
    main(
        num_days=args.num_days,
        percent_chance=args.percent_chance,
        min_units=args.min_units,
        max_units=args.max_units,
        seed=args.seed,
    )
