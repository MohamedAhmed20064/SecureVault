"""AES-256-GCM with a PBKDF2 key derived from a password."""
import base64, os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def _derive(password, salt):
    return PBKDF2HMAC(hashes.SHA256(), 32, salt, 200_000).derive(password.encode())

def aes_encrypt(plaintext, password):
    if not password: raise ValueError("Password is required")
    salt, nonce = os.urandom(16), os.urandom(12)
    ct = AESGCM(_derive(password, salt)).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(salt + nonce + ct).decode()

def aes_decrypt(token, password):
    try:
        raw = base64.b64decode(token.strip())
        salt, nonce, ct = raw[:16], raw[16:28], raw[28:]
        return AESGCM(_derive(password, salt)).decrypt(nonce, ct, None).decode()
    except (InvalidTag, ValueError) as e:
        raise ValueError("Decryption failed: wrong password or modified data") from e
