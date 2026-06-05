from fastapi import Request

# check eligibility status for token registration 
def verify_voter(request: Request, db, name: str, address: str, dob: str, ssn4: str):
    cursor = db.cursor()
    cursor.execute(
        """
            SELECT eligibility_used
            FROM voters
            WHERE name = %s AND address = %s AND dob = %s AND ssn4 = %s
        """, 
        (name, address, dob, ssn4)
    )

    row = cursor.fetchone()

    if row is None: return "no records found"

    if not row[0]:
        cursor.execute(
            """
                UPDATE voters
                SET eligibility_used = TRUE
                WHERE name = %s AND address = %s AND dob = %s AND ssn4 = %s
            """, 
            (name, address, dob, ssn4)
        )
        
        db.commit()

        request.session["allowed_token"] = True
        return "valid eligibility"
    
    else: return "eligibility already used"

def is_blinded_token_hash_unique(db, blinded_token_hash: str):
    cursor = db.cursor()
    cursor.execute(
        """
            SELECT hashed_token
            FROM ballots
            WHERE hashed_token = %s
        """,
        (blinded_token_hash,)
    )

    row = cursor.fetchone()
    return row is None

# if __name__ == "__main__":
    # db = get_election_authority_connection()
    # assert verify_voter('Alice Johnson', '123 Main Street', '1995-04-12', '1111', db) == 1
    # assert verify_voter('Alice', '123 Main Street', '1995-04-12', '1111', db) == 0
