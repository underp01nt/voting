import psycopg2

DB_CREDENTIALS = {
    "host": "election_authority_db",
    "database": "election_authority",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

def get_connection():
    return psycopg2.connect(**DB_CREDENTIALS)