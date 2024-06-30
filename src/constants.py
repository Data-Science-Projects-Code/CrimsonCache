# Define age distribution for 2024
age_distribution_2024 = [
    (17, 0.009),
    (18, 0.018),
    (19, 0.015),
    (range(20, 25), 0.056),
    (range(25, 65), 0.688),
    (range(65, 81), 0.217),
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
