#!/usr/bin/env python3
"""Bootstrap: reconstruct and install all 7 collection modules.
Run from project root:
  python scripts/bootstrap_collection_modules.py
"""
from __future__ import annotations
import base64, gzip, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHUNKS = [
    open(HERE / "payload_chunk_0.txt").read().strip(),
    open(HERE / "payload_chunk_1.txt").read().strip(),
    open(HERE / "payload_chunk_2.txt").read().strip(),
    open(HERE / "payload_chunk_3.txt").read().strip(),
    open(HERE / "payload_chunk_4.txt").read().strip(),
    open(HERE / "payload_chunk_5.txt").read().strip(),
    open(HERE / "payload_chunk_6.txt").read().strip(),
    open(HERE / "payload_chunk_7.txt").read().strip(),
]

def main():
    root = Path.cwd()
    if not (root / "manage.py").exists():
        print("ERROR: run from project root (where manage.py is)")
        return 1
    b64 = "".join(CHUNKS)
    data = json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf-8"))
    for rel, content in sorted(data.items()):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print("wrote", rel)
    print(f"\nOK — {len(data)} files installed.")
    print("Next:")
    print("  python manage.py migrate")
    print("  python manage.py check")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
