from __future__ import annotations

import fcntl
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .allowlist import validate_request
from .runner import run_curve
from . import __version__

LOCK_PATH = os.environ.get("HOST_YARN_LOCK", "/tmp/host-yarn-bridge.lock")
BIND = os.environ.get("HOST_YARN_BIND", "0.0.0.0")
PORT = int(os.environ.get("HOST_YARN_PORT", "8099"))


class OneRunLock:
    def __init__(self, path: str):
        self.path = path
        self.fd = None

    def acquire(self) -> bool:
        self.fd = open(self.path, "w")
        try:
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.fd.write(str(os.getpid()))
            self.fd.flush()
            return True
        except BlockingIOError:
            try:
                self.fd.close()
            except Exception:
                pass
            self.fd = None
            return False

    def release(self):
        if self.fd is not None:
            try:
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
            finally:
                self.fd.close()
                self.fd = None


RUN_LOCK = OneRunLock(LOCK_PATH)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _json(self, code: int, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ("/healthz", "/health"):
            return self._json(200, {"ok": True, "version": __version__})
        if self.path == "/version":
            return self._json(200, {"version": __version__})
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/run":
            return self._json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except Exception:
            return self._json(400, {"error": "invalid json"})
        try:
            timeout = validate_request(body)
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        if not RUN_LOCK.acquire():
            return self._json(409, {"error": "another run in progress"})
        try:
            result = run_curve(body["artifact_root"], timeout)
            code = 200 if result.get("succeeded") else 200  # worker wants JSON JobResult either way
            return self._json(code, result)
        except Exception as e:
            return self._json(500, {
                "job_name": "host-local-yarn-bridge",
                "succeeded": False,
                "exit_code": 1,
                "logs": f"bridge exception: {type(e).__name__}: {e}",
            })
        finally:
            RUN_LOCK.release()

    def log_message(self, fmt, *args):
        # keep stdout clean for systemd journal
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    httpd = ThreadingHTTPServer((BIND, PORT), Handler)
    print(f"host-yarn-bridge {__version__} listening on {BIND}:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
