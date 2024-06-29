import factory
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Define age distribution for 2024
age_distribution_2024 = [
    (17, 0.009),
    (18, 0.018),
    (19, 0.015),
    (range(20, 25), 0.056),
    (range(25, 65), 0.688),
    (range(65, 81), 0.217),
]

# Define blood type distribution
blood_type_distribution = [
    ('O positive', 0.39),
    ('A positive', 0.30),
    ('B positive', 0.09),
    ('O negative', 0.07),
    ('A negative', 0.06),
    ('AB positive', 0.04),
    ('B negative', 0.02),
    ('AB negative', 0.01),
]

# Define sex distribution for 2024
sex_distribution_2024 = [
    ('Male', 0.459),
    ('Female', 0.541),
]

# Define ethnicity distribution
ethnicity_distribution = [
    ('White', 0.878),
    ('Hispanic', 0.058),
    ('Black', 0.027),
    ('Asian', 0.03),
    ('Native American', 0.005),
    ('Native Hawaiian or Pacific Islander', 0.002),
]

# Define blood type distribution by ethnicity
blood_type_by_ethnicity = {
    'White': [('O positive', 0.37), ('O negative', 0.08), 
              ('A positive', 0.33), ('A negative', 0.07),
              ('B positive', 0.09), ('B negative', 0.02), 
              ('AB positive', 0.03),('AB negative', 0.01)],
    
    'Hispanic':[('O positive', 0.53), ('O negative', 0.04), 
              ('A positive', 0.29), ('A negative', 0.02),
              ('B positive', 0.09), ('B negative', 0.01), 
              ('AB positive', 0.02),('AB negative', 0.01)],
    
    'Black':[('O positive', 0.46), ('O negative', 0.04), 
              ('A positive', 0.24), ('A negative', 0.02),
              ('B positive', 0.18), ('B negative', 0.01), 
              ('AB positive', 0.04),('AB negative', 0.01)] ,
    
    'Asian':[('O positive', 0.39), ('O negative', 0.01), 
              ('A positive', 0.27), ('A negative', 0.005),
              ('B positive', 0.25), ('B negative', 0.004), 
              ('AB positive', 0.07),('AB negative', 0.001)] ,

    'Native American':[('O positive', 0.5), ('O negative', 0.046), 
              ('A positive', 0.314), ('A negative', 0.03),
              ('B positive', 0.074), ('B negative', 0.006), 
              ('AB positive', 0.028),('AB negative', 0.002)] ,

    'Native Hawaiian or Pacific Islander':[('O positive', 0.388), ('O negative', 0.03), 
              ('A positive', 0.32), ('A negative', 0.03),
              ('B positive', 0.16), ('B negative', 0.008), 
              ('AB positive', 0.06),('AB negative', 0.004)] ,
}

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
    first_time_donor = factory.LazyAttribute(lambda x: random.random() < 0.12)
    number_of_donations = factory.LazyAttribute(lambda x: 1 if x.first_time_donor else random.randint(1, 10))
    last_donation_date = factory.LazyAttribute(lambda x: fake.date_between(start_date='-10y', end_date='today'))

# Function to generate donation dates ensuring they are at least 112 days apart and within a valid age range
def generate_donation_dates(start_date, num_donations, birthdate):
    donation_dates = []
    current_date = datetime.combine(start_date, datetime.min.time())
    min_date = datetime.combine(birthdate.replace(year=birthdate.year + 17), datetime.min.time())
    while len(donation_dates) < num_donations:
        if current_date < min_date:
            break
        donation_dates.append(current_date.date())
        current_date -= timedelta(days=random.randint(112, 365))
        # Randomly skip some years
        if random.random() < 0.3:
            current_date -= timedelta(days=365 * random.randint(1, 3))
    return donation_dates

# Generate the data
donors = []
for _ in range(1000):  # Adjust the number of donors as needed
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
            'donation_date': date.strftime('%Y-%m-%d')
        })

# Display a sample of the generated data
for donor in donors[:7000]:
    print(donor)

import csv

# Specify the filename
filename = '../data/donors.csv'

# Define the header
header = ['donor_id', 'name', 'birthdate', 'age_at_donation', 'sex', 'ethnicity', 'blood_type', 'first_time_donor', 'donation_date']

# Write the data to a CSV file
with open(filename, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    for donor in donors:
        writer.writerow(donor)

print(f"Data has been written to {filename}")

