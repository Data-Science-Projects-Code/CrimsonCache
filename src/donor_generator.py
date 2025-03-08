import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
import factory
from constants import (
    AGE_DISTRIBUTION_2024,
    SEX_DISTRIBUTION_2024,
    ETHNICITY_DISTRIBUTION,
    BLOOD_TYPE_BY_ETHNICITY,
)

fake = Faker()


class DonorFactory(factory.Factory):
    class Meta:
        model = dict

    donor_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    unique_id = factory.LazyFunction(lambda: f"DON-{str(uuid.uuid4())[:8]}")
    name = factory.LazyFunction(fake.name)

    age = factory.LazyAttribute(lambda _: DonorFactory._generate_age())
    birthdate = factory.LazyAttribute(
        lambda obj: (datetime.now() - timedelta(days=obj.age * 365)).strftime(
            "%Y-%m-%d"
        )
    )

    sex = factory.LazyAttribute(lambda _: DonorFactory._generate_sex())
    ethnicity = factory.LazyAttribute(lambda _: DonorFactory._generate_ethnicity())
    blood_type = factory.LazyAttribute(
        lambda obj: DonorFactory._generate_blood_type(obj.ethnicity)
    )

    first_donation_date = factory.LazyAttribute(
        lambda obj: DonorFactory._generate_donation_dates(obj.birthdate, obj.age)[0]
    )
    last_donation_date = factory.LazyAttribute(
        lambda obj: DonorFactory._generate_donation_dates(obj.birthdate, obj.age)[1]
    )
    total_donations = factory.LazyAttribute(
        lambda obj: DonorFactory._generate_donation_dates(obj.birthdate, obj.age)[2]
    )

    @staticmethod
    def _generate_age():
        age_rand = random.random()
        cumulative_prob = 0
        for age, prob in AGE_DISTRIBUTION_2024:
            cumulative_prob += prob
            if age_rand <= cumulative_prob:
                return (
                    random.randint(age.start, age.stop - 1)
                    if isinstance(age, range)
                    else age
                )
        return 17

    @staticmethod
    def _generate_sex():
        return "Male" if random.random() <= SEX_DISTRIBUTION_2024[0][1] else "Female"

    @staticmethod
    def _generate_ethnicity():
        ethnicity_rand = random.random()
        cumulative_prob = 0
        for eth, prob in ETHNICITY_DISTRIBUTION:
            cumulative_prob += prob
            if ethnicity_rand <= cumulative_prob:
                return eth
        return ETHNICITY_DISTRIBUTION[0][0]

    @staticmethod
    def _generate_blood_type(ethnicity):
        blood_type_dist = BLOOD_TYPE_BY_ETHNICITY[ethnicity]
        blood_type_rand = random.random()
        cumulative_prob = 0
        for bt, prob in blood_type_dist:
            cumulative_prob += prob
            if blood_type_rand <= cumulative_prob:
                return bt
        return blood_type_dist[0][0]

    @staticmethod
    def _generate_donation_dates(birthdate_str, age):
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
        today = datetime.now()

        # Earliest possible donation date (17th birthday)
        first_possible_date = birthdate + timedelta(days=17 * 365)
        if first_possible_date > today:
            return birthdate_str, birthdate_str, 0

        # Random first donation date after 17th birthday
        days_since_first_possible = (today - first_possible_date).days
        first_donation_date = first_possible_date + timedelta(
            days=random.randint(0, days_since_first_possible)
        )

        # Calculate max possible donations based on 56-day intervals
        max_donations = (today - first_donation_date).days // 56
        max_donations = min(max_donations, 102)  # Capping at 102 donations

        if max_donations == 0:
            return (
                first_donation_date.strftime("%Y-%m-%d"),
                first_donation_date.strftime("%Y-%m-%d"),
                1,
            )

        total_donations = random.randint(1, max_donations)
        last_donation_date = first_donation_date + timedelta(
            days=56 * (total_donations - 1)
        )

        return (
            first_donation_date.strftime("%Y-%m-%d"),
            last_donation_date.strftime("%Y-%m-%d"),
            total_donations,
        )
