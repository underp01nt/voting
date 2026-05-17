import psycopg2

ELECTION_AUTHORITY_DB_CREDENTIALS = {
    "host": "election_authority_db",
    "database": "election_authority",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

VOTES_DB_CREDENTIALS = {}

''' raw connection for scripts + tests '''
def get_election_authority_connection():
    return psycopg2.connect(**ELECTION_AUTHORITY_DB_CREDENTIALS)

def get_votes_connection():
    raise NotImplementedError()


''' FastAPI dependencies for Depends() '''
def get_election_authority_db():
    conn = psycopg2.connect(**ELECTION_AUTHORITY_DB_CREDENTIALS)
    try: yield conn
    finally: conn.close()

def get_votes_db():
    raise NotImplementedError()
