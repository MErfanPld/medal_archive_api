#!/usr/bin/env python3
"""Install seed_all_collection_modules.py — run from project root:\n  python scripts/install_seed_collection.py\n"""
import base64, gzip
from pathlib import Path
HERE = Path(__file__).resolve().parent
B64 = (HERE/"seed_collection_payload_a.txt").read_text().strip() + (HERE/"seed_collection_payload_b.txt").read_text().strip()
def main():
    root = Path.cwd()
    if not (root/"manage.py").exists():
        print("Run from project root"); return 1
    content = gzip.decompress(base64.b64decode(B64)).decode()
    path = root/"scripts"/"seed_all_collection_modules.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", path)
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
