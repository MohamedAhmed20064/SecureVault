"""Performance measurements used by the Performance screen and the report."""
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .classical import caesar, vigenere
from .hashing import sha256
from .rsa_utils import rsa_generate, sign, verify

def _ms(fn, repeat):
    best = float("inf")
    for _ in range(repeat):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best * 1000

def run(sizes=(1024, 102_400, 1_048_576)):
    """Milliseconds per algorithm for each input size in bytes (AES timing excludes the password KDF)."""
    key, nonce, out = AESGCM.generate_key(256), bytes(12), {}
    for n in sizes:
        text = "".join(chr(97 + i % 26) for i in range(n)); data = text.encode(); rep = 1 if n >= 500_000 else 3
        out[n] = {"Caesar": _ms(lambda: caesar(text, 3), rep), "Vigenère": _ms(lambda: vigenere(text, "key"), rep),
                  "AES-256-GCM": _ms(lambda: AESGCM(key).encrypt(nonce, data, None), rep), "SHA-256": _ms(lambda: sha256(data), rep)}
    return out

def rsa_timings():
    t = time.perf_counter(); priv, pub = rsa_generate(2048); gen = (time.perf_counter() - t) * 1000
    s = sign("benchmark", priv)
    return {"RSA keygen": gen, "RSA sign": _ms(lambda: sign("benchmark", priv), 3), "RSA verify": _ms(lambda: verify("benchmark", s, pub), 3)}
