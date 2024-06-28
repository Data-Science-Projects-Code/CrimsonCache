import factory
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Define blood type distribution by ethnicity
blood_type_distribution_by_ethnicity = {
    'White': {'O': 0.45, 'A': 0.40, 'B': 0.11, 'AB': 0.04},
    'Hispanic': {'O': 0.57, 'A': 0.31, 'B': 0.10, 'AB': 0.03},
    'Black': {'O': 0.50, 'A': 0.26, 'B': 0.20, 'AB': 0.04},
    'Asian': {'O': 0.40, 'A': 0.28, 'B': 0.25, 'AB': 0.07},
    'Native American': {'O': 0.55, 'A': 0.35, 'B': 0.08, 'AB': 0.03},
    'Other': {'O': 0.47, 'A': 0.37, 'B': 0.12, 'AB': 0.04}
}

# Ethnicity distribution by year
ethnicity_distribution_by_year = {
    2019: {'White': 0.87, 'Black': 0.027, 'Hispanic': 0.058, 'Asian': 0.030, 'Native American': 0.005, 'Other': 0.005},
    2020: {'White': 0.845, 'Black': 0.0233, 'Hispanic': 0.053, 'Asian': 0.027, 'Native American': 0.0045, 'Other': 0.005},
    2021: {'White': 0.80, 'Black': 0.0175, 'Hispanic': 0.048, 'Asian': 0.0195, 'Native American': 0.003, 'Other': 0.005},
    2022: {'White': 0.80, 'Black': 0.0175, 'Hispanic': 0.048, 'Asian': 0.0195, 'Native American': 0.003, 'Other': 0.005},
    2023: {'White': 0.80, 'Black': 0.0175, 'Hispanic': 0.048, 'Asian': 0.0195, 'Native American': 0.003, 'Other': 0.005},
    2024: {'White': 0.80, 'Black': 0.0175, 'Hispanic': 0.048, 'Asian': 0.0195, 'Native American': 0.003, 'Other': 0.005}
}

# Gender distribution by year
gender_distribution_by_year = {
    2019: {'Male': 0.51, 'Female': 0.49},
    2020: {'Male': 0.4845, 'Female': 0.5155},
    2021: {'Male': 0.459, 'Female': 0.541},
    2022: {'Male': 0.459, 'Female': 0.541},
    2023: {'Male': 0.459, 'Female': 0.541},
    2024: {'Male': 0.459, 'Female': 0.541}
}

# Age distribution by year
age_distribution_by_year = {
    2019: {16: 0.042, 17: 0.042, 18: 0.042, range(19, 25): 0.086, range(25, 65): 0.632, range(65, 81): 0.161},
    2020: {16: 0.042, 17: 0.042, 18: 0.042, range(19, 25): 0.071, range(25, 65): 0.660, range(65, 81): 0.143},
    2021: {16: 0.042, 17: 0.042, 18: 0.042, range(19, 25): 0.056, range(25, 65): 0.688, range(65, 81): 0.217},
    2022: {16: 0.042, 17: 0.042, 18: 0.042, range(19, 25): 0.056, range(25, 65): 0.688, range(65, 81): 0.217},
    2023: {16: 0.042, 17: 0.042, 18: 0.042, range(19, 25): 0.056, range(25, 65): 0.688, range(65, 81): 0.217},
    2024: {16: 0.042, 17: 0.042, 18: 0.042, range(19, 25): 0.056, range(25, 65): 0.688, range(65, 81): 0.217}
}

# Custom provider to ensure name matches sex
class CustomProvider:
    @staticmethod
    def name(sex):
        if sex == 'Male':
            return fake.name_male()
        else:
            return fake.name_female()

# Function to generate realistic blood types based on ethnicity
def generate_blood_type(ethnicity):
    blood_type_probs = blood_type_distribution_by_ethnicity[ethnicity]
    blood_type = random.choices(
        population=list(blood_type_probs.keys()),
        weights=list(blood_type_probs.values()),
        k=1
    )[0]
    if blood_type == 'O':
        return random.choice(['O positive', 'O negative'])
    elif blood_type == 'A':
        return random.choice(['A positive', 'A negative'])
    elif blood_type == 'B':
        return random.choice(['B positive', 'B negative'])
    elif blood_type == 'AB':
        return random.choice(['AB positive', 'AB negative'])

# Factory for creating a donor
class DonorFactory(factory.Factory):
    class Meta:
        model = dict

    donor_id = factory.Sequence(lambda n: n + 1)
    year = factory.LazyAttribute(lambda x: random.choice([2019, 2020, 2021, 2022, 2023, 2024]))
    sex = factory.LazyAttribute(lambda x: random.choices(
        population=list(gender_distribution_by_year[x.year].keys()),
        weights=list(gender_distribution_by_year[x.year].values())
    )[0])
    name = factory.LazyAttribute(lambda x: CustomProvider.name(x.sex))
    ethnicity = factory.LazyAttribute(lambda x: random.choices(
        population=list(ethnicity_distribution_by_year[x.year].keys()),
        weights=list(ethnicity_distribution_by_year[x.year].values())
    )[0])
    age = factory.LazyAttribute(lambda x: random.choices(
        population=[age if isinstance(age, int) else random.choice(list(age)) for age in age_distribution_by_year[x.year].keys()],
        weights=list(age_distribution_by_year[x.year].values())
    )[0])
    birthdate = factory.LazyAttribute(lambda x: datetime.today().replace(year=datetime.today().year - x.age).date())
    blood_type = factory.LazyAttribute(lambda x: generate_blood_type(x.ethnicity))
    first_time_donor = factory.LazyAttribute(lambda x: random.random() < 0.23)
    number_of_donations = factory.LazyAttribute(lambda x: int(round(random.normalvariate(1.8, 0.5))) if not x.first_time_donor else 1)
    last_donation_date = factory.LazyAttribute(lambda x: fake.date_between(start_date=f'-{x.age}y', end_date='today'))

# Function to generate donation dates
def generate_donation_dates(start_date, num_donations):
    donation_dates = [start_date]
    current_date = datetime.combine(start_date, datetime.min.time())
    for _ in range(num_donations - 1):
        current_date += timedelta(days=random.randint(112, 365))
        if current_date.date() > datetime.today().date():
            break
        donation_dates.append(current_date.date())
    return donation_dates

# Generate the data
donors = []
for _ in range(1000):  # Adjust the number of donors as needed
    donor = DonorFactory()
    donation_dates = generate_donation_dates(donor['last_donation_date'], donor['number_of_donations'])
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
            'donation_date': date.strftime('%Y-%m-%d')
        })

# Display a sample of the generated data
for donor in donors[:10]:
    print(donor)

