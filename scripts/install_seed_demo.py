#!/usr/bin/env python3
"""Write scripts/seed_demo_all.py from embedded payload. Run from repo root."""
import base64, gzip
from pathlib import Path
B64 = open(Path(__file__).resolve().parent / 'seed_demo_payload.txt').read().strip()
out = Path(__file__).resolve().parent / 'seed_demo_all.py'
out.write_bytes(gzip.decompress(base64.b64decode(B64)))
print('wrote', out, 'bytes', out.stat().st_size)
