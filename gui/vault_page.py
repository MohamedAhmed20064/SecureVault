"""Screen 1 - Vault: message, key, actions, output + AI Scanner and AI Crypto Advisor cards."""
import time, tkinter as tk
import crypto as c
import ai
from . import theme as T, anim
from .widgets import card, caps, Btn, textbox, entry

KEY_LABELS = {"Caesar Cipher": "Shift (number)", "Vigenère Cipher": "Key (letters only)", "AES-256-GCM": "Password",
              "RSA-2048": "Key (not needed - uses your RSA keys)", "SHA-256 Hash": "Key (not needed)"}

class VaultPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app, self.rec = app, None
        self.columnconfigure(0, weight=1); self.columnconfigure(1, minsize=330)
        left = tk.Frame(self, bg=T.BG); left.grid(row=0, column=0, sticky="new", padx=(0, 20))
        right = tk.Frame(self, bg=T.BG); right.grid(row=0, column=1, sticky="new")
        # Message
        m = card(left); m.pack(fill="x", pady=(0, 20)); caps(m, "Message").pack(fill="x", pady=(0, 8))
        self.msg = textbox(m, 5); self.msg.pack(fill="x")
        self.msg.insert("1.0", "Hi, my card is 4111 1111 1111 1111 and my ID is 29901011234567. Email me at ahmed@example.com")
        self.msg.bind("<KeyRelease>", lambda e: self.scan())
        # Key + buttons
        k = card(left); k.pack(fill="x", pady=(0, 20))
        self.keylbl = caps(k, "Key / Password"); self.keylbl.pack(fill="x", pady=(0, 8))
        self.key = tk.StringVar(); entry(k, self.key, show="•").pack(fill="x", ipady=6)
        row = tk.Frame(k, bg=T.PANEL); row.pack(fill="x", pady=(16, 0))
        for i, (t, f) in enumerate([("Encrypt", self.encrypt), ("Decrypt", self.decrypt), ("Hash", self.hash_), ("Sign", self.sign)]):
            Btn(row, t, f, primary=(i == 0)).pack(side="left", padx=(0, 12))
        # Output
        o = card(left); o.pack(fill="x"); caps(o, "Output (Base64)").pack(fill="x", pady=(0, 8))
        self.out = textbox(o, 4); self.out.pack(fill="x")
        self.status = tk.Label(o, text="Ready", bg=T.PANEL, fg=T.MUTED, font=(T.FONT, 9), anchor="w"); self.status.pack(fill="x", pady=(8, 0))
        # AI Scanner
        self.sc = card(right, T.WARN); self.sc.pack(fill="x", pady=(0, 20))
        self.sc_title = caps(self.sc, "AI Scanner · Risk 0%", T.WARN); self.sc_title.pack(fill="x", pady=(0, 10))
        self.sc_list = tk.Frame(self.sc, bg=T.PANEL); self.sc_list.pack(fill="x")
        Btn(self.sc, "Mask sensitive data", self.do_mask, color=T.WARN).pack(fill="x", pady=(14, 0))
        # AI Advisor
        a = card(right); a.pack(fill="x"); caps(a, "AI Crypto Advisor").pack(fill="x", pady=(0, 8))
        self.adv_alg = tk.Label(a, text="—", bg=T.PANEL, fg=T.ACC, font=(T.FONT, 15, "bold"), anchor="w"); self.adv_alg.pack(fill="x")
        self.adv_why = tk.Label(a, text="Type a message to get a recommendation.", bg=T.PANEL, fg="#C5D2E0", font=(T.FONT, 10),
                                wraplength=290, justify="left", anchor="w"); self.adv_why.pack(fill="x", pady=(8, 14))
        Btn(a, "Apply recommendation", self.apply_rec, primary=True).pack(fill="x")
        self.scan()

    def set_algo(self, a): self.keylbl.config(text=KEY_LABELS.get(a, "Key / Password").upper())
    def text(self): return self.msg.get("1.0", "end-1c")
    def out_text(self): return self.out.get("1.0", "end-1c").strip()
    def show(self, s):
        self.out.delete("1.0", "end"); self.out.insert("end", s)
        if s: self.out.config(fg=T.MUTED); anim.fade(self.out, 450, fg=T.FG)
    def say(self, s, ok=True):
        self.status.config(text=s, fg=T.FG); anim.fade(self.status, 400, fg=T.ACC if ok else T.DANGER)

    def _count(self, v):
        a = getattr(self, "_risk", 0)
        if a != v: anim.tween(self.sc_title, 450, lambda t: self.sc_title.config(text=f"AI SCANNER · RISK {round(a + (v - a) * t)}%"), key="count")
        self._risk = v

    def scan(self):
        t = self.text()
        for w in self.sc_list.winfo_children(): w.destroy()
        if not t.strip():
            self.rec, self._sig = None, None; self._count(0); self.adv_alg.config(text="—"); return
        self.rec = r = ai.recommend(t)
        sig = tuple((f[0], f[2]) for f in r["findings"]); changed = sig != getattr(self, "_sig", None); self._sig = sig
        if not r["findings"]:
            tk.Label(self.sc_list, text="No sensitive data detected", bg=T.PANEL, fg=T.ACC, font=(T.FONT, 10)).pack(anchor="w")
        for i, (name, val, sev, _) in enumerate(r["findings"]):
            row = tk.Frame(self.sc_list, bg=T.PANEL); row.pack(fill="x", pady=3)
            l1 = tk.Label(row, text=name + " · ", bg=T.PANEL, fg=T.FG, font=(T.FONT, 10)); l1.pack(side="left")
            col = T.DANGER if sev == "High" else T.WARN
            l2 = tk.Label(row, text=sev, bg=T.PANEL, fg=col, font=(T.FONT, 10, "bold")); l2.pack(side="left")
            if changed:                                    # new finding -> fades in, one after another
                for lbl, target in ((l1, T.FG), (l2, col)):
                    lbl.config(fg=T.PANEL); self.after(i * 90, lambda l=lbl, c_=target: anim.fade(l, 260, fg=c_))
        self._count(r["risk"])
        new = "Use " + r["algorithm"]
        if self.adv_alg.cget("text") != new: self.adv_alg.config(text=new, fg=T.MUTED); anim.fade(self.adv_alg, 350, fg=T.ACC)
        self.adv_why.config(text=r["reason"])

    def do_mask(self):
        self.msg.delete("1.0", "end"); self.msg.insert("1.0", ai.mask(self.text())); self.scan()
    def apply_rec(self):
        if self.rec: self.app.select("RSA-2048" if self.rec["algorithm"].startswith("RSA") else
                                     "SHA-256 Hash" if self.rec["algorithm"].startswith("SHA") else "AES-256-GCM")

    def run(self, fn, label):
        t0 = time.perf_counter()
        try: self.show(fn()); self.say(f"{label} OK · {(time.perf_counter() - t0) * 1000:.1f} ms")
        except Exception as e: self.show(""); self.say(str(e), False)
    def encrypt(self):
        a, t, k = self.app.algo, self.text(), self.key.get()
        if a == "Caesar Cipher": self.run(lambda: c.caesar(t, int(k)), "Encrypt")
        elif a == "Vigenère Cipher": self.run(lambda: c.vigenere(t, k), "Encrypt")
        elif a == "AES-256-GCM": self.run(lambda: c.aes_encrypt(t, k), "Encrypt")
        elif a == "RSA-2048": self.app.ensure_keys(); self.run(lambda: c.rsa_encrypt(t, self.app.pub), "Encrypt")
        else: self.say("Use Hash for SHA-256", False)
    def decrypt(self):
        a, t, k = self.app.algo, self.out_text() or self.text(), self.key.get()
        if a == "Caesar Cipher": self.run(lambda: c.caesar(t, int(k), True), "Decrypt")
        elif a == "Vigenère Cipher": self.run(lambda: c.vigenere(t, k, True), "Decrypt")
        elif a == "AES-256-GCM": self.run(lambda: c.aes_decrypt(t, k), "Decrypt")
        elif a == "RSA-2048": self.app.ensure_keys(); self.run(lambda: c.rsa_decrypt(t, self.app.priv), "Decrypt")
        else: self.say("A hash cannot be decrypted", False)
    def hash_(self): self.run(lambda: c.sha256(self.text()), "SHA-256")
    def sign(self):
        self.app.ensure_keys(); self.run(lambda: c.sign(self.text(), self.app.priv), "Sign")
        self.app.signature = self.out_text()
