CREATE TABLE ballots (
    id BIGSERIAL PRIMARY KEY,

    hashed_token TEXT NOT NULL UNIQUE,
    encrypted_ballot TEXT,   /* nullable until voter makes a submission */
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);