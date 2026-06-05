from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from services.utils import to_hashed_int
import os, base64

# setup RSA constants
public_exponent, key_size = 65537, 2048
private_key = rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)

# file paths
AES_KEY_PATH = "sample_keys/aes.key"
RSA_PUBLIC_KEY_PATH = "sample_keys/public.pem"
RSA_PRIVATE_KEY_PATH = "sample_keys/private.pem"

# aes encryption constants
BIT_LENGTH = 256   # prefer AES-256

def save_keys():
    # save private key
    private_key_file_path = RSA_PRIVATE_KEY_PATH
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
    public_key_file_path = RSA_PUBLIC_KEY_PATH
    os.makedirs(directory, exist_ok=True)

    with open(public_key_file_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def load_private_key() -> rsa.RSAPrivateKey:
    with open(RSA_PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise TypeError("RSA private key expected")
        
        return private_key

def load_public_key() -> rsa.RSAPublicKey:
    with open(RSA_PUBLIC_KEY_PATH, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise TypeError("RSA public key expected")
        
        return public_key
    
"""   SYMMETRIC ENCRYPTION (FOR BALLOT PAYLOADS)   """
# https://www.qpython.com/python-how-to-encrypt-and-decrypt-with-aes-4h1k/

def generate_aes_key(file_path=None) -> AESGCM:
    key = AESGCM.generate_key(bit_length=BIT_LENGTH)
    aesgcm = AESGCM(key)
    if file_path:
        with open(file_path, "wb") as f:  # save as .key
            f.write(key)
    return aesgcm

def aes_encrypt(key: AESGCM, payload: str) -> str:
    nonce = os.urandom(12)   # random 12-bit string, prepend as first 12 bytes before base64 
    ciphertext = key.encrypt(nonce, payload.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode()

def aes_decrypt(key: AESGCM, data: str) -> str:
    raw_data = base64.b64decode(data)
    nonce = raw_data[:12]; ciphertext = raw_data[12:]
    plaintext = key.decrypt(nonce, ciphertext, None)

    return plaintext.decode()

with open(AES_KEY_PATH, "rb") as f: aesgcm = AESGCM(f.read())

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

""" SIGNING + VERIFICATION METHODS """

# signs voter's blinded(SHA256(token))
def sign_blinded_token(blinded_token: str) -> str:
    blinded_int = int(blinded_token)
    blinded_signature = pow(blinded_int, d, n)   

    return str(blinded_signature)   # blinded signature: (M')^d (mod n)

# use public key (e, n) to verify voter's signature 
def verify_signature(token: str, signature: str):
    token_int = to_hashed_int(token)   # voter hashed the token before blinding, so maintain that consistency
    signature_int = int(signature)

    return pow(signature_int, e, n) == token_int % n   # verification: s^e (mod n) ≡ h (mod n) 