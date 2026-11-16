"""Extra screen: File Vault - encrypt/decrypt any file with AES-256-GCM."""
import os, time, tkinter as tk
from tkinter import filedialog
import crypto as c
from . import theme as T
from .widgets import card, caps, Btn, entry

class FilePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG); self.app, self.path = app, ""
        a = card(self); a.pack(fill="x", pady=(0, 20)); caps(a, "File").pack(fill="x", pady=(0, 8))
        self.name = tk.Label(a, text="No file selected", bg=T.PANEL, fg=T.FG, font=(T.FONT, 12, "bold"), anchor="w"); self.name.pack(fill="x")
        self.info = tk.Label(a, text="Supports any file: PDF, images, documents…", bg=T.PANEL, fg=T.MUTED, font=(T.MONO, 9), anchor="w", wraplength=760, justify="left"); self.info.pack(fill="x", pady=(4, 12))
        Btn(a, "Choose file…", self.choose).pack(anchor="w")
        b = card(self); b.pack(fill="x", pady=(0, 20)); caps(b, "Password").pack(fill="x", pady=(0, 8))
        self.pw = tk.StringVar(); entry(b, self.pw, show="•").pack(fill="x", ipady=6)
        row = tk.Frame(b, bg=T.PANEL); row.pack(fill="x", pady=(16, 0))
        Btn(row, "Encrypt file", self.enc, primary=True).pack(side="left", padx=(0, 12)); Btn(row, "Decrypt file", self.dec).pack(side="left")
        r = card(self); r.pack(fill="x"); caps(r, "Result").pack(fill="x", pady=(0, 8))
        self.status = tk.Label(r, text="Ready. Encrypted files get the .svlt extension.", bg=T.PANEL, fg=T.MUTED, font=(T.FONT, 10), anchor="w", wraplength=760, justify="left"); self.status.pack(fill="x")

    def say(self, s, ok=True): self.status.config(text=s, fg=T.ACC if ok else T.DANGER)
    def choose(self):
        p = filedialog.askopenfilename()
        if not p: return
        self.path = p; data = open(p, "rb").read()
        self.name.config(text=os.path.basename(p)); self.info.config(text=f"{len(data):,} bytes · SHA-256: {c.sha256(data)}")
    def _run(self, fn, label):
        if not self.path: return self.say("Choose a file first", False)
        t0 = time.perf_counter()
        try: out = fn(); self.say(f"{label} OK · {(time.perf_counter() - t0) * 1000:.0f} ms\nSaved: {out}\nSHA-256 of result: {c.sha256(open(out, 'rb').read())}")
        except Exception as e: self.say(str(e), False)
    def enc(self):
        def f(): out = self.path + ".svlt"; c.encrypt_file(self.path, out, self.pw.get()); return out
        self._run(f, "Encrypt")
    def dec(self):
        def f():
            base, ext = os.path.splitext(self.path)
            if ext != ".svlt": raise ValueError("Choose a .svlt file to decrypt")
            out = base if not os.path.exists(base) else base + ".decrypted" + os.path.splitext(base)[1]
            c.decrypt_file(self.path, out, self.pw.get()); return out
        self._run(f, "Decrypt")
