"""Measure the AI models (for the report).   python -m ai.evaluate"""
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_score
from . import advisor, passwords as pw
from .dataset import TEST, TRAIN

def _metrics(y, p, labels):
    pr, rc, f1, _ = precision_recall_fscore_support(y, p, labels=labels, zero_division=0)
    return {"accuracy": round(float(accuracy_score(y, p)), 3), "labels": labels, "matrix": confusion_matrix(y, p, labels=labels).tolist(),
            "per_class": [{"label": l, "precision": round(float(a), 3), "recall": round(float(b), 3), "f1": round(float(c), 3)} for l, a, b, c in zip(labels, pr, rc, f1)]}

def advisor_report():
    labels = ["credentials", "financial", "personal", "short_secret", "public"]
    X, y = [t for _, t in TRAIN], [l for l, _ in TRAIN]; Xt, yt = [t for _, t in TEST], [l for l, _ in TEST]
    pred = advisor.build_model().fit(X, y).predict(Xt); r = _metrics(yt, pred, labels)
    r.update(train=len(TRAIN), test=len(TEST), cv_accuracy=round(float(cross_val_score(advisor.build_model(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()), 3),
             errors=[{"text": t, "expected": l, "got": str(g)} for (l, t), g in zip(TEST, pred) if l != g])
    return r

def password_report():
    labels = ["weak", "medium", "strong"]; Xs, ys = pw.make_dataset(7, 200)
    r = _metrics(ys, pw._MODEL.predict(Xs), labels)
    hand = [(p, l, pw.password_strength(p)["label"]) for p, l in pw.HAND_TEST]
    r.update(train=len(pw._y), test=len(ys), hand_accuracy=round(sum(l == g for _, l, g in hand) / len(hand), 3),
             errors=[{"text": p, "expected": l, "got": g} for p, l, g in hand if l != g])
    return r

def report(): return {"advisor": advisor_report(), "password": password_report()}

if __name__ == "__main__":
    for name, r in report().items():
        print(f"\n== {name} ==  accuracy on unseen data: {r['accuracy']:.1%}  (train {r['train']}, test {r['test']})")
        if "cv_accuracy" in r: print(f"   5-fold cross-validation on training data: {r['cv_accuracy']:.1%}")
        if "hand_accuracy" in r: print(f"   hand-written passwords: {r['hand_accuracy']:.1%}")
        for c in r["per_class"]: print(f"   {c['label']:<13} precision {c['precision']:.2f}  recall {c['recall']:.2f}  f1 {c['f1']:.2f}")
        print("   confusion matrix (rows = real, columns = predicted):", r["labels"])
        for lab, row in zip(r["labels"], r["matrix"]): print(f"   {lab:<13}", row)
        for e in r["errors"]: print("   MISS:", e)
