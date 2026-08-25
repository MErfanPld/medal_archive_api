#!/usr/bin/env python3
"""Install tasbih module. Run from project root: python scripts/install_tasbih.py"""
import base64, gzip, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
B64 = (HERE/"tasbih_payload_a.txt").read_text().strip() + (HERE/"tasbih_payload_b.txt").read_text().strip()
def main():
    root = Path.cwd()
    if not (root/"manage.py").exists():
        print("Run from project root"); return 1
    data = json.loads(gzip.decompress(base64.b64decode(B64)).decode())
    for rel, content in data.items():
        path = root/rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print("wrote", rel)
    print("OK", len(data), "files for tasbih")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
