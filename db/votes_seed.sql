CREATE TABLE ballots (
    id BIGSERIAL PRIMARY KEY,

    hashed_signature TEXT NOT NULL UNIQUE,
    encrypted_ballot TEXT,   /* nullable until voter makes a submission */
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    election_id TEXT,
    round INTEGER,

    UNIQUE(hashed_signature, election_id, round)
);

CREATE TABLE elections (
    id VARCHAR(32) PRIMARY KEY NOT NULL UNIQUE,
    name VARCHAR(32),
    target_size INTEGER,
    valid BOOLEAN NOT NULL,
    round INTEGER,

    UNIQUE(id, valid)
);

CREATE TABLE candidates (
    id VARCHAR(18) PRIMARY KEY NOT NULL UNIQUE,
    full_name VARCHAR(40) NOT NULL UNIQUE, 
    election_id VARCHAR(32) NOT NULL, 
    round_eliminated INTEGER,

    UNIQUE(id, full_name)
);