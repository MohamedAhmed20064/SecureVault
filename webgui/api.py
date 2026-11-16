"""Python <-> JavaScript bridge. Every PUBLIC method can be called from the web UI (names starting with _ are hidden)."""
import base64, os, tempfile, time
import crypto as c
import ai


def _r(fn):
    """Wrap a method: returns {"ok": True, "ms": ..., ...result} or {"ok": False, "error": "..."}."""
    def w(*a, **k):
        t = time.perf_counter()
        try:
            res = fn(*a, **k)
            res = res if isinstance(res, dict) else {"out": res}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True, "ms": round((time.perf_counter() - t) * 1000, 1), **res}
    w.__name__ = fn.__name__
    return w


class Api:
    def __init__(self):
        self._k = {"priv": None, "pub": None}
        self._window = None

    # ---- helpers (hidden from JS) ----
    def _keys(self):
        if not self._k["priv"]:
            self._k["priv"], self._k["pub"] = c.rsa_generate(2048)
        return self._k["priv"], self._k["pub"]

    # ---- keys ----
    def keys_ready(self): return bool(self._k["priv"])

    @_r
    def gen_keys(self):
        self._k["priv"], self._k["pub"] = c.rsa_generate(2048)
        return {"ready": True}

    @_r
    def public_pem(self):
        priv, pub = self._keys()
        return {"pem": c.rsa_export(priv, pub)[1]}

    @_r
    def save_public_key(self):
        priv, pub = self._keys()
        path = self._window.create_file_dialog(_dialog("SAVE"), save_filename="public_key.pem")
        if not path: raise ValueError("Cancelled")
        path = path if isinstance(path, str) else path[0]
        open(path, "w").write(c.rsa_export(priv, pub)[1])
        return {"path": path}

    # ---- AI ----
    def scan(self, text):
        if not text.strip(): return {"ok": True, "findings": [], "risk": 0, "rec": None}
        r = ai.recommend(text)
        return {"ok": True, "risk": r["risk"], "findings": [{"name": f[0], "value": f[1], "sev": f[2]} for f in r["findings"]],
                "rec": {"algorithm": r["algorithm"], "reason": r["reason"], "type": r["data_type"]}}

    def mask(self, text): return {"ok": True, "text": ai.mask(text)}

    @_r
    def password_strength(self, pw): return ai.password_strength(pw)

    _rep = {}   # evaluation is slow-ish, so it is computed once

    @_r
    def ai_report(self):
        if "r" not in self._rep:
            from ai import evaluate
            self._rep["r"] = evaluate.report()
        return {"report": self._rep["r"]}

    # ---- text crypto ----
    @_r
    def crypt(self, algo, mode, text, key):
        d = mode == "decrypt"
        if algo == "Caesar Cipher":
            try: shift = int(key)
            except ValueError: raise ValueError("Caesar shift must be a whole number")
            return c.caesar(text, shift, d)
        if algo == "Vigenère Cipher": return c.vigenere(text, key, d)
        if algo == "AES-256-GCM": return c.aes_decrypt(text, key) if d else c.aes_encrypt(text, key)
        if algo == "RSA-2048":
            priv, pub = self._keys()
            return c.rsa_decrypt(text, priv) if d else c.rsa_encrypt(text, pub)
        raise ValueError("Use the Hash button for SHA-256" if algo == "SHA-256 Hash" else "Pick an algorithm from the sidebar")

    @_r
    def hash(self, text): return c.sha256(text)
    @_r
    def brute_force(self, text):
        return {"results": c.classical.caesar_brute_force(text)}
    @_r
    def freq_analysis(self, text):
        return {"top": c.classical.frequency_analysis(text)}

    @_r
    def avalanche(self, t1, t2):
        return c.hashing.avalanche_test(t1, t2)

    @_r
    def sign(self, text): return c.sign(text, self._keys()[0])

    @_r
    def verify(self, text, sig):
        if not self._k["pub"]: raise ValueError("Generate RSA keys first (sidebar)")
        return {"valid": c.verify(text, sig, self._k["pub"])}

    @_r
    def run_tests(self, msg):
        priv, pub = self._keys(); sig = c.sign(msg, priv)
        ok = c.verify(msg, sig, pub)
        t1 = {"state": "ok" if ok else "bad", "title": "Signature valid" if ok else "Unexpected failure", "desc": "Hashes match: integrity and sender confirmed."}
        bad = msg.replace("500", "5000", 1) if "500" in msg else msg + "!"
        r = c.verify(bad, sig, pub)
        t2 = {"state": "bad" if not r else "warn", "title": "Signature invalid" if not r else "Tamper NOT detected",
              "desc": f"“{msg}” → “{bad}”. SHA-256 digests differ: {c.sha256(msg)[:10]}… vs {c.sha256(bad)[:10]}…"}
        token = c.aes_encrypt(msg, "correct-password")
        try:
            c.aes_decrypt(token, "wrong-password"); t3 = {"state": "warn", "title": "Unexpected success", "desc": "Wrong password should fail."}
        except ValueError:
            t3 = {"state": "warn", "title": "Decryption failed", "desc": "Authentication tag mismatch. No partial output shown."}
        return {"sig": sig, "tests": [t1, t2, t3]}

    # ---- hybrid ----
    @_r
    def hybrid(self, mode, text):
        priv, pub = self._keys()
        return c.hybrid_decrypt(text, priv) if mode == "decrypt" else c.hybrid_encrypt(text, pub)

    # ---- files ----
    def choose_file(self):
        try:
            r = self._window.create_file_dialog(_dialog("OPEN"))
            if not r: return {"ok": False, "error": "Cancelled"}
            p = r[0]; data = open(p, "rb").read()
            return {"ok": True, "path": p, "name": os.path.basename(p), "size": len(data), "sha256": c.sha256(data)}
        except Exception as e: return {"ok": False, "error": str(e)}

    @_r
    def file_op(self, op, path, password):
        if op == "encrypt": out = path + ".svlt"; c.encrypt_file(path, out, password)
        else:
            base, ext = os.path.splitext(path)
            if ext != ".svlt": raise ValueError("Choose a .svlt file to decrypt")
            out = base if not os.path.exists(base) else base + ".decrypted" + os.path.splitext(base)[1]
            c.decrypt_file(path, out, password)
        return {"path": out, "sha256": c.sha256(open(out, "rb").read())}

    @_r
    def file_op_b64(self, op, name, b64, password):
        """Browser mode: file comes in as base64, result goes back as base64 (no disk paths)."""
        d = tempfile.mkdtemp(); name = os.path.basename(name) or "file"; src = os.path.join(d, name)
        open(src, "wb").write(base64.b64decode(b64))
        if op == "encrypt": out = src + ".svlt"; c.encrypt_file(src, out, password); oname = name + ".svlt"
        else:
            if not name.endswith(".svlt"): raise ValueError("Choose a .svlt file to decrypt")
            oname = name[:-5]; out = os.path.join(d, "dec_" + oname); c.decrypt_file(src, out, password)
        data = open(out, "rb").read()
        return {"name": oname, "b64": base64.b64encode(data).decode(), "sha256": c.sha256(data), "size": len(data)}

    # ---- performance ----
    @_r
    def benchmark(self):
        res = c.benchmark.run()
        return {"sizes": {str(k): v for k, v in res.items()}, "rsa": c.benchmark.rsa_timings()}


def _dialog(kind):
    import webview
    fd = getattr(webview, "FileDialog", None)
    return getattr(fd, kind) if fd else getattr(webview, kind + "_DIALOG")
