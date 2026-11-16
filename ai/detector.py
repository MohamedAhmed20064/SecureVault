"""AI feature 1: sensitive-information detector (regex + Luhn + national-ID validation)."""
import re

def luhn(num):
    d = [int(c) for c in num][::-1]
    return (sum(d[0::2]) + sum(sum(divmod(x * 2, 10)) for x in d[1::2])) % 10 == 0

def valid_national_id(n):
    if not re.fullmatch(r"[23]\d{13}", n): return False
    mm, dd = int(n[3:5]), int(n[5:7])
    return 1 <= mm <= 12 and 1 <= dd <= 31

PATTERNS = [
    ("Email address", r"[\w.+-]+@[\w-]+\.[\w.-]+", "Medium"),
    ("Password / secret", r"(?i)(?:password|passwd|pwd|pass|باسورد|كلمة السر)\s*(?:is|=|:|هو)?\s*\S+", "High"),
    ("API key / token", r"\b(?:sk|pk|api|key|token)[-_][A-Za-z0-9_-]{12,}\b", "High"),
    ("Phone number", r"(?<!\d)(?:\+?20|0)1[0125]\d{8}(?!\d)", "Medium"),
]
WEIGHT = {"High": 40, "Medium": 20}

def detect(text):
    found = []
    for m in re.finditer(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", text):
        digits = re.sub(r"\D", "", m.group())
        if 13 <= len(digits) <= 19 and luhn(digits): found.append(("Credit card number", m.group().strip(), "High", m.span()))
    for m in re.finditer(r"(?<!\d)\d{14}(?!\d)", text):
        if valid_national_id(m.group()): found.append(("National ID", m.group(), "High", m.span()))
    for name, pat, sev in PATTERNS:
        for m in re.finditer(pat, text): found.append((name, m.group(), sev, m.span()))
    return found

def risk_score(findings):
    return min(100, sum(WEIGHT[f[2]] for f in findings))

def mask(text):
    for _, _, _, (a, b) in sorted(detect(text), key=lambda f: -f[3][0]):
        text = text[:a] + "█" * (b - a) + text[b:]
    return text
