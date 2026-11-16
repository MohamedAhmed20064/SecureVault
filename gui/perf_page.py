"""Extra screen: Performance - measured speed of each algorithm (log-scale bars)."""
import math, tkinter as tk
import crypto as c
from . import theme as T, anim
from .widgets import card, caps, Btn

COLORS = {"Caesar": T.WARN, "Vigenère": T.WARN, "AES-256-GCM": T.ACC, "SHA-256": "#7AA7FF"}
LABELS = {1024: "1 KB", 102_400: "100 KB", 1_048_576: "1 MB"}

class PerfPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=T.BG); self.app, self.res, self.size = app, None, 102_400
        top = card(self); top.pack(fill="x", pady=(0, 20)); caps(top, "Benchmark").pack(fill="x", pady=(0, 8))
        row = tk.Frame(top, bg=T.PANEL); row.pack(fill="x")
        Btn(row, "Run benchmark", self.run, primary=True).pack(side="left", padx=(0, 20))
        for n, t in LABELS.items(): Btn(row, t, lambda n=n: self.pick(n)).pack(side="left", padx=(0, 8))
        self.note = tk.Label(top, text="Press “Run benchmark” (takes a few seconds).", bg=T.PANEL, fg=T.MUTED, font=(T.FONT, 10), anchor="w", wraplength=900, justify="left"); self.note.pack(fill="x", pady=(12, 0))
        ch = card(self); ch.pack(fill="x", pady=(0, 20)); caps(ch, "Time to process the selected size (ms, log scale)").pack(fill="x", pady=(0, 8))
        self.cv = tk.Canvas(ch, bg=T.PANEL, height=190, highlightthickness=0); self.cv.pack(fill="x")
        rs = card(self); rs.pack(fill="x"); caps(rs, "RSA-2048 (single operation)").pack(fill="x", pady=(0, 8))
        self.rsa = tk.Label(rs, text="—", bg=T.PANEL, fg=T.FG, font=(T.MONO, 11), anchor="w"); self.rsa.pack(fill="x")

    def run(self):
        self.note.config(text="Running…", fg=T.WARN); self.update_idletasks()
        self.res = c.benchmark.run(); r = c.benchmark.rsa_timings()
        self.rsa.config(text="   ".join(f"{k}: {v:.2f} ms" for k, v in r.items())); self.pick(self.size)
    def pick(self, n):
        self.size = n
        if self.res: self.draw()
    def draw(self):
        d, cv = self.res[self.size], self.cv; W = max(cv.winfo_width(), 700); hi = math.log10(max(d.values())) + 3
        def frame(t):
            cv.delete("all")
            for i, (name, ms) in enumerate(d.items()):
                y = 12 + i * 44; tt = min(1, max(0, t * 1.5 - i * 0.15)); frac = max(0.02, (math.log10(max(ms, 0.001)) + 3) / hi) * tt
                cv.create_text(0, y + 14, text=name, fill=T.FG, anchor="w", font=(T.FONT, 10))
                cv.create_rectangle(120, y, 120 + max(2, frac * (W - 330)), y + 28, fill=COLORS[name], outline="")
                cv.create_text(130 + frac * (W - 330), y + 14, text=f"{ms:.3f} ms", fill=T.FG, anchor="w", font=(T.MONO, 10))
        anim.tween(cv, 800, frame, key="bars")
        aes, vig = d["AES-256-GCM"], d["Vigenère"]
        self.note.config(text=f"At {LABELS[self.size]}: AES-256-GCM is {vig / aes:.0f}× faster than our Vigenère and also far stronger. "
                              "(AES timing excludes the password-derivation step, which is intentionally slow to resist guessing.)", fg=T.ACC)
