from db.factory import get_election_authority_connection

# returns status indicating token registration eligibility
def verify_voter(name: str, address: str, dob: str, ssn4: str, db) -> str:
    cursor = db.cursor()
    cursor.execute(
        """
            SELECT eligibility_verified 
            FROM voters
            WHERE name = %s AND address = %s AND dob = %s AND ssn4 = %s
        """, 
        (name, address, dob, ssn4)
    )

    row = cursor.fetchone()

    #  0: no records founds,  1: eligible,  2: not eligible
    if row is None: return "no records found"

    if not row[0]:
        # TODO: flip eligibility_verified
        return "token generation ability granted"
    
    else: return "eligibility already used"

if __name__ == "__main__":
    db = get_election_authority_connection()
    assert verify_voter('Alice Johnson', '123 Main Street', '1995-04-12', '1111', db) == 1
    assert verify_voter('Alice', '123 Main Street', '1995-04-12', '1111', db) == 0
