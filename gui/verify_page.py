"""Screen 2 - Verify & Tamper Test: signature check + three real test cases."""
import tkinter as tk
import crypto as c
from . import theme as T, anim
from .widgets import card, caps, Btn, textbox, entry

class ResultCard:
    def __init__(self, parent, title):
        self.card = card(parent); self.title = caps(self.card, title); self.title.pack(fill="x", pady=(0, 8))
        self.big = tk.Label(self.card, text="Not run yet", bg=T.PANEL, fg=T.MUTED, font=(T.FONT, 17, "bold"), anchor="w"); self.big.pack(fill="x")
        self.desc = tk.Label(self.card, text="Press “Run all tests”.", bg=T.PANEL, fg="#C5D2E0", font=(T.FONT, 10),
                             wraplength=400, justify="left", anchor="w"); self.desc.pack(fill="x", pady=(6, 0))
    def set(self, color, big, desc):
        self.card._base = color
        anim.fade(self.card, 350, highlightbackground=color, highlightcolor=color)
        self.title.config(fg=T.MUTED); self.big.config(text=big, fg=T.MUTED); self.desc.config(text=desc)
        anim.fade(self.title, 350, fg=color); anim.fade(self.big, 450, fg=color)

class VerifyPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG)
        self.app = app
        for i in (0, 1): self.columnconfigure(i, weight=1, uniform="v")
        left = card(self); left.grid(row=0, column=0, sticky="new", padx=(0, 10), pady=(0, 20))
        caps(left, "Received message").pack(fill="x", pady=(0, 8))
        self.msg = textbox(left, 3); self.msg.pack(fill="x"); self.msg.insert("1.0", "Transfer 500 EGP to account 1234")
        caps(left, "Signature (RSA + SHA-256)").pack(fill="x", pady=(14, 8))
        self.sig = tk.StringVar(); entry(left, self.sig).pack(fill="x", ipady=6)
        row = tk.Frame(left, bg=T.PANEL); row.pack(fill="x", pady=(16, 0))
        Btn(row, "Verify", self.verify, primary=True).pack(side="left", padx=(0, 12))
        Btn(row, "Sign message", self.sign).pack(side="left", padx=(0, 12))
        Btn(row, "Run all tests", self.run_tests).pack(side="left")
        self.status = tk.Label(left, text="", bg=T.PANEL, fg=T.MUTED, font=(T.FONT, 10), anchor="w", wraplength=480, justify="left"); self.status.pack(fill="x", pady=(10, 0))
        self.t1 = ResultCard(self, "Test 1 · Original message"); self.t1.card.grid(row=0, column=1, sticky="new", padx=(10, 0), pady=(0, 20))
        self.t2 = ResultCard(self, "Test 2 · Message modified"); self.t2.card.grid(row=1, column=0, sticky="new", padx=(0, 10))
        self.t3 = ResultCard(self, "Test 3 · Wrong key"); self.t3.card.grid(row=1, column=1, sticky="new", padx=(10, 0))

    def refresh(self):
        if self.app.signature: self.sig.set(self.app.signature)
    def text(self): return self.msg.get("1.0", "end-1c")

    def _say(self, s, color):
        self.status.config(text=s, fg=T.FG); anim.fade(self.status, 400, fg=color)
    def sign(self):
        self.app.ensure_keys(); self.sig.set(c.sign(self.text(), self.app.priv)); self._say("Message signed with your RSA private key.", T.ACC)
    def verify(self):
        if not self.app.pub: return self._say("Generate RSA keys first (sidebar).", T.DANGER)
        ok = c.verify(self.text(), self.sig.get(), self.app.pub)
        self._say("Signature VALID - message is authentic." if ok else "Signature INVALID - message modified or wrong signature.", T.ACC if ok else T.DANGER)

    def run_tests(self):
        self.app.ensure_keys(); msg = self.text(); sig = c.sign(msg, self.app.priv); self.sig.set(sig)
        ok = c.verify(msg, sig, self.app.pub)
        r1 = (T.ACC if ok else T.DANGER, "Signature valid" if ok else "Unexpected failure", "Hashes match: integrity and sender confirmed.")
        bad = msg.replace("500", "5000", 1) if "500" in msg else msg + "!"
        r = c.verify(bad, sig, self.app.pub)
        r2 = (T.DANGER if not r else T.WARN, "Signature invalid" if not r else "Tamper NOT detected",
              f"“{msg}” → “{bad}”. SHA-256 digests differ: {c.sha256(msg)[:10]}… vs {c.sha256(bad)[:10]}…")
        token = c.aes_encrypt(msg, "correct-password")
        try: c.aes_decrypt(token, "wrong-password"); r3 = (T.WARN, "Unexpected success", "Wrong password should fail.")
        except ValueError: r3 = (T.WARN, "Decryption failed", "Authentication tag mismatch. No partial output shown.")
        for i, (card_, res) in enumerate(((self.t1, r1), (self.t2, r2), (self.t3, r3))):   # results appear one by one
            self.after(i * 220, lambda k=card_, v=res: k.set(*v))
