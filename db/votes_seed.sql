CREATE TABLE voters (
    hashed_signature TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ballots (
    id BIGSERIAL PRIMARY KEY NOT NULL UNIQUE,

    hashed_signature TEXT NOT NULL UNIQUE,
    encrypted_ballot TEXT,   /* nullable until voter makes a submission */

    /*  add last modified field?  */

    election_id TEXT,
    round INTEGER,

    UNIQUE(hashed_signature, election_id)
);

CREATE TABLE elections (
    id VARCHAR(32) PRIMARY KEY NOT NULL UNIQUE,
    name VARCHAR(32) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
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

    UNIQUE(id, election_id)
);