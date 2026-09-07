#!/usr/bin/env python3
"""Expand scripts/seed_demo_all.py from payload A+B. Run from repo root:

  python scripts/install_seed_demo.py
  python scripts/seed_demo_all.py
"""
import base64
import gzip
from pathlib import Path

HERE = Path(__file__).resolve().parent
a = (HERE / "seed_demo_payload_a.txt").read_text(encoding="ascii").strip()
b = (HERE / "seed_demo_payload_b.txt").read_text(encoding="ascii").strip()
out = HERE / "seed_demo_all.py"
out.write_bytes(gzip.decompress(base64.b64decode(a + b)))
print("wrote", out, "bytes", out.stat().st_size)
