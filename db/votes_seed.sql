CREATE TABLE voters (
    hashed_signature TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ballots (
    id BIGSERIAL PRIMARY KEY,

    hashed_signature TEXT NOT NULL UNIQUE,
    encrypted_ballot TEXT,   /* nullable until voter makes a submission */
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    election_id TEXT,
    round INTEGER,

    UNIQUE(hashed_signature, election_id)
);

CREATE TABLE elections (
    id VARCHAR(32) PRIMARY KEY NOT NULL UNIQUE,
    name VARCHAR(32) NOT NULL UNIQUE,
    target_size INTEGER NOT NULL,
    valid BOOLEAN NOT NULL,
    round INTEGER,

    UNIQUE(id, valid)
);

CREATE TABLE candidates (
    id VARCHAR(18) PRIMARY KEY NOT NULL UNIQUE,
    name VARCHAR(40) NOT NULL UNIQUE, 
    election_id VARCHAR(32), 
    round_eliminated INTEGER,

    UNIQUE(id, name)
);