"""Entry point.
  python main.py            -> desktop window (needs pywebview), falls back to browser mode
  python main.py --browser  -> opens the same UI in your browser
  python main.py --tk       -> old Tkinter interface
"""
import sys

def main():
    if "--tk" in sys.argv:
        from gui.main_window import App
        return App().mainloop()
    if "--browser" not in sys.argv:
        try:
            import webview  # noqa: F401
            from webgui.launcher import run_webview
            return run_webview()
        except ImportError:
            print("pywebview is not installed -> opening in your browser. (pip install pywebview for a desktop window)")
    from webgui.server import serve
    serve()

if __name__ == "__main__":
    main()
