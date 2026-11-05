#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

BASE = Path("/home/ubuntu/web-lab")
DB = BASE / "users.db"
LOG = BASE / "access.log"
PATCH = BASE / "secure.flag"

BASE.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB) as db:
    db.execute("CREATE TABLE IF NOT EXISTS users "
               "(username TEXT PRIMARY KEY, password TEXT)")
    db.execute("INSERT OR IGNORE INTO users VALUES (?, ?)",
               ("admin", "Admin2026!"))
    db.execute("INSERT OR IGNORE INTO users VALUES (?, ?)",
               ("reader", "Reader2026!"))
    db.commit()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        url = urlsplit(self.path)

        if url.path == "/health":
            return self.send_json({"status": "WEB_READY"})

        if url.path == "/events":
            if self.client_address[0] != "172.29.110.30":
                return self.send_json({"error": "SOC_ONLY"}, 403)
            events = [json.loads(x) for x in LOG.read_text().splitlines()] \
                if LOG.exists() else []
            return self.send_json({"events": events})

        if url.path != "/login":
            return self.send_json({"error": "NOT_FOUND"}, 404)

        params = parse_qs(url.query)
        user = params.get("user", [""])[0]
        password = params.get("password", [""])[0]
        patched = PATCH.exists()

        try:
            with sqlite3.connect(DB) as db:
                if patched:
                    row = db.execute(
                        "SELECT username FROM users "
                        "WHERE username=? AND password=?",
                        (user, password)).fetchone()
                else:
                    sql = ("SELECT username FROM users "
                           "WHERE username='%s' AND password='%s'"
                           % (user, password))
                    row = db.execute(sql).fetchone()
        except sqlite3.Error:
            row = None

        if patched:
            outcome = "SAFE_LEGIT_OK" if row else "SAFE_BLOCKED"
        elif row and user == "reader" and password == "Reader2026!":
            outcome = "LEGIT_LOGIN_OK"
        elif row and row[0] == "admin" and password != "Admin2026!":
            outcome = "VULN_BYPASS"
        else:
            outcome = "VULN_REJECT"

        event = {
            "time": datetime.now(timezone.utc).isoformat(),
            "source_ip": self.client_address[0],
            "username": user,
            "outcome": outcome
        }
        with LOG.open("a") as f:
            f.write(json.dumps(event) + "\n")
        self.send_json({"outcome": outcome})

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
