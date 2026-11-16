"""AI feature 2: crypto advisor (TF-IDF + Logistic Regression classifies data type)."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from .detector import detect, risk_score

from .dataset import TRAIN as _DATA

def build_model():
    return make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)), LogisticRegression(max_iter=1000, C=10))

_MODEL = build_model().fit([t for _, t in _DATA], [l for l, _ in _DATA])

ADVICE = {
 "credentials": ("AES-256-GCM", "Credentials need strong authenticated encryption. Never use classical ciphers."),
 "financial": ("AES-256-GCM + Digital Signature", "Financial data needs confidentiality AND integrity/authenticity."),
 "personal": ("AES-256-GCM", "Personal data: strong symmetric encryption; share the key via RSA."),
 "short_secret": ("RSA-2048", "Short text (<190 bytes) can be sent directly with the receiver's public key."),
 "public": ("SHA-256 Hash", "Not sensitive: hash it to prove integrity, or sign it. (Caesar/Vigenère are for learning only.)"),
}

def recommend(text):
    findings = detect(text)
    label = _MODEL.predict([text])[0]
    if findings:
        kinds = {f[0] for f in findings}
        if kinds & {"Password / secret", "API key / token"}: label = "credentials"
        elif "Credit card number" in kinds: label = "financial"
        elif label in ("public", "short_secret"): label = "personal"
    alg, why = ADVICE[label]
    if len(text.encode()) > 190 and alg == "RSA-2048": alg, why = "AES-256-GCM", "Message is longer than RSA-2048 can handle; use AES."
    return {"data_type": label, "algorithm": alg, "reason": why, "risk": risk_score(findings), "findings": findings}
