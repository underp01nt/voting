from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from services import crypto
import json

def test_generate_key():
    key = crypto.generate_aes_key()
    assert isinstance(key, AESGCM)

def test_aes_encrypt_decrypt():
    key = crypto.generate_aes_key()
    payload = json.dumps({"candidate_ids": ["ad123", "wesdsd23"]})
    
    cipher = crypto.aes_encrypt(key, payload)
    plain = crypto.aes_decrypt(key, cipher)

    assert payload == plain

    

