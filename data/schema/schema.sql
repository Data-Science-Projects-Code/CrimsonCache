PRAGMA foreign_keys = ON;


CREATE TABLE employees (
    employee_id UUID PRIMARY KEY,
    name TEXT,
    hire_date DATE
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

-- this doesn't have anything for a location. Not sure I need that.
CREATE TABLE donation_events (
    event_id UUID PRIMARY KEY,
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    total_units INTEGER,
    a_pos INTEGER,
    a_neg INTEGER,
    b_pos INTEGER,
    b_neg INTEGER,
    o_pos INTEGER,
    o_neg INTEGER,
    ab_pos INTEGER,
    ab_neg INTEGER
);

CREATE TABLE event_employees (
    event_id UUID,
    employee_id UUID,
    PRIMARY KEY (event_id, employee_id),
    FOREIGN KEY (event_id) REFERENCES donation_events(event_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE hospitals (
    NPI INTEGER PRIMARY KEY,
    address TEXT,
    tel INTEGER,
    POC TEXT
);

CREATE TABLE patients (
    patient_id UUID PRIMARY KEY,
    admission_date DATE,
    blood_type TEXT,
    bag_id TEXT
);

CREATE TABLE blood_requests (
    request_id UUID PRIMARY KEY,
    NPI INTEGER,
    request_datetime TIMESTAMP,
    units_requested INTEGER,
    blood_type TEXT,
    status TEXT,
    patient_id UUID,
    FOREIGN KEY (NPI) REFERENCES hospitals(NPI),
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
    NPI INTEGER,
    distribution_date TIMESTAMP,
    request_id UUID,
    FOREIGN KEY (bag_id) REFERENCES donations(bag_id),
    FOREIGN KEY (NPI) REFERENCES hospitals(NPI),
    FOREIGN KEY (request_id) REFERENCES blood_requests(request_id)
);

-- Additional indices for performance
CREATE INDEX idx_donations_status ON donations(status);
CREATE INDEX idx_blood_requests_datetime ON blood_requests(request_datetime);
CREATE INDEX idx_blood_requests_status ON blood_requests(status);
CREATE INDEX idx_donation_events_datetime ON donation_events(start_datetime);
