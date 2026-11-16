"""Browser mode: serves web/ and the Api over localhost (no pywebview needed). Run: python main.py --browser"""
import json, mimetypes, os, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .api import Api

WEB = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "web"))


def make_server(port=0, api=None):
    api = api or Api()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _send(self, code, body, ctype):
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            p = self.path.split("?")[0]; f = os.path.normpath(os.path.join(WEB, ("index.html" if p == "/" else p.lstrip("/"))))
            if not f.startswith(WEB) or not os.path.isfile(f): return self._send(404, b"not found", "text/plain")
            self._send(200, open(f, "rb").read(), (mimetypes.guess_type(f)[0] or "application/octet-stream") + "; charset=utf-8")
        def do_POST(self):
            name = self.path.rsplit("/", 1)[-1]; fn = getattr(api, name, None)
            if self.headers.get("X-SV") != "1" or name.startswith("_") or not callable(fn): return self._send(403, b"forbidden", "text/plain")
            args = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"[]")
            try: res = fn(*args)
            except Exception as e: res = {"ok": False, "error": str(e)}
            self._send(200, json.dumps(res).encode(), "application/json")
    return ThreadingHTTPServer(("127.0.0.1", port), H)


def serve(port=0):
    srv = make_server(port); url = f"http://127.0.0.1:{srv.server_address[1]}/?b=1"
    print("SecureVault running at", url, "(Ctrl+C to stop)"); threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
