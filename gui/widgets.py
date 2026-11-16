"""Small styled widgets that match the design (cards, caps labels, buttons, inputs)."""
import tkinter as tk
from . import theme as T, anim

def card(parent, border=T.BORDER):
    return tk.Frame(parent, bg=T.PANEL, highlightthickness=1, highlightbackground=border, highlightcolor=border, padx=18, pady=16)

def caps(parent, text, color=T.MUTED):
    return tk.Label(parent, text=text.upper(), bg=T.PANEL, fg=color, font=(T.FONT, 8, "bold"), anchor="w")

class Btn(tk.Label):
    """Button with hover glow, press-darken and release animation."""
    def __init__(self, parent, text, command, primary=False, color=T.ACC, **kw):
        self.cmd, self.rest = command, color if primary else T.PANEL
        self.hov = anim.mix(color, "#FFFFFF", .22) if primary else T.SEL
        self.pressed = anim.mix(color, "#000000", .3) if primary else anim.mix(T.SEL, color, .35)
        super().__init__(parent, text=text, bg=self.rest, fg=T.BG if primary else color, font=(T.FONT, 10, "bold"),
                         padx=18, pady=10, cursor="hand2", highlightthickness=1, highlightbackground=color, **kw)
        self.bind("<Enter>", lambda e: anim.fade(self, 130, bg=self.hov))
        self.bind("<Leave>", lambda e: anim.fade(self, 200, bg=self.rest))
        self.bind("<ButtonPress-1>", lambda e: anim.fade(self, 70, bg=self.pressed))
        self.bind("<ButtonRelease-1>", self._release)
    def _release(self, e):
        inside = 0 <= e.x < self.winfo_width() and 0 <= e.y < self.winfo_height()
        anim.fade(self, 220, bg=self.hov if inside else self.rest)
        if inside: self.after(40, self.cmd)      # small delay so the press animation is visible first

_BOX = dict(bg=T.BG, fg=T.FG, insertbackground=T.FG, relief="flat", highlightthickness=1,
            highlightbackground=T.BORDER, highlightcolor=T.ACC, font=(T.MONO, 11))

def textbox(parent, height):
    return tk.Text(parent, height=height, padx=10, pady=8, wrap="char", **_BOX)

def entry(parent, var, show=None):
    return tk.Entry(parent, textvariable=var, show=show or "", **_BOX)
