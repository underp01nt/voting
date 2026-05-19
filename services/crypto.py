from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import hashlib, os

public_exponent, key_size = 65537, 2048
private_key = rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)

def save_keys():
    # save private key
    private_key_file_path = "sample_keys/private.pem"
    directory = os.path.dirname(private_key_file_path)
    os.makedirs(directory, exist_ok=True)

    with open(private_key_file_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # save public key
    public_key = private_key.public_key()
    public_key_file_path = "sample_keys/public.pem"
    os.makedirs(directory, exist_ok=True)

    with open(public_key_file_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def load_private_key():
    with open("sample_keys/private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key():
    with open("sample_keys/public.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())
    
##############################################################################################

def initialize_keys():
    private_key = load_private_key()
    public_key = load_public_key()

    private_numbers = private_key.private_numbers()
    public_numbers = public_key.public_numbers()

    # public key components
    n = public_numbers.n    # modulus 
    e = public_numbers.e    # exponent

    # private key exponent
    d = private_numbers.d   

    return n, e, d

n, e, d = initialize_keys()

""" HELPER METHODS """

def hash_token(token: str):             # hashed in byte form
    return hashlib.sha256(token.encode()).digest()

def hash_token_hex(token: str) -> str:  # hashed in string form
    return hashlib.sha256(token.encode()).hexdigest()

# hashes token, then converts to int 
def _to_hashed_int(token: str) -> int:
    h = hash_token(token)
    return int.from_bytes(h, "big") % n


""" SIGNING + VERIFICATION METHODS """

# signs voter's blinded(SHA256(token))
def sign_blinded_token(blinded_token: str) -> str:
    blinded_int = int(blinded_token)
    blinded_signature = pow(blinded_int, d, n)

    return str(blinded_signature)

# use public key (e, n) to verify voter's signature 
def verify_signature(token: str, signature: str):
    token_int = _to_hashed_int(token)   # voter hashed the token before blinding, so maintain that consistency
    signature_int = int(signature)

    return pow(signature_int, e, n) == token_int


# if __name__ == "__main__":
#     print(n)
#     print(e)
#     print(d)