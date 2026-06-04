CREATE TABLE voters (
    hashed_signature TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE elections (
    id VARCHAR(32) PRIMARY KEY NOT NULL,
    name VARCHAR(40) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    target_sizes INTEGER[] NOT NULL,
    valid BOOLEAN NOT NULL,
    round INTEGER
);

CREATE TABLE ballots (
    id VARCHAR(18) PRIMARY KEY NOT NULL UNIQUE,

    hashed_signature TEXT NOT NULL,
    encrypted_ballot TEXT,   /* nullable until voter makes a submission */
    last_updated TIMESTAMPTZ,
    election_id TEXT REFERENCES elections(id),
    round INTEGER,

    UNIQUE(hashed_signature, election_id)
);

CREATE TABLE candidates (
    id VARCHAR(18) PRIMARY KEY NOT NULL,
    name VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE election_candidates (
    election_id VARCHAR(32) NOT NULL REFERENCES elections(id),
    candidate_id VARCHAR(18) NOT NULL REFERENCES candidates(id),
    round_eliminated INTEGER,

    PRIMARY KEY (election_id, candidate_id)
);
