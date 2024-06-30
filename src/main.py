import csv
import factory
from faker import Faker
import random
from datetime import datetime, timedelta
import math
from constants import AGE_DISTRIBUTION_2024, SEX_DISTRIBUTION_2024, ETHNICITY_DISTRIBUTION, BLOOD_TYPE_BY_ETHNICITY


fake = Faker()


# Custom provider to ensure name matches sex
class CustomProvider:
    @staticmethod
    def name(sex):
        if sex == 'Male':
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
    sex = factory.LazyAttribute(lambda x: random.choices(
        [sex for sex, _ in sex_distribution_2024],
        [prob for _, prob in sex_distribution_2024]
    )[0])
    name = factory.LazyAttribute(lambda x: CustomProvider.name(x.sex))
    age = factory.LazyAttribute(lambda x: random.choices(
        [age if isinstance(age, int) else random.choice(list(age)) for age, _ in age_distribution_2024],
        [prob for _, prob in age_distribution_2024]
    )[0])
    birthdate = factory.LazyAttribute(lambda x: datetime.today().replace(year=datetime.today().year - x.age).date())
    ethnicity = factory.LazyAttribute(lambda x: random.choices(
        [ethnicity for ethnicity, _ in ethnicity_distribution],
        [prob for _, prob in ethnicity_distribution]
    )[0])
    blood_type = factory.LazyAttribute(lambda x: random.choices(
        [blood_type for blood_type, _ in blood_type_by_ethnicity[x.ethnicity]],
        [prob for _, prob in blood_type_by_ethnicity[x.ethnicity]]
    )[0])
    first_time_donor = factory.LazyAttribute(lambda x: random.random() < first_time_donor_probability(x.age))
    number_of_donations = factory.LazyAttribute(lambda x: 1 if x.first_time_donor else random.randint(1, 10))
    last_donation_date = factory.LazyAttribute(lambda x: fake.date_between(start_date='-5y', end_date='today'))

# Function to generate donation dates ensuring they are at least 112 days apart and within a valid age range
def generate_donation_dates(start_date, num_donations, birthdate):
    donation_dates = []
    current_date = datetime.combine(start_date, datetime.min.time())
    min_date = datetime.combine(birthdate.replace(year=birthdate.year + 17), datetime.min.time())
    min_donation_date = datetime.strptime('2019-01-01', '%Y-%m-%d')
    while len(donation_dates) < num_donations:
        if current_date < min_date or current_date < min_donation_date:
            break
        # Random hour and minute to simulate semi-random donation times
        random_hour = random.randint(8, 18)  # Assuming donations happen during daytime
        random_minute = random.randint(0, 59)
        current_date_time = current_date.replace(hour=random_hour, minute=random_minute)
        donation_dates.append(current_date_time)
        current_date -= timedelta(days=random.randint(112, 365))
        # Randomly skip some years
        if random.random() < 0.3:
            current_date -= timedelta(days=365 * random.randint(1, 3))
    return donation_dates

# Function to generate random donation datetime
def generate_random_donation_datetime(start_date):
    random_days = random.randint(0, 28)  # Generate a random day of the month
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return datetime.combine(start_date, datetime.min.time()) + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)

# Generate the data
donors = []
for _ in range(3000):  # Adjust the number of donors as needed
    donor = DonorFactory()
    donation_dates = generate_donation_dates(datetime.today(), donor['number_of_donations'], donor['birthdate'])
    for idx, date in enumerate(donation_dates):
        donors.append({
            'donor_id': donor['donor_id'],
            'name': donor['name'],
            'birthdate': donor['birthdate'].strftime('%Y-%m-%d'),
            'age_at_donation': (date.year - donor['birthdate'].year) - ((date.month, date.day) < (donor['birthdate'].month, donor['birthdate'].day)),
            'sex': donor['sex'],
            'ethnicity': donor['ethnicity'],
            'blood_type': donor['blood_type'],
            'first_time_donor': donor['first_time_donor'] if idx == 0 else False,
            'donation_date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'donation_datetime': generate_random_donation_datetime(date).strftime('%Y-%m-%d %H:%M:%S')
        })



# Display a sample of the generated data
for donor in donors[:40]:
    print(donor)


# Specify the filename
filename = '../data/donors.csv'

# Define the header
header = ['donor_id', 'name', 'birthdate', 'age_at_donation', 'sex', 'ethnicity', 'blood_type', 'first_time_donor', 'donation_date', 'donation_datetime']

# Write the data to a CSV file
with open(filename, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    for donor in donors:
        writer.writerow(donor)

print(f"Data has been written to {filename}")

