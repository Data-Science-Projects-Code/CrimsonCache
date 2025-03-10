-- Enable foreign key support
PRAGMA foreign_keys = ON;

CREATE TABLE locations (
    location_id UUID PRIMARY KEY,
    name TEXT,
    address TEXT,
    town TEXT,
    blood_bank BOOLEAN
);

CREATE TABLE employees (
    employee_id UUID PRIMARY KEY,
    name TEXT,
    location_id UUID,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE donors (
    donor_id UUID PRIMARY KEY,
    unique_id TEXT,
    name TEXT,
    birthdate DATE,
    age INTEGER,
    sex TEXT,
    ethnicity TEXT,
    blood_type TEXT
);

CREATE TABLE donation_events (
    event_id UUID PRIMARY KEY,
    location_id UUID,
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    units_collected INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE event_employees (
    event_id UUID,
    employee_id UUID,
    PRIMARY KEY (event_id, employee_id),
    FOREIGN KEY (event_id) REFERENCES donation_events(event_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE hospitals (
    hospital_id UUID PRIMARY KEY,
    location_id UUID,
    physician TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE patients (
    patient_id UUID PRIMARY KEY,
    admission_date DATE,
    bag_id TEXT
);

CREATE TABLE blood_requests (
    request_id UUID PRIMARY KEY,
    hospital_id UUID,
    request_datetime TIMESTAMP,
    units_requested INTEGER,
    blood_type TEXT,
    status TEXT,
    patient_id UUID,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE donations (
    bag_id TEXT PRIMARY KEY,  -- Blood type + UUID
    donor_id UUID,
    event_id UUID,
    test_date DATE,
    test_result BOOLEAN,
    status TEXT,  -- available, reserved, discarded
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id),
    FOREIGN KEY (event_id) REFERENCES donation_events(event_id)
);

CREATE TABLE distribution (
    distribution_id UUID PRIMARY KEY,
    bag_id TEXT,
    hospital_id UUID,
    distribution_date TIMESTAMP,
    request_id UUID,
    FOREIGN KEY (bag_id) REFERENCES donations(bag_id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
    FOREIGN KEY (request_id) REFERENCES blood_requests(request_id)
);

-- Additional indices for performance
CREATE INDEX idx_donations_status ON donations(status);
CREATE INDEX idx_blood_requests_datetime ON blood_requests(request_datetime);
CREATE INDEX idx_blood_requests_status ON blood_requests(status);
CREATE INDEX idx_donation_events_datetime ON donation_events(start_datetime);
