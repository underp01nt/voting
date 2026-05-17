CREATE TABLE IF NOT EXISTS voters (
    voter_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    dob DATE NOT NULL,
    ssn4 VARCHAR(4) NOT NULL,
    eligibility_used BOOLEAN DEFAULT FALSE 
);

/* some AI generated entry samples */ 
INSERT INTO voters (
    name,
    address,
    dob,
    ssn4
)  
   /*      name             address             dob        ssn4      */
VALUES ('Alice Johnson', '123 Main Street', '1995-04-12', '1111'),
       ('Bob Smith', '456 Oak Avenue', '1988-09-23', '2222'),
       ('Charlie Brown', '789 Pine Road', '1977-01-15', '3333'),
       ('123', '123', '2026-05-15', '0000');