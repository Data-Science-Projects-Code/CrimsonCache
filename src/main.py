import csv
import factory
from faker import Faker
import random
from datetime import datetime, timedelta
from constants import (
    AGE_DISTRIBUTION_2024,
    SEX_DISTRIBUTION_2024,
    ETHNICITY_DISTRIBUTION,
    BLOOD_TYPE_BY_ETHNICITY,
)
import pandas as pd
import numpy as np

fake = Faker()


# Custom provider to ensure name matches sex
class CustomProvider:
    @staticmethod
    def name(sex):
        if sex == "Male":
            return fake.name_male()
        else:
            return fake.name_female()


# Exponential decay function for first-time donor probability
def first_time_donor_probability(age):
    # Half-life in years, we assume the probability halves every 5 years
    half_life = 5
    initial_probability = 1.0  # 100% at age 17
    decay_factor = 0.5 ** ((age - 17) / half_life)
    return initial_probability * decay_factor


# Factory for creating a donor
class DonorFactory(factory.Factory):
    class Meta:
        model = dict

    donor_id = factory.Sequence(lambda n: n + 1)
    sex = factory.LazyAttribute(
        lambda x: random.choices(
            [sex for sex, _ in SEX_DISTRIBUTION_2024],
            [prob for _, prob in SEX_DISTRIBUTION_2024],
        )[0]
    )
    name = factory.LazyAttribute(lambda x: CustomProvider.name(x.sex))
    age = factory.LazyAttribute(
        lambda x: random.choices(
            [
                age if isinstance(age, int) else random.choice(list(age))
                for age, _ in AGE_DISTRIBUTION_2024
            ],
            [prob for _, prob in AGE_DISTRIBUTION_2024],
        )[0]
    )
    birthdate = factory.LazyAttribute(
        lambda x: datetime.today().replace(year=datetime.today().year - x.age).date()
    )
    ethnicity = factory.LazyAttribute(
        lambda x: random.choices(
            [ethnicity for ethnicity, _ in ETHNICITY_DISTRIBUTION],
            [prob for _, prob in ETHNICITY_DISTRIBUTION],
        )[0]
    )
    blood_type = factory.LazyAttribute(
        lambda x: random.choices(
            [blood_type for blood_type, _ in BLOOD_TYPE_BY_ETHNICITY[x.ethnicity]],
            [prob for _, prob in BLOOD_TYPE_BY_ETHNICITY[x.ethnicity]],
        )[0]
    )
    first_time_donor = factory.LazyAttribute(
        lambda x: random.random() < first_time_donor_probability(x.age)
    )
    number_of_donations = factory.LazyAttribute(
        lambda x: 1 if x.first_time_donor else random.randint(1, 10)
    )
    last_donation_date = factory.LazyAttribute(
        lambda x: fake.date_between(start_date="-5y", end_date="today")
    )


def generate_donation_dates(start_date, num_donations, birthdate):
    min_date = datetime.combine(
        birthdate.replace(year=birthdate.year + 17), datetime.min.time()
    )
    donation_gap = pd.to_timedelta(
        np.random.randint(112, 366, size=num_donations), unit="D"
    )
    donation_dates = (start_date - donation_gap).sort_values(ascending=False)

    # Skip some years randomly
    skip_years = np.random.choice(
        [0, 1, 2, 3], size=num_donations, p=[0.7, 0.15, 0.1, 0.05]
    )
    donation_dates -= pd.to_timedelta(skip_years * 365, unit="D")

    return donation_dates[donation_dates >= min_date].tolist()[:num_donations]


# Function to generate random donation datetime
def generate_random_donation_datetime(start_date):
    random_days = random.randint(0, 28)  # Generate a random day of the month
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return datetime.combine(start_date, datetime.min.time()) + timedelta(
        days=random_days, hours=random_hours, minutes=random_minutes
    )


# Generate the data
donors = []
for _ in range(3000):  # Adjust the number of donors as needed
    donor = DonorFactory()
    donation_dates = generate_donation_dates(
        datetime.today(), donor["number_of_donations"], donor["birthdate"]
    )
    for idx, date in enumerate(donation_dates):
        donors.append(
            {
                "donor_id": donor["donor_id"],
                "name": donor["name"],
                "birthdate": donor["birthdate"].strftime("%Y-%m-%d"),
                "age_at_donation": (date.year - donor["birthdate"].year)
                - (
                    (date.month, date.day)
                    < (donor["birthdate"].month, donor["birthdate"].day)
                ),
                "sex": donor["sex"],
                "ethnicity": donor["ethnicity"],
                "blood_type": donor["blood_type"],
                "first_time_donor": donor["first_time_donor"] if idx == 0 else False,
                "donation_datetime": generate_random_donation_datetime(date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

# Display a sample of the generated data
for donor in donors[:40]:
    print(donor)

# Specify the filename
filename = "../data/donors.csv"

# Define the header
header = [
    "donor_id",
    "name",
    "birthdate",
    "age_at_donation",
    "sex",
    "ethnicity",
    "blood_type",
    "first_time_donor",
    "donation_datetime",
]

# Write the data to a CSV file
with open(filename, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(donors)

print(f"Data has been written to {filename}")

# Load the data from the CSV file
donors_df = pd.read_csv(filename)

# Convert the 'donation_datetime' column to datetime
donors_df["donation_datetime"] = pd.to_datetime(donors_df["donation_datetime"])

# Define the average donations per week
average_donations_per_week = 35

# Calculate the initial weekly counts
donors_df["week"] = donors_df["donation_datetime"].dt.to_period("W")
weekly_counts = donors_df.groupby("week").size()

# Calculate variation (standard deviation)
variation = np.std(weekly_counts)

# Define the minimum and maximum donations
min_donations = max(int(average_donations_per_week - 1.5 * variation), 0)
max_donations = int(average_donations_per_week + 1.5 * variation)


# Adjust the counts based on the seasonal variations
# adjusted_counts = weekly_counts.copy()
#
# for week in adjusted_counts.index:
#     month = week.start_time.month
#     if 6 <= month <= 8:  # Summer months
#         adjusted_counts[week] = int(average_donations_per_week * np.random.uniform(0.8, 0.9))
#     elif 9 <= month <= 11 or 3 <= month <= 5:  # High supply periods
#         adjusted_counts[week] = int(average_donations_per_week * np.random.uniform(1.1, 1.2))
#     else:  # Other periods
#         adjusted_counts[week] = average_donations_per_week
#
#     # Ensure minimum and maximum donations
#     adjusted_counts[week] = min(max(adjusted_counts[week], min_donations), max_donations)
#
def calculate_seasonal_adjustment(weekly_counts, avg_donations):
    variation = weekly_counts.std()
    min_donations = max(int(avg_donations - 1.5 * variation), 0)
    max_donations = int(avg_donations + 1.5 * variation)

    def adjust_week(week):
        month = week.start_time.month
        if 6 <= month <= 8:
            return int(avg_donations * np.random.uniform(0.8, 0.9))
        elif 9 <= month <= 11 or 3 <= month <= 5:
            return int(avg_donations * np.random.uniform(1.1, 1.2))
        else:
            return avg_donations

    adjusted_counts = weekly_counts.apply(adjust_week).clip(
        lower=min_donations, upper=max_donations
    )
    return adjusted_counts


# Adjust the total number of donations to match the adjusted weekly counts
adjusted_donors = []
for week, count in adjusted_counts.items():
    week_donations = donors_df[donors_df["week"] == week]
    if len(week_donations) > count:
        week_donations = week_donations.sample(count)
    elif len(week_donations) < count:
        additional_donors = week_donations.sample(
            count - len(week_donations), replace=True
        )
        week_donations = pd.concat([week_donations, additional_donors])
    adjusted_donors.append(week_donations)

# Combine the adjusted donations into a single DataFrame
adjusted_donors_df = pd.concat(adjusted_donors)

# Shuffle the adjusted DataFrame to mix the donations
adjusted_donors_df = adjusted_donors_df.sample(frac=1).reset_index(drop=True)


# Generate new donation datetimes for the adjusted donations
def generate_donation_datetime_for_week(week_start, count):
    random_days = np.random.randint(0, 7, size=count)
    random_times = [
        timedelta(hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60))
        for _ in range(count)
    ]
    return [
        week_start + timedelta(days=int(day)) + time
        for day, time in zip(random_days, random_times)
    ]


new_donation_datetimes = []
for week in adjusted_counts.index:
    week_start = week.start_time
    donation_datetimes = generate_donation_datetime_for_week(
        week_start, adjusted_counts[week]
    )
    new_donation_datetimes.extend(donation_datetimes)

# Ensure the length matches
if len(new_donation_datetimes) != len(adjusted_donors_df):
    raise ValueError(
        "Length of generated donation datetimes does not match the adjusted donors DataFrame"
    )

# Update the 'donation_datetime' column with the new datetimes
adjusted_donors_df["donation_datetime"] = new_donation_datetimes

# Write the adjusted data to a new CSV file
adjusted_filename = "../data/adjusted_donors.csv"
adjusted_donors_df.to_csv(adjusted_filename, index=False)

print(f"Adjusted data has been written to {adjusted_filename}")
