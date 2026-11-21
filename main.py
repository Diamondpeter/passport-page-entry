#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Writes one image -- an invented passport spread for the Republic of
Aldermere, a North Atlantic island nation that does not exist -- to
/output/entry.png.

The spread ships in this repository as the binary asset
assets/spread.png: a photographic portrait composited with a fully
drawn data page (personal data and a valid ICAO machine-readable
zone, issue 02 FEB 2024, expiry 01 FEB 2034) and a visa page whose
stamps tell one plausible travel history -- Bergen, Torshavn,
Reykjavik, and home to Skardvik -- plus the one telling detail of
paperwork: Condition 7, the holder must declare all wool and down on
arrival. It was composed in this repository's first build session
(see draw_passport.py).

This program checks the asset against the gate (a whole PNG, at most
1 MiB, at most 1024x1024) and writes it out byte for byte. Standard
library only, no network.
"""
import os
import struct
import sys

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def load_spread():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "assets", "spread.png")
    with open(path, "rb") as fh:
        return fh.read()


def check(data):
    if len(data) > MAX_BYTES:
        raise ValueError("spread is over the 1 MiB gate")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("spread is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("spread is over the 1024x1024 gate")
    return width, height


def write_out(data):
    """Write to /output/entry.png, falling back to ./output if needed.

    The written file is read back and compared byte for byte with the
    asset, so a short or corrupted write fails loudly instead of
    quietly entering a broken image.
    """
    try:
        os.makedirs("/output", exist_ok=True)
        target = "/output/entry.png"
    except OSError:
        os.makedirs("output", exist_ok=True)
        target = os.path.join("output", "entry.png")
    with open(target, "wb") as fh:
        fh.write(data)
    with open(target, "rb") as fh:
        if fh.read() != data:
            raise ValueError("written file does not match the asset")
    return target


def main():
    data = load_spread()
    if not data:
        raise ValueError("spread asset is empty")
    width, height = check(data)
    target = write_out(data)
    print(f"wrote {target}: {len(data)} bytes, {width}x{height}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
