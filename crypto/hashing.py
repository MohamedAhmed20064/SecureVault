"""SHA-256 hashing."""
import hashlib

def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()
def avalanche_test(text1, text2):
    h1, h2 = sha256(text1), sha256(text2)
    b1, b2 = bin(int(h1, 16))[2:].zfill(256), bin(int(h2, 16))[2:].zfill(256)
    diff = sum(c1 != c2 for c1, c2 in zip(b1, b2))
    return {"hash1": h1, "hash2": h2, "diff_bits": diff, "percent": round((diff / 256) * 100, 1)}
