"""Desktop window mode (pywebview): the web UI inside a native window."""
import os
from .api import Api

def run_webview():
    import webview
    api = Api()
    win = webview.create_window("SecureVault", os.path.join(os.path.dirname(__file__), "..", "web", "index.html"), js_api=api,
                                width=1320, height=840, min_size=(1100, 720), background_color="#070C14")
    api._window = win
    webview.start()
