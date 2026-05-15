CREATE TABLE IF NOT EXISTS voters (
    voter_id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    address TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    ssn_last4 VARCHAR(4) NOT NULL,
    eligibility_verified BOOLEAN DEFAULT TRUE
);

/* some AI generated entry samples */ 

INSERT INTO voters (
    full_name,
    address,
    date_of_birth,
    ssn_last4
)
VALUES
(
    'Alice Johnson',
    '123 Main Street',
    '1995-04-12',
    '1111'
),
(
    'Bob Smith',
    '456 Oak Avenue',
    '1988-09-23',
    '2222'
),
(
    'Charlie Brown',
    '789 Pine Road',
    '1977-01-15',
    '3333'
);