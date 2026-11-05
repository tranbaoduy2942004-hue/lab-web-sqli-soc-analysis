# Web SQL Injection Detection & Mitigation

Labtainer ID: lab-web-sqli-detection

## Topology
- attacker: 172.29.110.10
- web-server: 172.29.110.20 (HTTP 8080, SQLite)
- soc: 172.29.110.30

## Installation (Labtainer HOST)
imodule https://raw.githubusercontent.com/tranbaoduy2942004-hue/lab-web-sqli-detection/main/imodule.tar
labtainer lab-web-sqli-detection

## Practice

1. ATTACKER:
   python3 /usr/local/bin/sqli_client.py attack

2. SOC:
   python3 /usr/local/bin/soc.py collect
   python3 /usr/local/bin/soc.py detect

3. WEB-SERVER:
   python3 /usr/local/bin/remediate.py

4. ATTACKER:
   python3 /usr/local/bin/sqli_client.py verify

5. HOST:
   checkwork lab-web-sqli-detection

Expected result: 5/5 Y.

## Safety
Deliberately vulnerable application for authorized
local training only.
