"""Extra screen: Hybrid encryption (AES encrypts the message, RSA encrypts the AES key)."""
import time, tkinter as tk
import crypto as c
from . import theme as T
from .widgets import card, caps, Btn, textbox

STEPS = "1  A random AES-256 key is generated\n2  AES-GCM encrypts the message (any length)\n3  RSA-2048 encrypts only the AES key\n4  The receiver uses the RSA private key to recover the AES key, then decrypts"

class HybridPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG); self.app = app
        self.columnconfigure(0, weight=1); self.columnconfigure(1, minsize=330)
        left = tk.Frame(self, bg=T.BG); left.grid(row=0, column=0, sticky="new", padx=(0, 20))
        right = tk.Frame(self, bg=T.BG); right.grid(row=0, column=1, sticky="new")
        m = card(left); m.pack(fill="x", pady=(0, 20)); caps(m, "Message (any length)").pack(fill="x", pady=(0, 8))
        self.msg = textbox(m, 6); self.msg.pack(fill="x"); self.msg.insert("1.0", "Long message " * 40)
        row = tk.Frame(m, bg=T.PANEL); row.pack(fill="x", pady=(14, 0))
        Btn(row, "Hybrid encrypt", self.enc, primary=True).pack(side="left", padx=(0, 12)); Btn(row, "Hybrid decrypt", self.dec).pack(side="left")
        o = card(left); o.pack(fill="x"); caps(o, "Output (Base64 package: wrapped key + nonce + ciphertext)").pack(fill="x", pady=(0, 8))
        self.out = textbox(o, 6); self.out.pack(fill="x")
        self.status = tk.Label(o, text="Uses your RSA keys (created automatically).", bg=T.PANEL, fg=T.MUTED, font=(T.FONT, 9), anchor="w"); self.status.pack(fill="x", pady=(8, 0))
        h = card(right); h.pack(fill="x"); caps(h, "How it works").pack(fill="x", pady=(0, 8))
        tk.Label(h, text=STEPS, bg=T.PANEL, fg="#C5D2E0", font=(T.FONT, 10), justify="left", anchor="w", wraplength=290).pack(fill="x")
        w = card(right, T.ACC); w.pack(fill="x", pady=(20, 0)); caps(w, "Why", T.ACC).pack(fill="x", pady=(0, 8))
        tk.Label(w, text="RSA alone is limited to ~190 bytes and is slow. AES alone needs a shared password. Together you get speed, any size, and safe key exchange.",
                 bg=T.PANEL, fg="#C5D2E0", font=(T.FONT, 10), justify="left", anchor="w", wraplength=290).pack(fill="x")

    def say(self, s, ok=True): self.status.config(text=s, fg=T.ACC if ok else T.DANGER)
    def _run(self, fn, label, show):
        t0 = time.perf_counter()
        try:
            r = fn(); show(r); self.say(f"{label} OK · {(time.perf_counter() - t0) * 1000:.1f} ms")
        except Exception as e: self.say(str(e), False)
    def enc(self):
        self.app.ensure_keys()
        self._run(lambda: c.hybrid_encrypt(self.msg.get("1.0", "end-1c"), self.app.pub), "Encrypt", lambda r: (self.out.delete("1.0", "end"), self.out.insert("end", r)))
    def dec(self):
        self.app.ensure_keys()
        self._run(lambda: c.hybrid_decrypt(self.out.get("1.0", "end-1c"), self.app.priv), "Decrypt", lambda r: (self.msg.delete("1.0", "end"), self.msg.insert("end", r)))
