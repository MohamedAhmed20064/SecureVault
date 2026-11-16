"""Main window: sidebar (algorithms + RSA keys) and two screens (Vault, Verify)."""
import tkinter as tk
from tkinter import filedialog, messagebox
import crypto as c
from . import theme as T
from . import anim
from .widgets import Btn
from .vault_page import VaultPage
from .verify_page import VerifyPage
from .file_page import FilePage
from .hybrid_page import HybridPage
from .perf_page import PerfPage

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("SecureVault"); self.geometry("1280x800"); self.minsize(1100, 720); self.configure(bg=T.BG)
        self.priv = self.pub = None; self.signature = ""; self.algo = "AES-256-GCM"
        self.side = tk.Frame(self, bg=T.SIDEBAR, width=240, highlightthickness=1, highlightbackground=T.BORDER)
        self.side.pack(side="left", fill="y"); self.side.pack_propagate(False)
        logo = tk.Frame(self.side, bg=T.SIDEBAR); logo.pack(anchor="w", padx=24, pady=(26, 22))
        tk.Label(logo, text="Secure", bg=T.SIDEBAR, fg=T.FG, font=(T.FONT, 18, "bold")).pack(side="left")
        tk.Label(logo, text="Vault", bg=T.SIDEBAR, fg=T.ACC, font=(T.FONT, 18, "bold")).pack(side="left")
        tk.Label(self.side, text="ALGORITHMS", bg=T.SIDEBAR, fg=T.MUTED, font=(T.FONT, 8, "bold")).pack(anchor="w", padx=30, pady=(0, 6))
        self.items = {}
        for a in T.ALGOS + [None] + T.EXTRAS:
            if a is None:
                tk.Label(self.side, text="MORE TOOLS", bg=T.SIDEBAR, fg=T.MUTED, font=(T.FONT, 8, "bold")).pack(anchor="w", padx=30, pady=(14, 6)); continue
            lb = tk.Label(self.side, text=a, bg=T.SIDEBAR, fg=T.FG, font=(T.FONT, 10), anchor="w", padx=14, pady=11,
                          cursor="hand2", highlightthickness=1, highlightbackground=T.SIDEBAR)
            lb.pack(fill="x", padx=16, pady=2); lb.bind("<Button-1>", lambda e, a=a: self.select(a)); self.items[a] = lb
            lb.bind("<Enter>", lambda e, a=a, l=lb: self.hover(l, a, True)); lb.bind("<Leave>", lambda e, a=a, l=lb: self.hover(l, a, False))
        bottom = tk.Frame(self.side, bg=T.SIDEBAR); bottom.pack(side="bottom", fill="x", padx=16, pady=20)
        self.keystate = tk.Label(bottom, text="No RSA keys yet", bg=T.SIDEBAR, fg=T.MUTED, font=(T.FONT, 9)); self.keystate.pack(anchor="w", pady=(0, 8))
        Btn(bottom, "Generate RSA keys", self.ensure_keys, color=T.ACC).pack(fill="x", pady=(0, 8))
        Btn(bottom, "Save public key…", self.save_pub, color=T.MUTED).pack(fill="x")
        body = tk.Frame(self, bg=T.BG); body.pack(side="left", fill="both", expand=True, padx=28, pady=28)
        self.vault, self.verify = VaultPage(body, self), VerifyPage(body, self)
        self.extra = {"File Vault": FilePage(body, self), "Hybrid AES + RSA": HybridPage(body, self), "Performance": PerfPage(body, self)}
        self.current = None
        for pg in (self.vault, self.verify, *self.extra.values()): anim.glow(pg)
        self.select(self.algo)

    def hover(self, lb, a, on):
        if a != self.algo: anim.fade(lb, 140, bg=anim.mix(T.SIDEBAR, T.SEL, .6) if on else T.SIDEBAR)

    def select(self, algo):
        self.algo = algo
        for a, lb in self.items.items():
            on = a == algo
            anim.fade(lb, 220, bg=T.SEL if on else T.SIDEBAR, highlightbackground=T.ACC if on else T.SIDEBAR)
        page = self.verify if algo == "Digital Signature" else self.extra.get(algo, self.vault)
        if page is self.vault: self.vault.set_algo(algo)
        if page is self.verify: self.verify.refresh()
        if page is not self.current:                       # slide the new screen in
            if self.current: self.current.place_forget()
            self.current = page; anim.slide_in(page)

    def ensure_keys(self):
        if not self.priv:
            self.priv, self.pub = c.rsa_generate(2048); self.keystate.config(text="RSA-2048 keys ready", fg=T.ACC)

    def save_pub(self):
        if not self.pub: return messagebox.showwarning("RSA", "Generate RSA keys first")
        p = filedialog.asksaveasfilename(defaultextension=".pem")
        if p: open(p, "w").write(c.rsa_export(self.priv, self.pub)[1])
