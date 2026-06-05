""" UTILITY/HELPER METHODS """

import hashlib, secrets

# hashed in byte form
def hash(msg: str): return hashlib.sha256(msg.encode()).digest()

 # returns digest in hex form
def hash_hex(msg: str) -> str: return hashlib.sha256(msg.encode()).hexdigest()

# hashes token, then converts to int 
def to_hashed_int(msg: str) -> int: return int.from_bytes(hash(msg), "big")

# generates a random hex string of n characters
def generate_id(n: int): return secrets.token_hex(n)
