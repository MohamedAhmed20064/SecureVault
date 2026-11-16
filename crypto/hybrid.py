"""Hybrid encryption (how HTTPS/PGP work): AES-256-GCM encrypts the data, RSA-OAEP encrypts the AES key."""
import base64, json, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .rsa_utils import _OAEP

_b = lambda x: base64.b64encode(x).decode()
_d = lambda s: base64.b64decode(s)

def hybrid_encrypt(text, pub):
    key, nonce = AESGCM.generate_key(256), os.urandom(12)          # 1. fresh random session key
    ct = AESGCM(key).encrypt(nonce, text.encode(), None)            # 2. AES encrypts the (any-length) message
    wrapped = pub.encrypt(key, _OAEP)                               # 3. RSA encrypts only the 32-byte key
    return _b(json.dumps({"k": _b(wrapped), "n": _b(nonce), "c": _b(ct)}).encode())

def hybrid_decrypt(token, priv):
    try:
        p = json.loads(_d(token.strip()))
        key = priv.decrypt(_d(p["k"]), _OAEP)
        return AESGCM(key).decrypt(_d(p["n"]), _d(p["c"]), None).decode()
    except Exception as e:
        raise ValueError("Hybrid decryption failed: wrong key or modified data") from e
