"""Classical ciphers: Caesar and Vigenère."""

def caesar(text, shift, decrypt=False):
    shift = int(shift) % 26
    if decrypt: shift = -shift
    out = []
    for c in text:
        if c.isalpha() and c.isascii():
            base = ord('A') if c.isupper() else ord('a')
            out.append(chr((ord(c) - base + shift) % 26 + base))
        else: out.append(c)
    return ''.join(out)

def vigenere(text, key, decrypt=False):
    k = [ord(c.lower()) - 97 for c in key if c.isalpha() and c.isascii()]
    if not k: raise ValueError("Vigenère key must contain letters A-Z")
    out, i = [], 0
    for c in text:
        if c.isalpha() and c.isascii():
            s = -k[i % len(k)] if decrypt else k[i % len(k)]
            base = ord('A') if c.isupper() else ord('a')
            out.append(chr((ord(c) - base + s) % 26 + base)); i += 1
        else: out.append(c)
    return ''.join(out)
def caesar_brute_force(ciphertext):
    return [{"shift": s, "text": caesar(ciphertext, s, decrypt=True)} for s in range(1, 26)]
def frequency_analysis(text):
    letters = [c.upper() for c in text if c.isalpha() and c.isascii()]
    total = len(letters)
    if not total: return []
    counts = {}
    for c in letters: counts[c] = counts.get(c, 0) + 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [{"char": k, "count": v, "percent": round((v / total) * 100, 1)} for k, v in top]
