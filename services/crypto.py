from cryptography.hazmat.primitives.asymmetric import rsa
import hashlib

public_exponent, key_size = 65537, 2048

# generate RSA keypair
private_key = rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)
public_key = private_key.public_key()

private_numbers = private_key.private_numbers()
public_numbers = public_key.public_numbers()

n = public_numbers.n
e = public_numbers.e
d = private_numbers.d

##############################################################################################

def sign_blinded_token(blinded_token: str) -> str:
    blinded_int = int(blinded_token)
    blinded_signature = pow(blinded_int, d, n)

    return str(blinded_signature)

def hash_blinded_token(blinded_token: str) -> str:
    return hashlib.sha256(blinded_token.encode()).hexdigest()
