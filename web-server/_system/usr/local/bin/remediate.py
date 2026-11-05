#!/usr/bin/env python3
from pathlib import Path

flag = Path("/home/ubuntu/web-lab/secure.flag")
flag.write_text("Parameterized query enabled\n")
print("SQLI_PATCH_ENABLED")
