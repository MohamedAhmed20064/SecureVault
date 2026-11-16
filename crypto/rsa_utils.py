"""RSA-2048: key generation, OAEP encryption, PSS digital signatures."""
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

def rsa_generate(bits=2048):
    priv = rsa.generate_private_key(65537, bits)
    return priv, priv.public_key()

def rsa_export(priv, pub):
    p = priv.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    q = pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return p, q

_OAEP = padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None)
def rsa_encrypt(text, pub):
    data = text.encode()
    if len(data) > 190: raise ValueError("RSA-2048 handles at most 190 bytes; use AES for longer data")
    return base64.b64encode(pub.encrypt(data, _OAEP)).decode()
def rsa_decrypt(token, priv):
    try: return priv.decrypt(base64.b64decode(token.strip()), _OAEP).decode()
    except Exception as e: raise ValueError("RSA decryption failed: wrong key or modified data") from e

_PSS = padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH)
def sign(message, priv):
    return base64.b64encode(priv.sign(message.encode(), _PSS, hashes.SHA256())).decode()
def verify(message, signature, pub):
    try:
        pub.verify(base64.b64decode(signature.strip()), message.encode(), _PSS, hashes.SHA256()); return True
    except (InvalidSignature, ValueError): return False
