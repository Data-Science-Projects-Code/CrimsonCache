import factory
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Define age distribution
age_distribution = [
    (16, 0.009),
    (17, 0.018),
    (18, 0.015),
    (range(19, 25), 0.056),
    (range(25, 65), 0.688),
    (range(65, 81), 0.217),
]

# Define blood type distribution
blood_type_distribution = [
    ('O positive', 0.38),
    ('A positive', 0.34),
    ('B positive', 0.09),
    ('O negative', 0.07),
    ('A negative', 0.06),
    ('AB positive', 0.03),
    ('B negative', 0.02),
    ('AB negative', 0.01),
]

# Define sex distribution
sex_distribution = [
    ('Male', 0.646),
    ('Female', 0.354),
]

# Define race distribution
race_distribution = [
    ('White', 0.78),
    ('Black', 0.16),
    ('Other', 0.06),
]

# Custom provider to ensure name matches sex
class CustomProvider:
    @staticmethod
    def name(sex):
        if sex == 'Male':
            return fake.name_male()
        else:
            return fake.name_female()

# Factory for creating a donor
class DonorFactory(factory.Factory):
    class Meta:
        model = dict

    donor_id = factory.Sequence(lambda n: n + 1)
    sex = factory.LazyAttribute(lambda x: random.choices(
        [sex for sex, _ in sex_distribution],
        [prob for _, prob in sex_distribution]
    )[0])
    name = factory.LazyAttribute(lambda x: CustomProvider.name(x.sex))
    age = factory.LazyAttribute(lambda x: random.choices(
        [age if isinstance(age, int) else random.choice(list(age)) for age, _ in age_distribution],
        [prob for _, prob in age_distribution]
    )[0])
    race = factory.LazyAttribute(lambda x: random.choices(
        [race for race, _ in race_distribution],
        [prob for _, prob in race_distribution]
    )[0])
    blood_type = factory.LazyAttribute(lambda x: random.choices(
        [blood_type for blood_type, _ in blood_type_distribution],
        [prob for _, prob in blood_type_distribution]
    )[0])
    first_time_donor = factory.LazyAttribute(lambda x: random.random() < 0.23)
    number_of_donations = factory.LazyAttribute(lambda x: random.randint(1, 10) if not x.first_time_donor else 1)
    last_donation_date = factory.LazyAttribute(lambda x: fake.date_between(start_date='-10y', end_date='today'))

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
    for date in donation_dates:
        donors.append({
            'donor_id': donor['donor_id'],
            'name': donor['name'],
            'age': donor['age'],
            'sex': donor['sex'],
            'race': donor['race'],
            'blood_type': donor['blood_type'],
            'first_time_donor': donor['first_time_donor'],
            'donation_date': date.strftime('%Y-%m-%d')
        })

# Display a sample of the generated data
for donor in donors[:50]:
    print(donor)

