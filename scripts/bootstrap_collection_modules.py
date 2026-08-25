#!/usr/bin/env python3
"""Bootstrap all collection modules into the Django project root."""
from __future__ import annotations
import base64, gzip, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTS = HERE / "collection_bundle"

def main() -> int:
    root = Path.cwd()
    if not (root / "manage.py").exists():
        print("ERROR: run from project root (where manage.py is).")
        return 1
    parts = sorted(PARTS.glob("p*.txt"))
    if not parts:
        print("ERROR: missing scripts/collection_bundle/p*.txt")
        return 1
    b64 = "".join(p.read_text().strip() for p in parts)
    data = json.loads(gzip.decompress(base64.b64decode(b64)).decode("utf-8"))
    written = 0
    for app, files in data["apps"].items():
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written += 1
            print("  write", rel)
    for rel, content in data.get("extra", {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written += 1
        print("  write", rel)
    print(f"Done. {written} files written.")
    print("Next:")
    print("  python manage.py migrate")
    print("  python manage.py check")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
