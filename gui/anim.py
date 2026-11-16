"""Tiny animation toolkit for Tkinter: colour fades, slide-ins, count-ups, hover glow (60 fps via after())."""
import tkinter as tk
from . import theme as T

def _hex(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
def _ok(c): return isinstance(c, str) and len(c) == 7 and c[0] == "#"
def mix(a, b, t): return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(_hex(a), _hex(b)))
def ease(t): return 1 - (1 - t) ** 3                       # ease-out: fast start, soft landing

def tween(w, ms, fn, done=None, key="t"):
    """Call fn(progress 0..1) every ~16 ms. A new tween with the same key cancels the old one."""
    ids = w.__dict__.setdefault("_tw", {})
    if key in ids:
        try: w.after_cancel(ids[key])
        except tk.TclError: pass
    steps, n = max(1, ms // 16), [0]
    def step():
        n[0] += 1
        try:
            fn(ease(n[0] / steps))
            if n[0] < steps: ids[key] = w.after(16, step)
            else:
                ids.pop(key, None)
                if done: done()
        except tk.TclError: pass                            # widget was destroyed mid-animation
    ids[key] = w.after(16, step)

def fade(w, ms=160, done=None, **targets):
    """Smoothly change colour options, e.g. fade(lbl, 200, fg="#fff", bg="#000")."""
    try: starts = {k: w.cget(k) for k in targets}
    except tk.TclError: return
    if not all(_ok(s) for s in starts.values()):
        try: w.configure(**targets)
        except tk.TclError: pass
        return
    tween(w, ms, lambda t: w.configure(**{k: mix(starts[k], v, t) for k, v in targets.items()}), done, key="fade")

def cards(root):
    out = []
    for w in root.winfo_children():
        if isinstance(w, tk.Frame) and str(w.cget("bg")).lower() == T.PANEL.lower() and int(w.cget("highlightthickness")) == 1: out.append(w)
        out += cards(w)
    return out

def _inside(w, card):
    while w is not None:
        if w is card: return True
        w = getattr(w, "master", None)
    return False

def glow(page):
    """Cards light up their border when the mouse is over them."""
    for card in cards(page):
        card._hot, card._base = False, card.cget("highlightbackground")
        def enter(e, c=card):
            if not c._hot: c._base, c._hot = c.cget("highlightbackground"), True
            g = mix(c._base, "#FFFFFF", .35); fade(c, 140, highlightbackground=g, highlightcolor=g)
        def check(c):
            try: w = c.winfo_containing(*c.winfo_pointerxy())
            except (tk.TclError, KeyError): w = None
            if c._hot and not _inside(w, c): c._hot = False; fade(c, 240, highlightbackground=c._base, highlightcolor=c._base)
        def leave(e, c=card): c.after(25, lambda: check(c))
        def bind_all(w):
            w.bind("<Enter>", enter, add="+"); w.bind("<Leave>", leave, add="+")
            for ch in w.winfo_children(): bind_all(ch)
        bind_all(card)

def reveal(page):
    """Cards appear one after another (border fades in)."""
    for i, card in enumerate(cards(page)):
        base = card._base if getattr(card, "_hot", False) else card.cget("highlightbackground")
        card.config(highlightbackground=T.BG, highlightcolor=T.BG)
        card.after(i * 70, lambda c=card, b=base: fade(c, 320, highlightbackground=b, highlightcolor=b))

def slide_in(page, dy=26):
    page.place(x=0, y=dy, relwidth=1, relheight=1)
    tween(page, 260, lambda t: page.place_configure(y=round(dy * (1 - t))), key="slide")
    reveal(page)
