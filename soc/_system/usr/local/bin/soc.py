#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.request import urlopen

BASE = Path("/home/ubuntu/web-lab")
EVENTS = BASE / "events.log"
ALERTS = BASE / "alerts.log"
URL = "http://172.29.110.20:8080/events"

def collect():
    with urlopen(URL, timeout=8) as response:
        records = json.load(response)["events"]

    with EVENTS.open("w") as f:
        for event in records:
            f.write(json.dumps(event) + "\n")

    print(f"SOC_COLLECT_OK: {len(records)} events")

def detect():
    if not EVENTS.exists():
        sys.exit("ERROR: RUN_COLLECT_FIRST")

    count = 0

    for line in EVENTS.read_text().splitlines():
        event = json.loads(line)
        user = event.get("username", "")

        if (event.get("outcome") == "VULN_BYPASS"
                and event.get("source_ip") == "172.29.110.10"
                and "'" in user and "--" in user):

            alert = {
                "event": "SQLI_DETECTED",
                "source_ip": event["source_ip"],
                "username": user
            }

            with ALERTS.open("a") as f:
                f.write(json.dumps(alert) + "\n")

            print(json.dumps(alert))
            count += 1

    print(f"SOC_DETECTION_OK: {count} alerts")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: soc.py collect|detect")

    if sys.argv[1] == "collect":
        collect()
    elif sys.argv[1] == "detect":
        detect()
    else:
        sys.exit("UNKNOWN_MODE")
