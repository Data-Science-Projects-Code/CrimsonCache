import os
import sqlite3
import random
import uuid
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DonationHistoryGenerator:
    """Generates historical donation records based on specified parameters"""

    def __init__(self, donor_db_path, donation_db_path, seed=42):
        """
        Initialize the donation history generator

        Args:
            donor_db_path: Path to the donors database
            donation_db_path: Path to the donations database
            seed: Random seed for reproducibility
        """
        random.seed(seed)
        self.donor_db_path = donor_db_path
        self.donation_db_path = donation_db_path

    def initialize_donation_database(self):
        """Create the donations table if it doesn't exist"""
        conn = sqlite3.connect(self.donation_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            bag_id TEXT PRIMARY KEY,
            donor_id TEXT,
            event_id TEXT,
            donation_date DATE,
            test_date DATE,
            test_result BOOLEAN,
            status TEXT,
            FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
        )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Initialized donation database at {self.donation_db_path}")

    def get_eligible_donors(self, current_date_str):
        """
        Get list of eligible donors who haven't donated in the past 56 days
        
        Args:
            current_date_str: Current date in 'YYYY-MM-DD' format
            
        Returns:
            List of eligible donor records
        """
        if not os.path.exists(self.donor_db_path):
            logger.error(f"Donor database not found at {self.donor_db_path}")
            return []

        try:
            conn = sqlite3.connect(self.donor_db_path)
            cursor = conn.cursor()
            
            # Convert date string to datetime for comparison
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
            cutoff_date = current_date - timedelta(days=56)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Efficiently query only eligible donors
            cursor.execute("""
                SELECT * FROM donors 
                WHERE last_donation_date IS NULL 
                OR last_donation_date <= ?
            """, (cutoff_date_str,))
            
            eligible_donors = cursor.fetchall()
            conn.close()
            
            logger.info(f"Found {len(eligible_donors)} eligible donors for {current_date_str}")
            return eligible_donors
            
        except Exception as e:
            logger.error(f"Error retrieving eligible donors: {e}")
            return []

    def update_donor_donation_info(self, donor_id, donation_date):
        """
        Update donor's last donation date and increment total donations

        Args:
            donor_id: The donor's ID
            donation_date: The new donation date

        Returns:
            bool: True if successful
        """
        try:
            conn = sqlite3.connect(self.donor_db_path)
            cursor = conn.cursor()

            # Get current total_donations
            cursor.execute(
                "SELECT total_donations FROM donors WHERE donor_id = ?", (donor_id,)
            )
            result = cursor.fetchone()
            current_donations = result[0] if result[0] is not None else 0

            # Update the donor information
            cursor.execute(
                """
                UPDATE donors 
                SET last_donation_date = ?, total_donations = ? 
                WHERE donor_id = ?
                """,
                (donation_date, current_donations + 1, donor_id),
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error updating donor information: {e}")
            return False

    def generate_donation_event(self, donation_date, donor_id, donor_blood_type):
        """
        Generate a single donation event

        Args:
            donation_date: Date of the donation
            donor_id: ID of the donor
            donor_blood_type: Blood type of the donor

        Returns:
            dict: Donation event data
        """
        event_id = str(uuid.uuid4())

        # Generate donation with a random time between 8am and 5pm
        donation_datetime = datetime.strptime(donation_date, "%Y-%m-%d")
        donation_datetime = donation_datetime.replace(
            hour=random.randint(8, 17),
            minute=random.randint(0, 59),
        )

        # Test date is the day after donation
        test_date = (donation_datetime + timedelta(days=1)).strftime("%Y-%m-%d")

        return {
            "bag_id": f"{donor_blood_type}-{str(uuid.uuid4())[:8]}",
            "donor_id": donor_id,
            "event_id": event_id,
            "donation_date": donation_date,
            "test_date": test_date,
            "test_result": random.random() < 0.998,  # 99.8% pass rate
            "status": "available" if random.random() < 0.95 else "used",
        }

    def save_donation_events(self, events):
        """
        Save donation events to the database

        Args:
            events: List of donation event dictionaries

        Returns:
            bool: True if successful
        """
        if not events:
            logger.warning("No events to save")
            return False

        try:
            conn = sqlite3.connect(self.donation_db_path)
            cursor = conn.cursor()

            for event in events:
                # Fixed: Added all necessary fields from event to the INSERT statement
                cursor.execute(
                    """
                    INSERT INTO donations 
                    (bag_id, donor_id, event_id, donation_date, test_date, test_result, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event["bag_id"],
                        event["donor_id"],
                        event["event_id"],
                        event["donation_date"],
                        event["test_date"],
                        event["test_result"],
                        event["status"],
                    ),
                )

            conn.commit()
            conn.close()
            logger.info(f"Saved {len(events)} donation events to database")
            return True

        except Exception as e:
            logger.error(f"Error saving donation events: {e}")
            return False

    def generate_daily_donations(self, date_str, min_units, max_units, percent_chance):
        """
        Generate donations for a single day if a blood drive occurs

        Args:
            date_str: The date to generate donations for in 'YYYY-MM-DD' format
            min_units: Minimum number of units to collect
            max_units: Maximum number of units to collect
            percent_chance: Chance of a blood drive occurring

        Returns:
            list: List of donation events, empty if no blood drive
        """
        # Determine if there's a blood drive today
        if random.random() > percent_chance / 100:
            logger.info(f"No blood drive on {date_str}")
            return []

        # Determine number of units to collect
        units_to_collect = random.randint(min_units, max_units)
        logger.info(f"Blood drive on {date_str} with target of {units_to_collect} units")

        # Get eligible donors for this date
        eligible_donors = self.get_eligible_donors(date_str)
        if not eligible_donors:
            logger.warning(f"No eligible donors available for {date_str}")
            return []

        # Column indices from the donors table
        DONOR_ID_IDX = 0
        BLOOD_TYPE_IDX = 7

        donation_events = []
        random.shuffle(eligible_donors)  # Randomize donor order

        # Go through donors until we collect enough units or run out of eligible donors
        for donor in eligible_donors:
            if len(donation_events) >= units_to_collect:
                break

            donor_id = donor[DONOR_ID_IDX]
            blood_type = donor[BLOOD_TYPE_IDX]

            # Create donation event
            donation_event = self.generate_donation_event(date_str, donor_id, blood_type)
            donation_events.append(donation_event)

            # Update donor's information
            self.update_donor_donation_info(donor_id, date_str)

        logger.info(f"Generated {len(donation_events)} donations for {date_str}")
        return donation_events

    def generate_historical_data(self, num_days, min_units, max_units, percent_chance):
        """
        Generate historical donation data for the specified number of days

        Args:
            num_days: Number of days in the past to generate data for
            min_units: Minimum number of units per blood drive
            max_units: Maximum number of units per blood drive
            percent_chance: Percentage chance of a blood drive on any day

        Returns:
            bool: True if successful
        """
        # Initialize the donation database first to ensure table exists
        self.initialize_donation_database()

        # Get the current date and calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=num_days)

        current_date = start_date
        total_events = 0
        total_days_processed = 0

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            total_days_processed += 1

            # Generate donations for this day
            daily_events = self.generate_daily_donations(
                date_str, min_units, max_units, percent_chance
            )

            # Save events if any were generated
            if daily_events:
                success = self.save_donation_events(daily_events)
                if success:
                    total_events += len(daily_events)
                    logger.info(f"Successfully saved {len(daily_events)} events for {date_str}")
                else:
                    logger.error(f"Failed to save events for {date_str}")

            # Move to next day
            current_date += timedelta(days=1)

            # Log progress every 30 days
            if total_days_processed % 30 == 0:
                logger.info(
                    f"Processed {total_days_processed}/{num_days} days, generated {total_events} events so far"
                )

        logger.info(
            f"Historical data generation complete. Generated {total_events} donations over {num_days} days"
        )
        return True

    def generate_daily_file(self, min_units, max_units, percent_chance):
        """
        Generate a separate SQLite file for today's donations

        Args:
            min_units: Minimum number of units per blood drive
            max_units: Maximum number of units per blood drive
            percent_chance: Percentage chance of a blood drive

        Returns:
            str: Path to the generated file, or None if no blood drive
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # Generate today's donations
        daily_events = self.generate_daily_donations(
            today, min_units, max_units, percent_chance
        )

        if not daily_events:
            logger.info(f"No blood drive today ({today})")
            return None

        # Create a new database file for today
        data_dir = os.path.dirname(self.donation_db_path)
        today_db_path = os.path.join(data_dir, f"{today}_activity.sqlite3")

        # Create the database and table
        conn = sqlite3.connect(today_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            bag_id TEXT PRIMARY KEY,
            donor_id TEXT,
            event_id TEXT,
            donation_date DATE,
            test_date DATE,
            test_result BOOLEAN,
            status TEXT
        )
        """)

        # Save the events
        for event in daily_events:
            cursor.execute(
                """
                INSERT INTO donations 
                (bag_id, donor_id, event_id, donation_date, test_date, test_result, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["bag_id"],
                    event["donor_id"],
                    event["event_id"],
                    event["donation_date"],
                    event["test_date"],
                    event["test_result"],
                    event["status"],
                ),
            )

        conn.commit()
        conn.close()

        logger.info(
            f"Generated {len(daily_events)} donations for today, saved to {today_db_path}"
        )
        return today_db_path
        
    def check_donation_records(self):
        """
        Check if donation records exist in the database
        
        Returns:
            int: Number of records in the donations table
        """
        try:
            if not os.path.exists(self.donation_db_path):
                return 0
                
            conn = sqlite3.connect(self.donation_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM donations")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error checking donation records: {e}")
            return 0
