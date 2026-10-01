"""Minimal web app for the AI Text Summarizer demo (Python standard library only).

Run:  python app.py   then open http://127.0.0.1:8000
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from summarizer import summarize

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_BODY_BYTES = 100 * 1024
MAX_SENTENCES = 10


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (STATIC_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/healthz":
            self._json(200, {"status": "ok"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/summarize":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length <= 0 or length > MAX_BODY_BYTES:
            self._json(400, {"error": "body must be between 1 byte and %d bytes" % MAX_BODY_BYTES})
            return
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            text = str(data.get("text", "")).strip()
            sentences = max(1, min(MAX_SENTENCES, int(data.get("sentences", 3))))
        except (ValueError, AttributeError, TypeError, OverflowError):
            self._json(400, {"error": "expected JSON: {\"text\": \"...\", \"sentences\": 3}"})
            return
        if not text:
            self._json(400, {"error": "'text' is required"})
            return
        try:
            summary, mode = summarize(text, sentences)
        except Exception as exc:  # noqa: BLE001 - surface a safe message to the client
            self.log_error("summarization failed: %r", exc)
            self._json(502, {"error": "summarization failed; check server logs and configuration"})
            return
        self._json(200, {"summary": summary, "mode": mode})

    def _json(self, status, payload):
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print("AI Text Summarizer running on http://%s:%d" % (host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
