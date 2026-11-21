#!/usr/bin/env python3
"""Embed assets/spread.png into main.py's IMAGE_B64 placeholder.

Mechanical step only: the spread itself was composed by draw_passport.py
in this session; this just carries its bytes into the entrypoint so the
program is self-contained in the no-network sandbox.
"""
import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPREAD = ROOT / "assets" / "spread.png"
MAIN = ROOT / "main.py"

raw = SPREAD.read_bytes()
b64 = base64.b64encode(raw).decode("ascii")
text = MAIN.read_text()
new, n = re.subn(r'IMAGE_B64 = ""',
                 'IMAGE_B64 = (\n    "' + '"\n    "'.join(
                     b64[i:i + 76] for i in range(0, len(b64), 76)) + '"\n)',
                 text, count=1)
if n != 1:
    sys.exit("placeholder IMAGE_B64 = \"\" not found exactly once")
MAIN.write_text(new)
print("embedded %d bytes as %d base64 chars into main.py" % (len(raw), len(b64)))
