"""File encryption: AES-256-GCM on any file (PDF, image, ...). Output format: MAGIC | salt | nonce | ciphertext+tag."""
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .aes import _derive

MAGIC = b"SVLT1"

def encrypt_file(src, dst, password):
    if not password: raise ValueError("Password is required")
    with open(src, "rb") as f: data = f.read()
    salt, nonce = os.urandom(16), os.urandom(12)
    ct = AESGCM(_derive(password, salt)).encrypt(nonce, data, MAGIC)
    with open(dst, "wb") as f: f.write(MAGIC + salt + nonce + ct)

def decrypt_file(src, dst, password):
    with open(src, "rb") as f: raw = f.read()
    if not raw.startswith(MAGIC): raise ValueError("Not a SecureVault encrypted file")
    salt, nonce, ct = raw[5:21], raw[21:33], raw[33:]
    try: data = AESGCM(_derive(password, salt)).decrypt(nonce, ct, MAGIC)
    except InvalidTag as e: raise ValueError("Decryption failed: wrong password or file was modified") from e
    with open(dst, "wb") as f: f.write(data)
